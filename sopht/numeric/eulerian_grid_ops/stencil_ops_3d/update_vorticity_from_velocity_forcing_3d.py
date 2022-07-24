"""Kernels for updating vorticity based on velocity forcing in 3D."""
import numpy as np

import pystencils as ps

import sympy as sp


def gen_update_vorticity_from_velocity_forcing_pyst_kernel_3d(
    real_t, num_threads=False, fixed_grid_size=False
):
    # TODO expand docs
    """Update vorticity based on velocity forcing in 3D kernel generator."""
    pyst_dtype = "float32" if real_t == np.float32 else "float64"
    kernel_config = ps.CreateKernelConfig(data_type=pyst_dtype, cpu_openmp=num_threads)
    # we can add dtype checks later
    grid_info = (
        f"{fixed_grid_size[0]}, {fixed_grid_size[1]}, {fixed_grid_size[2]}"
        if fixed_grid_size
        else "3D"
    )

    @ps.kernel
    def _update_vorticity_from_velocity_forcing_x_comp_stencil_3d():
        (
            vorticity_field_x,
            velocity_forcing_field_y,
            velocity_forcing_field_z,
        ) = ps.fields(
            f"vorticity_field_x, velocity_forcing_field_y, "
            f"velocity_forcing_field_z : {pyst_dtype}[{grid_info}]"
        )
        prefactor = sp.symbols("prefactor")
        # curl_x = df_z / dy - df_y / dz
        vorticity_field_x[0, 0, 0] @= vorticity_field_x[0, 0, 0] + prefactor * (
            velocity_forcing_field_z[0, 1, 0]
            - velocity_forcing_field_z[0, -1, 0]
            - velocity_forcing_field_y[1, 0, 0]
            + velocity_forcing_field_y[-1, 0, 0]
        )

    _update_vorticity_from_velocity_forcing_x_comp_kernel_3d = ps.create_kernel(
        _update_vorticity_from_velocity_forcing_x_comp_stencil_3d, config=kernel_config
    ).compile()

    @ps.kernel
    def _update_vorticity_from_velocity_forcing_y_comp_stencil_3d():
        (
            vorticity_field_y,
            velocity_forcing_field_x,
            velocity_forcing_field_z,
        ) = ps.fields(
            f"vorticity_field_y, velocity_forcing_field_x,"
            f" velocity_forcing_field_z : {pyst_dtype}[{grid_info}]"
        )
        prefactor = sp.symbols("prefactor")
        # curl_y = df_x / dz - df_z / dx
        vorticity_field_y[0, 0, 0] @= vorticity_field_y[0, 0, 0] + prefactor * (
            velocity_forcing_field_x[1, 0, 0]
            - velocity_forcing_field_x[-1, 0, 0]
            - velocity_forcing_field_z[0, 0, 1]
            + velocity_forcing_field_z[0, 0, -1]
        )

    _update_vorticity_from_velocity_forcing_y_comp_kernel_3d = ps.create_kernel(
        _update_vorticity_from_velocity_forcing_y_comp_stencil_3d, config=kernel_config
    ).compile()

    @ps.kernel
    def _update_vorticity_from_velocity_forcing_z_comp_stencil_3d():
        (
            vorticity_field_z,
            velocity_forcing_field_x,
            velocity_forcing_field_y,
        ) = ps.fields(
            f"vorticity_field_z, velocity_forcing_field_x,"
            f" velocity_forcing_field_y : {pyst_dtype}[{grid_info}]"
        )
        ""
        prefactor = sp.symbols("prefactor")
        # curl_z = df_y / dx - df_x / dy
        vorticity_field_z[0, 0, 0] @= vorticity_field_z[0, 0, 0] + prefactor * (
            velocity_forcing_field_y[0, 0, 1]
            - velocity_forcing_field_y[0, 0, -1]
            - velocity_forcing_field_x[0, 1, 0]
            + velocity_forcing_field_x[0, -1, 0]
        )

    _update_vorticity_from_velocity_forcing_z_comp_kernel_3d = ps.create_kernel(
        _update_vorticity_from_velocity_forcing_z_comp_stencil_3d, config=kernel_config
    ).compile()

    def update_vorticity_from_velocity_forcing_pyst_kernel_3d(
        vorticity_field, velocity_forcing_field, prefactor
    ):
        """Kernel for updating vorticity based on velocity forcing in 3D.

        Updates vorticity_field based on velocity_forcing_field
        vorticity_field += prefactor * curl(velocity_forcing_field)
        prefactor: grid spacing factored out, along with any other multiplier
        Assumes velocity_forcing_field is (3, n, n).
        """
        _update_vorticity_from_velocity_forcing_x_comp_kernel_3d(
            vorticity_field_x=vorticity_field[0],
            velocity_forcing_field_y=velocity_forcing_field[1],
            velocity_forcing_field_z=velocity_forcing_field[2],
            prefactor=prefactor,
        )
        _update_vorticity_from_velocity_forcing_y_comp_kernel_3d(
            vorticity_field_y=vorticity_field[1],
            velocity_forcing_field_x=velocity_forcing_field[0],
            velocity_forcing_field_z=velocity_forcing_field[2],
            prefactor=prefactor,
        )
        _update_vorticity_from_velocity_forcing_z_comp_kernel_3d(
            vorticity_field_z=vorticity_field[2],
            velocity_forcing_field_x=velocity_forcing_field[0],
            velocity_forcing_field_y=velocity_forcing_field[1],
            prefactor=prefactor,
        )

    return update_vorticity_from_velocity_forcing_pyst_kernel_3d


