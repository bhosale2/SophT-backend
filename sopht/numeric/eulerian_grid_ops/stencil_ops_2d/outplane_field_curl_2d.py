"""Kernels for computing curl of outplane field in 2D."""
import numpy as np

import pystencils as ps

from sopht.numeric.eulerian_grid_ops.stencil_ops_2d.elementwise_ops_2d import (
    gen_set_fixed_val_at_boundaries_pyst_kernel_2d,
)

import sympy as sp


def gen_outplane_field_curl_pyst_kernel_2d(
    real_t, num_threads=False, fixed_grid_size=False
):
    """2D Outplane field curl kernel generator."""
    pyst_dtype = "float32" if real_t == np.float32 else "float64"
    kernel_config = ps.CreateKernelConfig(data_type=pyst_dtype, cpu_openmp=num_threads)
    # we can add dtype checks later
    grid_info = (
        f"{fixed_grid_size[0]}, {fixed_grid_size[1]}" if fixed_grid_size else "2D"
    )

    @ps.kernel
    def _outplane_field_curl_x_stencil_2d():
        curl_x, field = ps.fields(f"curl_x, field : {pyst_dtype}[{grid_info}]")
        prefactor = sp.symbols("prefactor")
        # curl_x = d (field) / dy
        curl_x[0, 0] @= (field[1, 0] - field[-1, 0]) * prefactor

    _outplane_field_curl_x_pyst_kernel_2d = ps.create_kernel(
        _outplane_field_curl_x_stencil_2d, config=kernel_config
    ).compile()

    @ps.kernel
    def _outplane_field_curl_y_stencil_2d():
        curl_y, field = ps.fields(f"curl_y, field : {pyst_dtype}[{grid_info}]")
        prefactor = sp.symbols("prefactor")
        # curl_y = -d (field) / dx
        curl_y[0, 0] @= (field[0, -1] - field[0, 1]) * prefactor

    _outplane_field_curl_y_pyst_kernel_2d = ps.create_kernel(
        _outplane_field_curl_y_stencil_2d, config=kernel_config
    ).compile()

    # to set boundary zone = 0
    boundary_width = 1
    set_fixed_val_at_boundaries_2d = gen_set_fixed_val_at_boundaries_pyst_kernel_2d(
        real_t=real_t,
        width=boundary_width,
        num_threads=num_threads,
    )

    def outplane_field_curl_pyst_kernel_2d(curl, field, prefactor):
        """Outplane field curl in 2D.

        Computes curl of outplane 2D vector field (field)
        into vector 2D inplane field (curl_x, curl_y).
        Used for psi ---> velocity
        Assumes curl field is (2, n, n).
        """
        _outplane_field_curl_x_pyst_kernel_2d(
            curl_x=curl[0], field=field, prefactor=prefactor
        )
        _outplane_field_curl_y_pyst_kernel_2d(
            curl_y=curl[1], field=field, prefactor=prefactor
        )
        # set boundary unaffected points to 0
        # TODO need one sided corrections?
        set_fixed_val_at_boundaries_2d(field=curl[0], fixed_val=0)
        set_fixed_val_at_boundaries_2d(field=curl[1], fixed_val=0)

    return outplane_field_curl_pyst_kernel_2d
