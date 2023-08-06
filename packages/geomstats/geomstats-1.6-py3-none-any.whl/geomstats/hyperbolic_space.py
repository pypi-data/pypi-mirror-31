"""
Computations on the Hyperbolic space H_n
as embedded in Minkowski space R^{1,n}.

Elements of the Hyperbolic space are the elements
of Minkowski space of squared norm -1.

NB: we use "riemannian" to refer to "pseudo-riemannian".
"""

import logging
import math
import numpy as np

from geomstats.embedded_manifold import EmbeddedManifold
from geomstats.minkowski_space import MinkowskiMetric
from geomstats.minkowski_space import MinkowskiSpace
from geomstats.riemannian_metric import RiemannianMetric
import geomstats.vectorization as vectorization

TOLERANCE = 1e-6

SINH_TAYLOR_COEFFS = [0., 1.,
                      0., 1 / math.factorial(3),
                      0., 1 / math.factorial(5),
                      0., 1 / math.factorial(7),
                      0., 1 / math.factorial(9)]
COSH_TAYLOR_COEFFS = [1., 0.,
                      1 / math.factorial(2), 0.,
                      1 / math.factorial(4), 0.,
                      1 / math.factorial(6), 0.,
                      1 / math.factorial(8), 0.]
INV_SINH_TAYLOR_COEFFS = [0., - 1. / 6.,
                          0., + 7. / 360.,
                          0., - 31. / 15120.,
                          0., + 127. / 604800.]
INV_TANH_TAYLOR_COEFFS = [0., + 1. / 3.,
                          0., - 1. / 45.,
                          0., + 2. / 945.,
                          0., -1. / 4725.]


class HyperbolicSpace(EmbeddedManifold):
    """
    Hyperbolic space embedded in Minkowski space.
    Note: points are parameterized by the extrinsic
    coordinates by defaults.
    """

    def __init__(self, dimension):
        super(HyperbolicSpace, self).__init__(
                dimension=dimension,
                embedding_manifold=MinkowskiSpace(dimension+1))
        self.embedding_metric = self.embedding_manifold.metric
        self.metric = HyperbolicMetric(self.dimension)

    def belongs(self, point, tolerance=TOLERANCE):
        """
        By definition, a point on the Hyperbolic space
        has Minkowski squared norm -1.

        We use a tolerance relative to the Euclidean norm of
        the point.

        Note: point must be given in extrinsic coordinates.
        """
        point = vectorization.to_ndarray(point, to_ndim=2)
        _, point_dim = point.shape

        if point_dim is not self.dimension + 1:
            if point_dim is self.dimension:
                logging.warning('Use the extrinsic coordinates to '
                                'represent points on the hyperbolic space.')
            return False

        sq_norm = self.embedding_metric.squared_norm(point)
        euclidean_sq_norm = np.dot(point, point.transpose())
        diff = np.abs(sq_norm + 1)
        return diff < tolerance * euclidean_sq_norm

    def regularize(self, point):
        # TODO(nina): vectorize
        assert self.belongs(point)
        sq_norm = self.embedding_metric.squared_norm(point)
        real_norm = np.sqrt(np.abs(sq_norm))
        for i in range(len(real_norm)):
            if real_norm[i] != 0:
                point[i] = point[i] / real_norm[i]
        return point

    def intrinsic_to_extrinsic_coords(self, point_intrinsic):
        """
        From the intrinsic coordinates in the hyperbolic space,
        to the extrinsic coordinates in Minkowski space.
        """
        point_intrinsic = vectorization.to_ndarray(point_intrinsic,
                                                   to_ndim=2)
        n_points, _ = point_intrinsic.shape

        dimension = self.dimension
        point_extrinsic = np.zeros((n_points, dimension + 1))
        point_extrinsic[:, 1: dimension + 1] = point_intrinsic[:, 0: dimension]
        point_extrinsic[:, 0] = np.sqrt(1. + np.linalg.norm(point_intrinsic,
                                                            axis=1) ** 2)
        assert np.all(self.belongs(point_extrinsic))

        assert point_extrinsic.ndim == 2
        return point_extrinsic

    def extrinsic_to_intrinsic_coords(self, point_extrinsic):
        """
        From the extrinsic coordinates in Minkowski space,
        to the extrinsic coordinates in Hyperbolic space.
        """
        point_extrinsic = vectorization.to_ndarray(point_extrinsic,
                                                   to_ndim=2)
        assert np.all(self.belongs(point_extrinsic))

        point_intrinsic = point_extrinsic[:, 1:]
        assert point_intrinsic.ndim == 2
        return point_intrinsic

    def projection_to_tangent_space(self, vector, base_point):
        """
         Project the vector vector onto the tangent space at base_point
         T_{base_point}H
                = { w s.t. embedding_inner_product(base_point, w) = 0 }
        """
        assert self.belongs(base_point)

        inner_prod = self.embedding_metric.inner_product(base_point,
                                                         vector)
        sq_norm_base_point = self.embedding_metric.squared_norm(base_point)

        tangent_vec = vector - inner_prod * base_point / sq_norm_base_point
        return tangent_vec

    def random_uniform(self, n_samples=1, max_norm=1):
        """
        Generate random elements on the hyperbolic space.
        """
        point = (np.random.rand(n_samples, self.dimension) - .5) * max_norm
        point = self.intrinsic_to_extrinsic_coords(point)
        assert np.all(self.belongs(point))

        assert point.ndim == 2
        return point


