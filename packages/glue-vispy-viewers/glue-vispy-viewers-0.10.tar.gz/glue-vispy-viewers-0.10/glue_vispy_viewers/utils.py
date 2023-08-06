from __future__ import absolute_import, division, print_function

import numpy as np

from glue_vispy_viewers.extern.vispy.visuals.transforms import (ChainTransform, NullTransform,
                                                                MatrixTransform, STTransform)
from glue_vispy_viewers.extern.vispy.visuals.transforms.base_transform import InverseTransform


def as_matrix_transform(transform):
    """
    Simplify a transform to a single matrix transform, which makes it a lot
    faster to compute transformations.

    Raises a TypeError if the transform cannot be simplified.
    """
    if isinstance(transform, ChainTransform):
        matrix = np.identity(4)
        for tr in transform.transforms:
            # We need to do the matrix multiplication manually because VisPy
            # somehow doesn't mutliply matrices if there is a perspective
            # component. The equation below looks like it's the wrong way
            # around, but the VisPy matrices are transposed.
            matrix = np.matmul(as_matrix_transform(tr).matrix, matrix)
        return MatrixTransform(matrix)
    elif isinstance(transform, InverseTransform):
        matrix = as_matrix_transform(transform._inverse)
        return MatrixTransform(matrix.inv_matrix)
    elif isinstance(transform, NullTransform):
        return MatrixTransform()
    elif isinstance(transform, STTransform):
        return transform.as_matrix()
    elif isinstance(transform, MatrixTransform):
        return transform
    else:
        raise TypeError("Could not simplify transform of type {0}".format(type(transform)))


try:

    from glue.utils.qt import fix_tab_widget_fontsize  # noqa

except ImportError:

    import platform
    from glue.utils.qt import get_qapp

    def fix_tab_widget_fontsize(tab_widget):
        """
        Because of a bug in Qt, tab titles on MacOS X don't have the right font size
        """
        if platform.system() == 'Darwin':
            app = get_qapp()
            app_font = app.font()
            tab_widget.setStyleSheet('font-size: {0}px'.format(app_font.pointSize()))
