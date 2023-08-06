import numpy as np


def make_linear_combination(*functions, weights=None):
    """
    Takes the given functions and makes a function which returns the linear combination
    of the output of original functions. It works well with functions returning numpy
    arrays of the same shape.

    Parameters
    ----------
    *functions: base functions for the linear combination
        The functions shall have the same argument and if they return numpy arrays,
        the returned arrays shall have the same shape.

    weights: array-like, length shall match the number of functions given
        Coefficients of the functions in the linear combination. The i-th given function
        will be multiplied with with weights[i]

    Returns
    -------
    linear_combination: function
        A function which returns the linear combination of the given functions output.
    """

    if weights is None:
        weights = np.ones(shape=(len(functions)))
    else:
        assert len(functions) == len(weights), 'the length of weights must be the ' \
                                               'same as the number of given functions'

    def linear_combination(*args, **kwargs):
        return np.sum((weights[i]*functions[i](*args, **kwargs)
                       for i in range(len(weights))), axis=0)

    return linear_combination


def make_product(*functions, exponents=None):
    """
    Takes the given functions and makes a function which returns the product of the output
    of original functions. It works well with functions returning numpy arrays of the same
    shape.

    Parameters
    ----------
    *functions: base functions for the product
        The functions shall have the same argument and if they return numpy arrays,
        the returned arrays shall have the same shape.

    exponents: array-like, length shall match the number of functions given
        Exponents of the functions in the product. The i-th given function in the product
        will be raised to the power of exponents[i]

    Returns
    -------
    product_function: function
        A function which returns the product function of the given functions output.
    """

    if exponents is None:
        exponents = np.ones(shape=(len(functions)))
    else:
        assert len(functions) == len(exponents), 'the length of exponents must be the ' \
                                                 'same as the number of given functions'

    def product_function(*args, **kwargs):
        return np.prod([functions[i](*args, **kwargs)**exponents[i]
                       for i in range(len(exponents))], axis=0)

    return product_function


def make_query_strategy(utility_measure, selector):
    """
    Takes the given utility measure and selector functions and makes a query strategy
    by combining them.

    Parameters
    ----------
    utility_measure: function
        Utility measure, for instance modAL.disagreement.vote_entropy, but it can be
        a custom function as well. Should take a classifier and the unlabelled data
        and should return an array containing the utility scores.

    selector: function
        Function selecting instances for query. Should take an array of utility scores
        and should return an array containing the queried items.

    Returns
    -------
    query_strategy: function
        A function which returns queried instances given a classifier and an unlabelled
        pool.
    """

    def query_strategy(classifier, X):
        utility = utility_measure(classifier, X)
        query_idx = selector(utility)
        return query_idx, X[query_idx]

    return query_strategy
