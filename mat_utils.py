import numpy as np


"""
Code from pytransform3d.rotations
"""

def active_matrix_from_angle(basis, angle):
    r"""Compute active rotation matrix from rotation about basis vector.

    With the angle :math:`\alpha` and :math:`s = \sin{\alpha}, c=\cos{\alpha}`,
    we construct rotation matrices about the basis vectors as follows:

    .. math::

        \boldsymbol{R}_x(\alpha) =
        \left(
        \begin{array}{ccc}
        1 & 0 & 0\\
        0 & c & -s\\
        0 & s & c
        \end{array}
        \right)

    .. math::

        \boldsymbol{R}_y(\alpha) =
        \left(
        \begin{array}{ccc}
        c & 0 & s\\
        0 & 1 & 0\\
        -s & 0 & c
        \end{array}
        \right)

    .. math::

        \boldsymbol{R}_z(\alpha) =
        \left(
        \begin{array}{ccc}
        c & -s & 0\\
        s & c & 0\\
        0 & 0 & 1
        \end{array}
        \right)

    Parameters
    ----------
    basis : int from [0, 1, 2]
        The rotation axis (0: x, 1: y, 2: z)

    angle : float
        Rotation angle

    Returns
    -------
    R : array, shape (3, 3)
        Rotation matrix

    Raises
    ------
    ValueError
        If basis is invalid
    """
    c = np.cos(angle)
    s = np.sin(angle)

    if basis == 0:
        R = np.array([[1.0, 0.0, 0.0],
                      [0.0, c, -s],
                      [0.0, s, c]])
    elif basis == 1:
        R = np.array([[c, 0.0, s],
                      [0.0, 1.0, 0.0],
                      [-s, 0.0, c]])
    elif basis == 2:
        R = np.array([[c, -s, 0.0],
                      [s, c, 0.0],
                      [0.0, 0.0, 1.0]])
    else:
        raise ValueError("Basis must be in [0, 1, 2]")

    return R


def active_matrix_from_extrinsic_euler(e, order=[0,1,2]):
    """Compute active rotation matrix from extrinsic Cardan angles.

    Parameters
    ----------
    e : array-like, shape (3,)
        Angles for rotation around x-, y-, and z-axes (extrinsic rotations)

    Returns
    -------
    R : array, shape (3, 3)
        Rotation matrix
    """
    alpha, beta, gamma = e
    R = active_matrix_from_angle(order[2], gamma).dot(
        active_matrix_from_angle(order[1], beta)).dot(
        active_matrix_from_angle(order[0], alpha))
    return R


def matrix_from_euler(e, rotation_order='xyz', degrees=False):
    assert len(rotation_order) == 3
    assert all([r in 'xyz' for r in rotation_order.lower()])

    if degrees:
        e = np.radians(e)

    angles = {'x':0,'y':1,'z':2}
    order = [angles[r] for r in rotation_order.lower()]
    return active_matrix_from_extrinsic_euler(e, order)