class HyperbolicMetric(RiemannianMetric):

    def __init__(self, dimension):
        self.dimension = dimension
        self.signature = (dimension, 0, 0)
        self.embedding_metric = MinkowskiMetric(dimension + 1)

    def squared_norm(self, vector, base_point=None):
        """
        Squared norm associated to the Hyperbolic Metric.
        """
        sq_norm = self.embedding_metric.squared_norm(vector)
        return sq_norm

    def projection_to_tangent_space(self, vector, base_point):
        """
         Project the vector vector onto the tangent space at base_point
         T_{base_point}H
                = { w s.t. embedding_inner_product(base_point, w) = 0 }
        """
        # TODO(nina): define HyperbolicMetric class inside HyperbolicSpace
        # so that there is no need to copy-paste this code?
        inner_prod = self.embedding_metric.inner_product(base_point,
                                                         vector)
        sq_norm_base_point = self.embedding_metric.squared_norm(base_point)

        tangent_vec = vector - inner_prod * base_point / sq_norm_base_point
        return tangent_vec

    def exp_basis(self, tangent_vec, base_point):
        """
        Compute the Riemannian exponential at point base_point
        of tangent vector tangent_vec wrt the metric obtained by
        embedding of the hyperbolic space in the Minkowski space.

        This gives a point on the hyperbolic space.

        :param base_point: a point on the hyperbolic space
        :param vector: vector
        :returns riem_exp: a point on the hyperbolic space
        """
        projected_tangent_vec = self.projection_to_tangent_space(
            vector=tangent_vec, base_point=base_point)
        diff = np.abs(projected_tangent_vec - tangent_vec)
        if not np.allclose(diff, 0):
            tangent_vec = projected_tangent_vec
            logging.warning(
                'The input vector is not tangent to the hyperbolic space.'
                ' We project it on the tangent space at base_point={}.'.format(
                    base_point))

        sq_norm_tangent_vec = self.embedding_metric.squared_norm(
                tangent_vec)
        norm_tangent_vec = np.sqrt(sq_norm_tangent_vec)

        if np.isclose(sq_norm_tangent_vec, 0):
            coef_1 = (1. + COSH_TAYLOR_COEFFS[2] * norm_tangent_vec ** 2
                      + COSH_TAYLOR_COEFFS[4] * norm_tangent_vec ** 4
                      + COSH_TAYLOR_COEFFS[6] * norm_tangent_vec ** 6
                      + COSH_TAYLOR_COEFFS[8] * norm_tangent_vec ** 8)
            coef_2 = (1. + SINH_TAYLOR_COEFFS[3] * norm_tangent_vec ** 2
                      + SINH_TAYLOR_COEFFS[5] * norm_tangent_vec ** 4
                      + SINH_TAYLOR_COEFFS[7] * norm_tangent_vec ** 6
                      + SINH_TAYLOR_COEFFS[9] * norm_tangent_vec ** 8)
        else:
            coef_1 = np.cosh(norm_tangent_vec)
            coef_2 = np.sinh(norm_tangent_vec) / norm_tangent_vec

        riem_exp = coef_1 * base_point + coef_2 * tangent_vec

        hyperbolic_space = HyperbolicSpace(dimension=self.dimension)
        riem_exp = hyperbolic_space.regularize(riem_exp)
        return riem_exp

    def log_basis(self, point, base_point):
        """
        Compute the Riemannian logarithm at point base_point,
        of point wrt the metric obtained by
        embedding of the hyperbolic space in the Minkowski space.

        This gives a tangent vector at point base_point.

        :param base_point: point on the hyperbolic space
        :param point: point on the hyperbolic space
        :returns riem_log: tangent vector at base_point
        """
        angle = self.dist(base_point, point)
        if np.isclose(angle, 0):
            coef_1 = (1. + INV_SINH_TAYLOR_COEFFS[1] * angle ** 2
                      + INV_SINH_TAYLOR_COEFFS[3] * angle ** 4
                      + INV_SINH_TAYLOR_COEFFS[5] * angle ** 6
                      + INV_SINH_TAYLOR_COEFFS[7] * angle ** 8)
            coef_2 = (1. + INV_TANH_TAYLOR_COEFFS[1] * angle ** 2
                      + INV_TANH_TAYLOR_COEFFS[3] * angle ** 4
                      + INV_TANH_TAYLOR_COEFFS[5] * angle ** 6
                      + INV_TANH_TAYLOR_COEFFS[7] * angle ** 8)
        else:
            coef_1 = angle / np.sinh(angle)
            coef_2 = angle / np.tanh(angle)
        return coef_1 * point - coef_2 * base_point

    def dist(self, point_a, point_b):
        """
        Compute the distance induced on the hyperbolic
        space, from its embedding in the Minkowski space.
        """
        if np.all(point_a == point_b):
            return 0.
        point_a = vectorization.to_ndarray(point_a, to_ndim=2)
        point_b = vectorization.to_ndarray(point_b, to_ndim=2)

        n_points_a, _ = point_a.shape
        n_points_b, _ = point_b.shape

        assert (n_points_a == n_points_b
                or n_points_a == 1
                or n_points_b == 1)

        n_dists = np.maximum(n_points_a, n_points_b)
        dist = np.zeros((n_dists, 1))
        sq_norm_a = self.embedding_metric.squared_norm(point_a)
        sq_norm_b = self.embedding_metric.squared_norm(point_b)
        inner_prod = self.embedding_metric.inner_product(point_a, point_b)

        cosh_angle = - inner_prod / np.sqrt(sq_norm_a * sq_norm_b)

        mask_cosh_less_1 = np.less_equal(cosh_angle, 1.)
        mask_cosh_greater_1 = ~mask_cosh_less_1

        dist[mask_cosh_less_1] = 0.
        dist[mask_cosh_greater_1] = np.arccosh(cosh_angle[mask_cosh_greater_1])

        return dist