def gen_update_vorticity_from_penalised_velocity_pyst_kernel_3d(
    real_t, num_threads=False, fixed_grid_size=False
):
    # TODO expand docs
    """Update vorticity based on penalised velocity in 3D kernel generator."""
    pyst_dtype = "float32" if real_t == np.float32 else "float64"
    kernel_config = ps.CreateKernelConfig(data_type=pyst_dtype, cpu_openmp=num_threads)
    # we can add dtype checks later
    grid_info = (
        f"{fixed_grid_size[0]}, {fixed_grid_size[1]}, {fixed_grid_size[2]}"
        if fixed_grid_size
        else "3D"
    )

    @ps.kernel
    def _update_vorticity_from_penalised_velocity_x_comp_stencil_3d():
        (vorticity_field_x, velocity_field_y, velocity_field_z,) = ps.fields(
            f"vorticity_field_x, velocity_field_y, "
            f"velocity_field_z : {pyst_dtype}[{grid_info}]"
        )
        (penalised_velocity_field_y, penalised_velocity_field_z,) = ps.fields(
            f"penalised_velocity_field_y, "
            f"penalised_velocity_field_z : {pyst_dtype}[{grid_info}]"
        )
        prefactor = sp.symbols("prefactor")
        # curl_x = df_z / dy - df_y / dz
        vorticity_field_x[0, 0, 0] @= vorticity_field_x[0, 0, 0] + prefactor * (
            penalised_velocity_field_z[0, 1, 0]
            - velocity_field_z[0, 1, 0]
            - penalised_velocity_field_z[0, -1, 0]
            + velocity_field_z[0, -1, 0]
            - penalised_velocity_field_y[1, 0, 0]
            + velocity_field_y[1, 0, 0]
            + penalised_velocity_field_y[-1, 0, 0]
            - velocity_field_y[-1, 0, 0]
        )

    _update_vorticity_from_penalised_velocity_x_comp_kernel_3d = ps.create_kernel(
        _update_vorticity_from_penalised_velocity_x_comp_stencil_3d,
        config=kernel_config,
    ).compile()

    @ps.kernel
    def _update_vorticity_from_penalised_velocity_y_comp_stencil_3d():
        (vorticity_field_y, velocity_field_x, velocity_field_z,) = ps.fields(
            f"vorticity_field_y, velocity_field_x,"
            f" velocity_field_z : {pyst_dtype}[{grid_info}]"
        )
        (penalised_velocity_field_x, penalised_velocity_field_z,) = ps.fields(
            f"penalised_velocity_field_x, "
            f"penalised_velocity_field_z : {pyst_dtype}[{grid_info}]"
        )
        prefactor = sp.symbols("prefactor")
        # curl_y = df_x / dz - df_z / dx
        vorticity_field_y[0, 0, 0] @= vorticity_field_y[0, 0, 0] + prefactor * (
            penalised_velocity_field_x[1, 0, 0]
            - velocity_field_x[1, 0, 0]
            - penalised_velocity_field_x[-1, 0, 0]
            + velocity_field_x[-1, 0, 0]
            - penalised_velocity_field_z[0, 0, 1]
            + velocity_field_z[0, 0, 1]
            + penalised_velocity_field_z[0, 0, -1]
            - velocity_field_z[0, 0, -1]
        )

    _update_vorticity_from_penalised_velocity_y_comp_kernel_3d = ps.create_kernel(
        _update_vorticity_from_penalised_velocity_y_comp_stencil_3d,
        config=kernel_config,
    ).compile()

    @ps.kernel
    def _update_vorticity_from_penalised_velocity_z_comp_stencil_3d():
        (vorticity_field_z, velocity_field_x, velocity_field_y,) = ps.fields(
            f"vorticity_field_z, velocity_field_x,"
            f" velocity_field_y : {pyst_dtype}[{grid_info}]"
        )
        (penalised_velocity_field_x, penalised_velocity_field_y,) = ps.fields(
            f"penalised_velocity_field_x, "
            f"penalised_velocity_field_y : {pyst_dtype}[{grid_info}]"
        )
        prefactor = sp.symbols("prefactor")
        # curl_z = df_y / dx - df_x / dy
        vorticity_field_z[0, 0, 0] @= vorticity_field_z[0, 0, 0] + prefactor * (
            penalised_velocity_field_y[0, 0, 1]
            - velocity_field_y[0, 0, 1]
            - penalised_velocity_field_y[0, 0, -1]
            + velocity_field_y[0, 0, -1]
            - penalised_velocity_field_x[0, 1, 0]
            + velocity_field_x[0, 1, 0]
            + penalised_velocity_field_x[0, -1, 0]
            - velocity_field_x[0, -1, 0]
        )

    _update_vorticity_from_penalised_velocity_z_comp_kernel_3d = ps.create_kernel(
        _update_vorticity_from_penalised_velocity_z_comp_stencil_3d,
        config=kernel_config,
    ).compile()

    def update_vorticity_from_penalised_velocity_kernel_3d(
        vorticity_field,
        penalised_velocity_field,
        velocity_field,
        prefactor,
    ):
        """Update vorticity based on penalised velocity kernel in 3D.

        Updates vorticity_field based on velocity_field and penalised_velocity_field
        vorticity_field += prefactor * curl(penalised_velocity_field - velocity_field)
        prefactor: grid spacing factored out, along with any other multiplier
        Assumes velocity_field is (3, n, n).
        """
        _update_vorticity_from_penalised_velocity_x_comp_kernel_3d(
            vorticity_field_x=vorticity_field[0],
            penalised_velocity_field_y=penalised_velocity_field[1],
            penalised_velocity_field_z=penalised_velocity_field[2],
            velocity_field_y=velocity_field[1],
            velocity_field_z=velocity_field[2],
            prefactor=prefactor,
        )
        _update_vorticity_from_penalised_velocity_y_comp_kernel_3d(
            vorticity_field_y=vorticity_field[1],
            penalised_velocity_field_x=penalised_velocity_field[0],
            penalised_velocity_field_z=penalised_velocity_field[2],
            velocity_field_x=velocity_field[0],
            velocity_field_z=velocity_field[2],
            prefactor=prefactor,
        )
        _update_vorticity_from_penalised_velocity_z_comp_kernel_3d(
            vorticity_field_z=vorticity_field[2],
            penalised_velocity_field_x=penalised_velocity_field[0],
            penalised_velocity_field_y=penalised_velocity_field[1],
            velocity_field_x=velocity_field[0],
            velocity_field_y=velocity_field[1],
            prefactor=prefactor,
        )

    return update_vorticity_from_penalised_velocity_kernel_3d
