"""
Ocropus's magic PIL-numpy array conversion routines. They express slightly
different behavior from PIL.Image.toarray() but the reason is rather
mysterious.
"""

from __future__ import absolute_import, division, print_function
from future import standard_library
from future.utils import PY2
standard_library.install_aliases()

import numpy as np

from PIL import Image


def pil2array(im, alpha=0):
    if im.mode == "L":
        a = np.fromstring(im.tobytes(), 'B')
        a.shape = im.size[1], im.size[0]
        return a
    if im.mode == "RGB":
        a = np.fromstring(im.tobytes(), 'B')
        a.shape = im.size[1], im.size[0], 3
        return a
    if im.mode == "RGBA":
        a = np.fromstring(im.tobytes(), 'B')
        a.shape = im.size[1], im.size[0], 4
        if not alpha:
            a = a[:, :, :3]
        return a
    return pil2array(im.convert("L"))


def array2pil(a):
    if a.dtype == np.dtype("B"):
        if a.ndim == 2:
            return Image.frombytes("L", (a.shape[1], a.shape[0]),
                                   a.tostring())
        elif a.ndim == 3:
            return Image.frombytes("RGB", (a.shape[1], a.shape[0]),
                                   a.tostring())
        else:
            raise Exception("bad image rank")
    elif a.dtype == np.dtype('float32'):
        return Image.frombytes("F", (a.shape[1], a.shape[0]), a.tostring())
    else:
        raise Exception("unknown image type")

def is_bitonal(im):
    """
    Tests a PIL.Image for bitonality.

    Args:
        im (PIL.Image): Image to test

    Returns:
        True if the image contains only two different color values. False
        otherwise.
    """
    if im.getcolors(2):
        return True
    else:
        return False

def get_im_str(im):
    if PY2:
        return im.filename.decode('utf-8') if hasattr(im, 'filename') else str(im)
    else:
        return im.filename if hasattr(im, 'filename') else str(im)

