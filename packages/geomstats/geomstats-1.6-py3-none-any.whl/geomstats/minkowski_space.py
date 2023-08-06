"""
Computations on the (n+1)-dimensional Minkowski space.
"""

import numpy as np

from geomstats.manifold import Manifold
from geomstats.riemannian_metric import RiemannianMetric
import geomstats.vectorization as vectorization


class MinkowskiSpace(Manifold):
    """The Minkowski Space."""

    def __init__(self, dimension):
        self.dimension = dimension
        self.metric = MinkowskiMetric(dimension)

    def belongs(self, point):
        """
        Check if point belongs to the Minkowski space.
        """
        point = vectorization.to_ndarray(point, to_ndim=2)
        _, point_dim = point.shape
        return point_dim == self.dimension

    def random_uniform(self, n_samples=1):
        """
        Sample a vector uniformly in the Minkowski space,
        with coordinates each between -1. and 1.
        """
        point = np.random.rand(n_samples, self.dimension) * 2 - 1
        return point


class MinkowskiMetric(RiemannianMetric):
    """
    Class for the pseudo-Riemannian Minkowski metric.
    The metric is flat: inner product independent of the reference point.
    The metric has signature (-1, n) on the (n+1)-D vector space.
    """
    def __init__(self, dimension):
        super(MinkowskiMetric, self).__init__(
                                          dimension=dimension,
                                          signature=(dimension - 1, 1, 0))

    def inner_product_matrix(self, base_point=None):
        """
        Minkowski inner product matrix.

        Note: the matrix is independent on the base_point.
        """
        inner_prod_mat = np.eye(self.dimension)
        inner_prod_mat[0, 0] = -1
        return inner_prod_mat

    def exp_basis(self, tangent_vec, base_point):
        """
        The Riemannian exponential is the addition in the Minkowski space.
        """
        return base_point + tangent_vec

    def log_basis(self, point, base_point):
        """
        The Riemannian logarithm is the subtraction in the Minkowski space.
        """
        return point - base_point

    def mean(self, points, weights=None):
        """
        Weighted mean of the points.
        """
        return np.average(points, axis=0, weights=weights)
