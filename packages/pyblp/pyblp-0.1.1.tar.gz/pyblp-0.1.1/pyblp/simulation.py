"""Simulation of synthetic BLP problem data."""

import time

import numpy as np

from . import options, exceptions
from .construction import build_blp_instruments
from .primitives import Products, Agents, Market
from .utilities import output, extract_matrix, Matrices, ParallelItems, Iteration, Integration


class Simulation(object):
    r"""Simulation of synthetic BLP data.

    All data are simulated during initialization, except for Bertrand-Nash prices and shares, which are computed by
    :meth:`Simulation.solve`.

    Non-constant exogenous product characteristics in :math:`X_1`, :math:`X_2`, and :math:`X_3`, collectively denoted
    :math:`X`, along with any demographics, :math:`d`, are all drawn from the standard uniform distribution.

    Unobserved demand- and supply-side product characteristics, :math:`\xi` and :math:`\omega`, are drawn from a
    mean-zero bivariate normal distribution.

    After simulating exogenous product characteristics and constructing agent data according to an integration
    configuration, canonical instruments are computed. Specifically,

    .. math:: Z_D = [1, X, \mathrm{BLP}(X_D)] \quad\text{and}\quad Z_S = [1, X, \mathrm{BLP}(X_S)],

    in which :math:`X` are all non-constant exogenous product characteristics, :math:`\mathrm{BLP}(X_D)` are traditional
    BLP instruments constructed by :func:`build_blp_instruments` from all non-constant exogenous characteristics in
    :math:`X_1` and :math:`X_2`, and :math:`\mathrm{BLP}(X_S)` are constructed from all non-constant characteristics in
    :math:`X_3`.

    Parameters
    ----------
    id_data : `structured array-like`
        IDs that associate products with markets and firms. Each row corresponds to a product. The convenience function
        :func:`build_id_data` can be used to construct ID data from market, product, and firm counts. Fields:

            - **market_ids** : (`object`) - IDs that associate products with markets.

            - **firm_ids** : (`object`) - IDs that associate products with firms. Any columns after the first can be
              used in :meth:`Simulation.solve` to compute Bertrand-Nash prices and shares after changes, such as
              mergers. If there are multiple columns, this field can either be a matrix or it can be broken up into
              multiple one-dimensional fields with column index suffixes that start at zero. For example, if there are
              two columns, this field can be replaced with two one-dimensional fields: `firm_ids0` and `firm_ids1`.

    integration : `Integration`
        :class:`Integration` configuration for how to build nodes and weights for integration over agent utilities.
    gamma : `array-like`
        Configuration for values of supply-side linear parameters, :math:`\gamma`, and for which product characteristics
        are in :math:`X_3`. The first element of this vector corresponds to a constant column; if it is zero,
        :math:`X_3` will not have a constant column. The number of following elements determines the number of columns
        in the matrix of non-constant exogenous characteristics, :math:`X`.

        If an element is zero, its corresponding characteristic will not be in :math:`X_3`. Nonzeros constitute
        :math:`\gamma`.

    beta : `array-like`
        Configuration for values of demand-side linear parameters, :math:`\beta`, and for which product characteristics
        are in :math:`X_1`. This vector must have one more element than `gamma` because the first element corresponds to
        prices and hence cannot be zero and should probably be negative. Following elements correspond to the same
        characteristics (a constant column and columns in :math:`X`) as do the elements of `gamma`, but shifted over by
        one.

        If an element is zero, its corresponding characteristic will not be in :math:`X_1`. Nonzeros constitute
        :math:`\beta`.

    sigma : `array-like`
        Configuration for values of the Cholesky decomposition of the covariance matrix that measures agents' random
        taste distribution, :math:`\Sigma`, and for which product characteristics are in :math:`X_2`. This square matrix
        should have as many rows and columns as there are elements in `beta`, and the lower triangle must be all zeros.
        Rows and columns correspond to the same characteristics (prices, a constant column, and columns in :math:`X`) as
        do the elements of `beta`.

        If a diagonal element is zero, its corresponding characteristic will not be in :math:`X_2`. Rows and columns
        associated with nonzeros on the diagonal constitute :math:`\Sigma`.

    pi : `array-like, optional`
        Configuration for values of parameters that measures how agent tastes vary with demographics, :math:`\Pi`, and
        for the number of demographics, :math:`d`. This matrix must have as many rows as `sigma`, since they correspond
        to the same characteristics (prices, a constant column, and columns in :math:`X`) as do the rows of `sigma`.

        The number of columns with at least one nonzero element determines the number of demographic columns in
        :math:`d`, and these columns along with rows associated with nonzeros on the diagonal of `sigma` constitute
        :math:`\Pi`.

    xi_variance : `float, optional`
        Variance of the unobserved demand-side product characteristics, :math:`\xi`. The default value is ``1.0``.
    omega_variance : `float, optional`
        Variance of the unobserved supply-side product characteristics, :math:`\omega`. The default value is ``1.0``.
    correlation : `float, optional`
        Correlation between :math:`\xi` and :math:`\omega`. The default value is ``0.9``.
    linear_costs : `bool, optional`
        Whether to compute marginal costs, :math:`c`, according to a linear or a log-linear marginal cost specification.
        By default, a linear specification is used. That is, :math:`\tilde{c} = c` instead of
        :math:`\tilde{c} = \log c`.
    seed : `int, optional`
        Passed to :func:`numpy.random.seed` to seed the random number generator before data are simulated.

    Attributes
    ----------
    beta : `ndarray`
        Demand-side linear parameters, :math:`\beta`, which are the nonzeros from `beta` in :class:`Simulation`
        initialization.
    sigma : `ndarray`
        Cholesky decomposition of the covariance matrix that measures agents' random taste distribution, :math:`\Sigma`,
        which are the rows and columns from `sigma` in :class:`Simulation` initialization that are associated with
        nonzeros on the diagonal.
    pi : `ndarray`
        Parameters that measures how agent tastes vary with demographics, :math:`\Pi`, which are columns from `pi` in
        :class:`Simulation` with at least one nonzero, and rows from `pi` that are associated with nonzeros on the
        diagonal of `sigma`.
    gamma : `ndarray`
        Supply-side linear parameters, :math:`\gamma`, which are the nonzeros from `gamma` in :class:`Simulation`
        initialization.
    product_data : `recarray`
        Synthetic product data that were simulated during initialization, except for Bertrand-Nash prices and shares,
        which :meth:`Simulation.solve` computes.
    agent_data : `recarray`
        Synthetic agent data that were simulated during initialization.
    products : `Products`
        Restructured :attr:`Simulation.product_data`, which is an instance of :class:`primitives.Products`.
    agents : `Agents`
        Restructured :attr:`Simulation.agent_data`, which is an instance of :class:`primitives.Agents`.
    characteristics : `ndarray`
        Matrix of distinct columns of all exogenous product characteristics in :attr:`Simulation.product_data`.
    characteristic_indices : `list of tuple`
        List of tuples of the form `(linear_index, nonlinear_index, cost_index)`, which associate indices of
        :attr:`Simulation.characteristics` columns with their counterparts in the `linear_characteristics`,
        `nonlinear_characteristics`, and `cost_characteristics` fields of :attr:`Simulation.product_data`.
        Characteristics without counterparts will have indices that are `None`.
    xi : `ndarray`
        Unobserved demand-side product characteristics, :math:`\xi`, that were simulated during initialization.
    omega : `ndarray`
        Unobserved supply-side product characteristics, :math:`\omega`, that were simulated during initialization.
    costs : `ndarray`
        Marginal costs, :math:`c`, that were simulated during initialization.
    nonlinear_prices : `bool`
        Whether prices are a nonlinear characteristic in :math:`X_2` in addition to being a linear characteristic in
        :math:`X_1`.
    integration : `Integration`
        :class:`Integration` configuration for how nodes and weights for integration over agent utilities built during
        :class:`Simulation` initialization.
    linear_costs : `bool`
        Whether :attr:`Simulation.costs` were simulated according to a linear or a log-linear marginal cost
        specification during :class:`Simulation` initialization.
    N : `int`
        Number of products across all markets, :math:`N`.
    T : `int`
        Number of markets, :math:`T`.
    K1 : `int`
        Number of linear product characteristics, :math:`K_1`.
    K2 : `int`
        Number of nonlinear product characteristics, :math:`K_2`.
    K3 : `int`
        Number of cost product characteristics, :math:`K_3`.
    D : `int`
        Number of demographic variables, :math:`D`.
    MD : `int`
        Number of demand-side instruments, :math:`M_D`.
    MS : `int`
        Number of supply-side instruments, :math:`M_S`.

    Example
    -------
    The following code simulates a small amount of data with two markets, nonlinear prices, a nonlinear constant,
    a cost/linear characteristic, another cost characteristic, a demographic, and other agent data constructed
    according to a low level Gauss-Hermite product rule:

    .. ipython:: python

       simulation = pyblp.Simulation(
           id_data=pyblp.build_id_data(T=2, J=20, F=5),
           integration=pyblp.Integration('product', 4),
           gamma=[0, 1, 2],
           beta=[-10, 0, 1, 0],
           sigma=[
               [1, 0, 0, 0],
               [0, 2, 0, 0],
               [0, 0, 0, 0],
               [0, 0, 0, 0]
           ],
           pi=[
               [0],
               [1],
               [0],
               [0]
           ],
           seed=0
       )
       simulation.product_data

    Bertrand-Nash prices and shares, which are initialized as ``numpy.nan`` above, can be computed by solving the
    simulation:

    .. ipython:: python

       product_data = simulation.solve()
       product_data

    """

    def __init__(self, id_data, integration, gamma, beta, sigma, pi=None, xi_variance=1, omega_variance=1,
                 correlation=0.9, linear_costs=True, seed=None):
        """Validate the specification and simulate all data except for Bertrand-Nash prices and shares."""

        # extract and validate IDs
        market_ids = extract_matrix(id_data, 'market_ids')
        firm_ids = extract_matrix(id_data, 'firm_ids')
        if market_ids.shape[1] > 1:
            raise ValueError("The market_ids field of id_data must be one-dimensional.")

        # validate full parameter vectors and matrices
        gamma = np.c_[np.asarray(gamma, options.dtype)]
        beta = np.c_[np.asarray(beta, options.dtype)]
        sigma = np.c_[np.asarray(sigma, options.dtype)]
        pi = None if pi is None else np.c_[np.asarray(pi, options.dtype)]
        if gamma.shape != (gamma.size, 1) or gamma.size < 1 or np.all(gamma == 0):
            raise ValueError("gamma must be a vector with at least one nonzero element.")
        if beta.shape != (gamma.size + 1, 1) or beta[0] == 0:
            raise ValueError("beta must be a vector with a nonzero first element and with one more element than gamma.")
        if sigma.shape != (beta.size, beta.size) or np.all(sigma.diagonal() == 0) or np.any(np.tril(sigma, -1) > 0):
            raise ValueError(
                "sigma must be a weakly upper triangular square matrix with as many rows and columns as there are "
                "elements in beta."
            )
        if pi is not None and pi.shape != (sigma.shape[0], pi.shape[1]):
            raise ValueError(f"pi must be a matrix with as many rows as sigma.")

        # identify nonzero parameter values
        gamma_indices = np.flatnonzero(gamma)
        beta_indices = np.flatnonzero(beta)
        sigma_indices = np.flatnonzero(sigma.diagonal())
        pi_indices = None if pi is None else np.flatnonzero(np.abs(pi).sum(axis=0))
        self.gamma = gamma[gamma_indices]
        self.beta = beta[beta_indices]
        self.sigma = sigma[np.ix_(sigma_indices, sigma_indices)]
        self.pi = None if pi is None else pi[np.ix_(sigma_indices, pi_indices)]

        # count dimensions
        self.N = market_ids.size
        self.T = np.unique(market_ids).size
        self.K1 = self.beta.size
        self.K2 = self.sigma.shape[1]
        self.K3 = self.gamma.size
        self.D = 0 if pi is None else self.pi.shape[1]

        # determine which product characteristics will go into which matrices
        linear_indices = np.flatnonzero(beta[2:])
        nonlinear_indices = np.flatnonzero(sigma.diagonal()[2:])
        cost_indices = np.flatnonzero(gamma[1:])

        # set the seed before simulating data
        if seed is not None:
            np.random.seed(seed)

        # simulate product characteristics and construct matrices of non-constant exogenous product characteristics
        self.characteristics = np.random.rand(self.N, beta.size - 2).astype(options.dtype)
        linear_characteristics = self.characteristics[:, linear_indices]
        nonlinear_characteristics = self.characteristics[:, nonlinear_indices]
        cost_characteristics = self.characteristics[:, cost_indices]

        # add constant columns to the matrices of product characteristics
        linear_constant = nonlinear_constant = cost_constant = False
        if beta[1] != 0:
            linear_constant = True
            linear_characteristics = np.c_[np.ones(self.N), linear_characteristics]
        if sigma[1, 1] != 0:
            nonlinear_constant = True
            nonlinear_characteristics = np.c_[np.ones(self.N), nonlinear_characteristics]
        if gamma[0] != 0:
            cost_constant = True
            cost_characteristics = np.c_[np.ones(self.N), cost_characteristics]

        # associate characteristic column indices with column indices in each subset of characteristics
        self.characteristic_indices = []
        for index in range(self.characteristics.shape[1]):
            self.characteristic_indices.append((
                list(linear_indices).index(index) + int(linear_constant) if index in linear_indices else None,
                list(nonlinear_indices).index(index) + int(nonlinear_constant) if index in nonlinear_indices else None,
                list(cost_indices).index(index) + int(cost_constant) if index in cost_indices else None
            ))

        # simulate xi and omega
        covariance = correlation * np.sqrt(xi_variance * omega_variance)
        variances = [[xi_variance, covariance], [covariance, omega_variance]]
        try:
            shocks = np.random.multivariate_normal([0, 0], variances, self.N, check_valid='raise').astype(options.dtype)
        except ValueError:
            raise ValueError("xi_variance, omega_variance, and covariance must furnish a positive-semidefinite matrix.")
        else:
            self.xi = shocks[:, [0]]
            self.omega = shocks[:, [1]]

        # compute marginal costs
        self.linear_costs = linear_costs
        self.costs = cost_characteristics @ self.gamma + self.omega
        if not linear_costs:
            self.costs = np.exp(self.costs)

        # construct instruments
        all_characteristics = self.characteristics[:, np.unique(np.r_[linear_indices, nonlinear_indices, cost_indices])]
        blp_demand_instruments = build_blp_instruments({
            'market_ids': market_ids,
            'firm_ids': firm_ids[:, 0],
            'characteristics': self.characteristics[:, np.unique(np.r_[linear_indices, nonlinear_indices])]
        })
        blp_supply_instruments = build_blp_instruments({
            'market_ids': market_ids,
            'firm_ids': firm_ids[:, 0],
            'characteristics': self.characteristics[:, cost_indices]
        })
        demand_instruments = np.c_[np.ones(self.N), all_characteristics, blp_demand_instruments]
        supply_instruments = np.c_[np.ones(self.N), all_characteristics, blp_supply_instruments]
        self.MD = demand_instruments.shape[1]
        self.MS = supply_instruments.shape[1]

        # structure all product data except for shares and prices, which for now are nullified
        self.nonlinear_prices = sigma[0, 0] != 0
        self.product_data = Matrices({
            'market_ids': (market_ids, np.object),
            'firm_ids': (firm_ids, np.object),
            'shares': (np.full(self.N, np.nan), options.dtype),
            'prices': (np.full(self.N, np.nan), options.dtype),
            'linear_characteristics': (linear_characteristics, options.dtype),
            'nonlinear_characteristics': (nonlinear_characteristics, options.dtype),
            'cost_characteristics': (cost_characteristics, options.dtype),
            'demand_instruments': (demand_instruments, options.dtype),
            'supply_instruments': (supply_instruments, options.dtype)
        })
        self.products = Products(self.product_data, self.nonlinear_prices)

        # validate integration
        if not isinstance(integration, Integration):
            raise ValueError("integration must be an Integration instance.")

        # build nodes and weights, simulate demographics, and structure agent data
        agent_market_ids, nodes, weights = integration._build_many(self.K2, np.unique(market_ids))
        self.integration = integration
        self.agent_data = Matrices({
            'market_ids': (agent_market_ids, np.object),
            'nodes': (nodes, options.dtype),
            'weights': (weights, options.dtype),
            'demographics': (np.random.rand(weights.size, self.D) if self.D > 0 else None, options.dtype)
        })
        self.agents = Agents(self.products, self.agent_data)

    def solve(self, firm_ids_index=0, prices=None, iteration=None, error_behavior='raise', processes=1):
        r"""Compute Bertrand-Nash prices and shares.

        Prices and shares are computed by iterating in each market over the :math:`\zeta`-markup equation from
        :ref:`Morrow and Skerlos (2011) <ms11>`,

        .. math:: p \leftarrow c + \zeta(p).

        Parameters
        ----------
        firm_ids_index : `int, optional`
            Index of the column in the `firm_ids` field of `id_data` in :class:`Simulation` initialization that defines
            which firms produce which products. By default, unchanged firm IDs are used.
        prices : `array-like, optional`
            Prices at which the fixed point iteration routine will start. By default, marginal costs, :math:`c`, are
            used as starting values.
        iteration : `Iteration, optional`
            :class:`Iteration` configuration for how to solve the fixed point problem. By default,
            ``Iteration('simple')`` is used.
        error_behavior : `str, optional`
            How to handle errors when computing prices and shares. For example, the fixed point routine may not converge
            if the effects of nonlinear parameters on price overwhelm the linear parameter on price, which should be
            sufficiently negative. The following behaviors are supported:

                - ``'raise'`` (default) - Raises an exception.

                - ``'warn'`` - Uses the last computed prices and shares. If the fixed point routine fails to converge,
                  these are the last prices and shares computed by the routine. If there are other issues, these are the
                  starting prices and their associated shares.

        processes : `int, optional`
            The number of Python processes that will be used during computation. By default, multiprocessing will not be
            used. For values greater than one, a pool of that many Python processes will be created. Market-by-market
            computation of prices and shares and its Jacobian will be distributed among these processes. Using
            multiprocessing will only improve computation speed if gains from parallelization outweigh overhead from
            creating the process pool.

        Returns
        -------
        `recarray`
            Simulated :attr:`Simulation.product_data` that are updated with Bertrand-Nash prices and shares, which can
            be passed to the `product_data` argument of :class:`Problem` initialization.

        """

        # choose or validate initial prices
        if prices is None:
            output("Starting with marginal costs as prices.")
            prices = self.costs
        else:
            output("Starting with the specified prices.")
            prices = np.c_[np.asarray(prices, dtype=options.dtype)]
            if prices.shape != (self.N, 1):
                raise ValueError(f"prices must be a vector with {self.N} elements.")

        # configure or validate integration
        if iteration is None:
            iteration = Iteration('simple')
        elif not isinstance(iteration, Iteration):
            raise ValueError("iteration must be an Iteration instance.")

        # validate error behavior
        if error_behavior not in {'raise', 'warn'}:
            raise ValueError("error_behavior must be 'raise' or 'warn'.")

        # output configuration information
        output(f"Firm IDs column index: {firm_ids_index}.")
        output(iteration)
        output(f"Error behavior: {error_behavior}.")
        output(f"Processes: {processes}.")

        # construct a mapping from market IDs to market-specific arguments used to compute prices and shares
        mapping = {}
        for t in np.unique(self.products.market_ids):
            market_t = SimulationMarket(
                t, self.nonlinear_prices, self.products, self.agents, xi=self.xi, beta=self.beta, sigma=self.sigma,
                pi=self.pi
            )
            prices_t = prices[self.products.market_ids.flat == t]
            costs_t = self.costs[self.products.market_ids.flat == t]
            mapping[t] = [market_t, prices_t, costs_t, firm_ids_index, iteration]

        # time how long it takes to solve for prices and shares
        output("Solving for prices and shares ...")
        start_time = time.time()

        # update prices and shares market-by-market
        errors = set()
        updated_product_data = self.product_data.copy()
        with ParallelItems(SimulationMarket.solve, mapping, processes) as items:
            for t, (prices_t, shares_t, errors_t) in items:
                updated_product_data.prices[self.products.market_ids.flat == t] = prices_t
                updated_product_data.shares[self.products.market_ids.flat == t] = shares_t
                errors |= errors_t

        # handle any errors
        if errors:
            exception = exceptions.MultipleErrors(errors)
            if error_behavior == 'raise':
                raise exception
            if error_behavior == 'warn':
                output("")
                output(exception)
                output("Using the last computed prices and shares.")
                output("")

        # output a message about how long it took to compute prices and shares
        end_time = time.time()
        output(f"Finished computing prices and shares after {output.format_seconds(end_time - start_time)}.")
        return updated_product_data


class SimulationMarket(Market):
    """A single market in the BLP simulation, which can be used to solve for a single market's prices and shares."""

    def solve(self, initial_prices, costs, firm_ids_index, iteration):
        """Solve the fixed point problem defined by the zeta-markup equation to compute prices and shares in this
        market. Also returned is a set of any exception classes encountered during computation.
        """

        # configure numpy to identify floating point errors
        errors = set()
        with np.errstate(all='call'):
            np.seterrcall(lambda *_: errors.add(exceptions.SyntheticPricesFloatingPointError))

            # solve the fixed point problem
            ownership = self.get_ownership_matrix(firm_ids_index)
            jacobian = self.compute_utilities_by_prices_jacobian()
            contraction = lambda p: costs + self.compute_zeta(ownership, jacobian, costs, p)
            prices, converged = iteration._iterate(contraction, initial_prices)

            # store whether the fixed point converged
            if not converged:
                errors.add(exceptions.SyntheticPricesConvergenceError)

            # compute the associated shares
            delta = self.update_delta_with_prices(prices)
            mu = self.update_mu_with_prices(prices)
            shares = self.compute_probabilities(delta, mu) @ self.agents.weights
            return prices, shares, errors
