"""Construction of commonly-used product data."""

import numpy as np

from . import options
from .utilities import extract_matrix, Matrices


def build_id_data(T, J, F, mergers=()):
    """Build a balanced panel of market and firm IDs.

    This function can be used to build `id_data` for :class:`Simulation` initialization.

    Parameters
    ----------
    T : `int`
        Number of markets.
    J : `int`
        Number of products in each market.
    F : `int`
        Number of firms. If `J` is divisible by `F`, firms produce ``J / F`` products in each market. Otherwise, firms
        with smaller IDs will produce excess products.
    mergers : `tuple of dict, optional`
        Each dictionary adds a column of changed firm IDs to the returned matrix of firm IDs. Changed firm IDs are
        identical to the first column of firm IDs, but IDs that are dictionary keys will be replaced with their values,
        which should also be firm IDs between ``0`` and ``F - 1``.

    Returns
    -------
    `recarray`
        IDs that associate products with markets and firms. Each of the ``T * J`` rows corresponds to a product. Fields:

            - **market_ids** : (`object`) - Market IDs that take on values from ``0`` to ``T - 1``.

            - **firm_ids** : (`object`) - Firm IDs that take on values from ``0`` to ``F - 1``. Any columns after the
              first are defined according to `mergers`.

    Example
    -------


    The following code builds a small panel of market and firm IDs with an extra column of firm IDs that represents a
    simple acquisition:

    .. ipython:: python
       :suppress:

       old_options = np.get_printoptions()
       np.set_printoptions(linewidth=1)

    .. ipython:: python

       id_data = pyblp.build_id_data(T=2, J=4, F=3, mergers=[{0: 1}])
       id_data

    .. ipython:: python
       :suppress:

       np.set_printoptions(**old_options)

    """

    # validate the arguments
    if T < 1 or F < 1:
        raise ValueError("Both T and F must be at least 1.")
    if J < F:
        raise ValueError("J must be at least F.")
    for mapping in mergers:
        if not isinstance(mapping, dict):
            raise TypeError("mergers must be a list of dicts.")
        for f1, f2 in mapping.items():
            if not isinstance(f1, int) or not isinstance(f2, int) or not 0 <= f1 <= F - 1 or not 0 <= f2 <= F - 1:
                raise ValueError("dicts in mergers must map from and to firm IDs, which are ints between 0 and F - 1.")

    # build all columns of firm IDs
    firm_ids_list = [np.floor(np.tile(np.arange(J), T) * F / J)]
    for mapping in mergers:
        changed_firm_ids = firm_ids_list[0].copy()
        for f1, f2 in mapping.items():
            changed_firm_ids[changed_firm_ids == f1] = f2
        firm_ids_list.append(changed_firm_ids)

    # build market IDs and structure both sets of IDs
    return Matrices({
        'market_ids': (np.repeat(np.arange(T), J).astype(np.int), np.object),
        'firm_ids': (np.stack(firm_ids_list, axis=1).astype(np.int), np.object)
    })


def build_indicators(ids):
    """Build indicator variables.

    Parameters
    ----------
    ids : `array-like`
        IDs from which indicator variables will be build. For example, these may be product or firm IDs.

    Returns
    -------
    `ndarray`
        Matrix of indicator variables with as many rows as there are elements in `ids` and with as many columns as there
        are unique elements in `ids`. Each column consists entirely of zeros except for rows for which `ids` takes on
        the value associated with the column.

    Example
    -------
    The following code loads the fake cereal product data from :ref:`Nevo (2000) <n00>` and builds indicator variables
    from its product IDs:

    .. ipython:: python

       import numpy as np
       data = np.recfromcsv(pyblp.data.NEVO_PRODUCTS_LOCATION)
       indicators = pyblp.build_indicators(data['product_ids'])
       indicators

    """
    ids = np.asarray(ids, dtype=np.object).flatten()
    return np.hstack([np.where(np.c_[ids] == i, 1, 0) for i in np.unique(ids)]).astype(options.dtype)


def build_blp_instruments(characteristic_data, average=False):
    r"""Construct traditional BLP instruments.

    For each column of product characteristics, two columns of instruments are created, which are defined for each
    market in terms of :math:`x_{jk}`, characteristic :math:`k` of product :math:`j` produced by firm :math:`f`:

        1. :math:`\sum_r x_{rk}`, in which each :math:`r` is not produced by firm :math:`f`.

        2. :math:`\sum_{r \neq j} x_{rk}`, in which each :math:`r` is produced by firm :math:`f`.


    Parameters
    ----------
    characteristic_data : `structured array-like`
        Each row corresponds to a product. Fields:

            - **market_ids** : (`object`) - IDs that associate products with markets.

            - **firm_ids** : (`object`) - IDs that associate products with firms.

            - **characteristics** : (`numeric`) - One or more columns of product characteristics. If there are multiple
              columns, this field can either be a matrix or it can be broken up into multiple one-dimensional fields
              with column index suffixes that start at zero. For example, if there are two columns, this field can be
              replaced with two one-dimensional fields: `characteristics0` and `characteristics1`.

    average : `bool`
        Whether to sum or average over characteristics. By default, characteristics are summed.

    Returns
    -------
    `ndarray`
        Traditional BLP instruments, which have two times the number of columns as the `characteristics` field of
        `characteristics_data`.

    Example
    -------
    The following code loads the automobile product data from :ref:`Berry, Levinsohn, and Pakes (1995) <blp95>`,
    constructs an array of non-price linear characteristics, and from it, builds instruments for the problem:

    .. ipython:: python

       import numpy as np
       data = np.recfromcsv(pyblp.data.BLP_PRODUCTS_LOCATION)
       linear = np.c_[np.ones(data.size), data['hpwt'], data['air'], data['mpg'], data['space']]
       characteristic_data = {
           'market_ids': data['market_ids'],
           'firm_ids': data['firm_ids'],
           'characteristics': linear
       }
       instruments = np.c_[linear, pyblp.build_blp_instruments(characteristic_data)]
       instruments.shape

    """

    # extract and validate IDs and characteristics
    market_ids = extract_matrix(characteristic_data, 'market_ids')
    firm_ids = extract_matrix(characteristic_data, 'firm_ids')
    characteristics = extract_matrix(characteristic_data, 'characteristics')
    if market_ids is None or firm_ids is None or characteristics is None:
        raise KeyError("characteristic_data must have market_ids, firm_ids, and characteristics fields.")
    if market_ids.shape[1] > 1:
        raise ValueError("The market_ids field of characteristic_data must be one-dimensional.")
    if firm_ids.shape[1] > 1:
        raise ValueError("The firm_ids field of characteristic_data must be one-dimensional.")

    # determine the aggregation function
    aggregate = np.mean if average else np.sum

    # build the instruments
    indices = np.arange(market_ids.size)
    rival = np.zeros_like(characteristics, dtype=options.dtype)
    other = np.zeros_like(characteristics, dtype=options.dtype)
    for n, (t, f) in enumerate(zip(market_ids, firm_ids)):
        rival[n] = aggregate(characteristics[(market_ids.flat == t) & (firm_ids.flat != f)], axis=0)
        other[n] = aggregate(characteristics[(market_ids.flat == t) & (firm_ids.flat == f) & (indices != n)], axis=0)
    return np.c_[rival, other]
