import pytest
from numpy import testing as npt

import numpy as np
import xarray as xr

from rigid_body_motion.core import \
    _resolve_axis, _maybe_unpack_dataarray, _make_dataarray


class TestCore(object):

    def test_resolve_axis(self):
        """"""
        assert _resolve_axis(0, 1) == 0
        assert _resolve_axis(-1, 1) == 0
        assert _resolve_axis((0, -1), 2) == (0, 1)
        assert _resolve_axis(None, 2) == (0, 1)

        with pytest.raises(IndexError):
            _resolve_axis(2, 1)
        with pytest.raises(IndexError):
            _resolve_axis((-2, 0), 1)

    def test_maybe_unpack_datarray(self):
        """"""
        # ndarray
        arr = np.ones((10, 3))
        arr_out, axis, timestamps, coords, dims, name, attrs = \
            _maybe_unpack_dataarray(arr)
        assert arr_out is arr
        assert axis == -1
        assert timestamps is None
        assert coords is None
        assert dims is None
        assert name is None
        assert attrs is None

        # dim argument with ndarray
        with pytest.raises(ValueError):
            _maybe_unpack_dataarray(arr, dim='cartesian_axis')

        # DataArray
        da = xr.DataArray(
            arr, {'time': np.arange(10)}, ('time', 'cartesian_axis'), 'da',
            {'test_attr': 0})
        arr_out, axis, timestamps, coords, dims, name, attrs = \
            _maybe_unpack_dataarray(
                da, dim='cartesian_axis', timestamps='time')
        npt.assert_equal(arr_out, arr)
        assert axis == 1
        npt.assert_equal(timestamps, np.arange(10))
        assert all(c in da.coords for c in coords)
        assert dims is da.dims
        assert name is da.name
        assert attrs is da.attrs

        # static DataArray
        da = xr.DataArray(arr[0], dims=('cartesian_axis',))
        arr_out, axis, timestamps, coords, dims, _, _ = \
            _maybe_unpack_dataarray(
                da, dim='cartesian_axis', timestamps=None)
        npt.assert_equal(arr_out, arr[0])
        assert axis == 0
        assert timestamps is None

        # dim and axis argument at the same time
        with pytest.raises(ValueError):
            _maybe_unpack_dataarray(da, dim='cartesian_axis', axis=-1)

    def test_make_dataarray(self):
        """"""
        arr = np.ones((10, 3))

        # no input timestamps
        da_out = _make_dataarray(
            arr, {}, ('cartesian_axis',), 'da', {'test_attr': 0}, None,
            np.arange(10))
        npt.assert_equal(da_out, arr)
        assert da_out.dims == ('time', 'cartesian_axis')
        npt.assert_equal(da_out.coords['time'], np.arange(10))
        assert da_out.name == 'da'
        assert da_out.attrs['test_attr'] == 0

        # timestamps from coord
        da_in = xr.DataArray(
            arr, dims=('time', 'cartesian_axis'),
            coords={'time': np.arange(10),
                    'test_coord': ('time', 2*np.arange(10))})
        da_out = _make_dataarray(arr[:5], dict(da_in.coords), da_in.dims,
                                 None, None, 'time', np.arange(5) + 2.5)
        npt.assert_allclose(da_out, arr[:5])
        assert da_out.dims == ('time', 'cartesian_axis')
        npt.assert_equal(da_out.coords['time'], np.arange(5)+2.5)
        npt.assert_allclose(da_out.coords['test_coord'], 2*np.arange(5)+5)

        # invalid coord name
        with pytest.raises(ValueError):
            _make_dataarray(
                arr, dict(da_in.coords), da_in.dims, None, None,
                'not_a_coord', None)