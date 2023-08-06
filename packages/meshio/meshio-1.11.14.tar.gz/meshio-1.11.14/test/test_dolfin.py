# -*- coding: utf-8 -*-
#
import numpy
import pytest

import meshio

import helpers


@pytest.mark.parametrize('mesh', [
    helpers.tri_mesh,
    helpers.tet_mesh,
    helpers.add_cell_data(helpers.tri_mesh, 1, dtype=float),
    helpers.add_cell_data(helpers.tri_mesh, 1, dtype=numpy.int32),
    ])
def test_io(mesh):
    helpers.write_read(
        meshio.dolfin_io.write,
        meshio.dolfin_io.read,
        mesh, 1.0e-15
        )
    return
