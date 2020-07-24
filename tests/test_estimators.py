import numpy as np
import pytest
from numpy import testing as npt

from rigid_body_motion.estimators import (
    best_fit_transform,
    shortest_arc_rotation,
)


class TestEstimators(object):
    def test_shortest_arc_rotation(self):
        """"""
        # ndarray
        v1 = np.zeros((10, 3))
        v1[:, 0] = 1.0
        v2 = np.zeros((10, 3))
        v2[:, 1] = 1.0
        q_exp = np.tile((np.sqrt(2) / 2, 0.0, 0.0, np.sqrt(2) / 2), (10, 1))

        npt.assert_allclose(shortest_arc_rotation(v1, v2), q_exp)

    def test_shortest_arc_rotation_xr(self):
        """"""
        xr = pytest.importorskip("xarray")

        v1 = np.zeros((10, 3))
        v1[:, 0] = 1.0
        v2 = np.zeros((10, 3))
        v2[:, 1] = 1.0
        q_exp = np.tile((np.sqrt(2) / 2, 0.0, 0.0, np.sqrt(2) / 2), (10, 1))

        v1_da = xr.DataArray(
            v1, {"cartesian_axis": ["x", "y", "z"]}, ("time", "cartesian_axis")
        )
        expected = xr.DataArray(
            q_exp,
            {"quaternion_axis": ["w", "x", "y", "z"]},
            ("time", "quaternion_axis"),
        )
        actual = shortest_arc_rotation(v1_da, v2, dim="cartesian_axis")

        xr.testing.assert_allclose(actual, expected)

    def test_best_fit_transform(self, get_rf_tree, mock_quaternion):
        """"""
        rf_world, rf_child1, _ = get_rf_tree(
            (1.0, 0.0, 0.0), mock_quaternion(np.pi / 2, 0.0, 0.0)
        )
        v1 = np.random.randn(10, 3)
        v2 = rf_world.transform_points(v1, rf_child1)

        t, r = best_fit_transform(v1, v2)
        t_exp, r_exp, _ = rf_world.get_transformation(rf_child1)
        npt.assert_allclose(t, t_exp, rtol=1.0, atol=1e-10)
        npt.assert_allclose(np.abs(r), np.abs(r_exp), rtol=1.0, atol=1e-10)

        # not 3d
        with pytest.raises(ValueError):
            best_fit_transform(v1[:, :2], v2[:, :2])

        # not enough dimensions
        with pytest.raises(ValueError):
            best_fit_transform(v1[0], v2[0])

        # different shapes
        with pytest.raises(ValueError):
            best_fit_transform(v1, v2[:, :2])

    def test_best_fit_transform_xr(self, get_rf_tree, mock_quaternion):
        """"""
        xr = pytest.importorskip("xarray")

        rf_world, rf_child1, _ = get_rf_tree(
            (1.0, 0.0, 0.0), mock_quaternion(np.pi / 2, 0.0, 0.0)
        )
        v1 = np.random.randn(10, 3)
        v2 = rf_world.transform_points(v1, rf_child1)

        v1_da = xr.DataArray(
            v1, {"cartesian_axis": ["x", "y", "z"]}, ("time", "cartesian_axis")
        )
        t, r = best_fit_transform(v1_da.T, v2.T, dim="cartesian_axis")

        assert t.dims == ("cartesian_axis",)
        assert r.dims == ("quaternion_axis",)
