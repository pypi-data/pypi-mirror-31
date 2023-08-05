"""
Visualization
~~~~~~~~~~~~~

Common functions for visualization.
"""
import bohrium as np
from . import ufuncs, bhary, array_create


def plot_surface(ary, mode, colormap, lowerbound, upperbound):
    mode = mode.lower()

    ranks = [2, 3]
    modes = ["2d", "3d"]
    types = [np.float32]

    if not (ary.ndim == 2 or ary.ndim == 3):
        raise ValueError("Unsupported array-rank, must be one of %s" % ranks)
    if mode not in modes:
        raise ValueError("Unsupported mode, must be one of %s" % modes)

    if ary.dtype not in types:
        ary = array_create.array(ary, bohrium=True, dtype=np.float32)

    if mode == "2d":
        flat = True
        cube = False
    elif mode == "3d":
        if ary.ndim == 2:
            flat = False
            cube = False
        else:
            flat = False
            cube = True
    else:
        raise ValueError("Unsupported mode '%s' " % mode)

    if bhary.check(ary):  # Must be a Bohrium array
        ary = array_create.array(ary)

    args = array_create.array([  # Construct arguments
        np.float32(colormap),
        np.float32(flat),
        np.float32(cube),
        np.float32(lowerbound),
        np.float32(upperbound)
    ],
        bohrium=True
    )
    ufuncs.extmethod("visualizer", ary, args, ary)  # Send to extension
