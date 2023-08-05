from __future__ import absolute_import


import inspect

import pandas as pd
from sklearn import base
from sklearn import decomposition as orig

from .._adapter import frame_ex
from .._utils import set_lowest_level_column_names


def transform(self, base_ret):
    if isinstance(base_ret, pd.DataFrame):
        set_lowest_level_column_names(
            base_ret,
            ['comp_%i' % i for i in range(len(base_ret.columns))])
    return base_ret


def get_transform_doc(
        orig,
        name,
        est,
        kwargs,
        is_regressor,
        is_classifier,
        is_transformer,
        is_clusterer,
        has_dataframe_y):

    return r"""
    Example:

        >>> import pandas as pd
        >>> import numpy as np
        >>> from ibex.sklearn import datasets
        >>> from ibex.sklearn.decomposition import PCA as PdPCA

        >>> iris = datasets.load_iris()
        >>> features = iris['feature_names']
        >>> iris = pd.DataFrame(
        ...     np.c_[iris['data'], iris['target']],
        ...     columns=features+['class'])

        >>> iris[features]
        sepal length (cm)  sepal width (cm)  petal length (cm)  petal width (cm)
        0                5.1               3.5                1.4               0.2
        1                4.9               3.0                1.4               0.2
        2                4.7               3.2                1.3               0.2
        3                4.6               3.1                1.5               0.2
        4                5.0               3.6                1.4               0.2
        ...

        >>> PdPCA(n_components=2).fit(iris[features], iris['class']).transform(iris[features])
            comp_0    comp_1
        0   -2.684207 ...0.326607
        1   -2.715391 ...0.169557
        2   -2.889820 ...0.137346
        3   -2.746437 ...0.311124
        4   -2.728593 ...0.333925
        ...

    """


def fit_transform(self, base_ret):
    if isinstance(base_ret, pd.DataFrame):
        set_lowest_level_column_names(
            base_ret,
            ['comp_%i' % i for i in range(len(base_ret.columns))])
    return base_ret


def get_fit_transform_doc(
        orig,
        name,
        est,
        kwargs,
        is_regressor,
        is_classifier,
        is_transformer,
        is_clusterer,
        has_dataframe_y):
    return r"""
    Example:

        >>> import pandas as pd
        >>> import numpy as np
        >>> from ibex.sklearn import datasets
        >>> from ibex.sklearn.decomposition import PCA as PdPCA

        >>> iris = datasets.load_iris()
        >>> features = iris['feature_names']
        >>> iris = pd.DataFrame(
        ...     np.c_[iris['data'], iris['target']],
        ...     columns=features+['class'])

        >>> iris[features]
        sepal length (cm)  sepal width (cm)  petal length (cm)  petal width (cm)
        0                5.1               3.5                1.4               0.2
        1                4.9               3.0                1.4               0.2
        2                4.7               3.2                1.3               0.2
        3                4.6               3.1                1.5               0.2
        4                5.0               3.6                1.4               0.2
        ...

        >>> PdPCA(n_components=2).fit(iris[features], iris['class']).transform(iris[features])
            comp_0    comp_1
        0   -2.684207 ...0.326607
        1   -2.715391 ...0.169557
        2   -2.889820 ...0.137346
        3   -2.746437 ...0.311124
        4   -2.728593 ...0.333925
        ...

    """


def components_(self, base_ret):
    return pd.DataFrame(
        base_ret,
        index=['comp_%i' % i for i in range(len(base_ret))],
        columns=self.x_columns)


def get_components_doc(
        orig,
        name,
        est,
        kwargs,
        is_regressor,
        is_classifier,
        is_transformer,
        is_clusterer,
        has_dataframe_y):
    return r"""
    Example:

        >>> import pandas as pd
        >>> import numpy as np
        >>> from ibex.sklearn import datasets
        >>> from ibex.sklearn.decomposition import PCA as PdPCA

        >>> iris = datasets.load_iris()
        >>> features = iris['feature_names']
        >>> iris = pd.DataFrame(
        ...     np.c_[iris['data'], iris['target']],
        ...     columns=features+['class'])

        >>> iris[features]
        sepal length (cm)  sepal width (cm)  petal length (cm)  petal width (cm)
        0                5.1               3.5                1.4               0.2
        1                4.9               3.0                1.4               0.2
        2                4.7               3.2                1.3               0.2
        3                4.6               3.1                1.5               0.2
        4                5.0               3.6                1.4               0.2
        ...

        >>> PdPCA(n_components=2).fit(iris[features], iris['class']).transform(iris[features])
            comp_0    comp_1
        0   -2.684207 ...0.326607
        1   -2.715391 ...0.169557
        2   -2.889820 ...0.137346
        3   -2.746437 ...0.311124
        4   -2.728593 ...0.333925
        ...

    """
