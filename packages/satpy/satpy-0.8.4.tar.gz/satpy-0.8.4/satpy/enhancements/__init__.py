#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017.

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This file is part of satpy.

# satpy is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# satpy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# satpy.  If not, see <http://www.gnu.org/licenses/>.

"""Enhancements."""

import numpy as np
import logging

LOG = logging.getLogger(__name__)


def stretch(img, **kwargs):
    """Perform stretch."""
    img.stretch(**kwargs)


def gamma(img, **kwargs):
    """Perform gamma correction."""
    img.gamma(**kwargs)


def invert(img, *args):
    """Perform inversion."""
    img.invert(*args)


def cira_stretch(img, **kwargs):
    """Logarithmic stretch adapted to human vision.

    Applicable only for visible channels.
    """
    LOG.debug("Applying the cira-stretch")
    for chn in img.channels:
        chn /= 100
        np.log10(chn.data, out=chn.data)
        chn -= np.log10(0.0223)
        chn /= 1.0 - np.log10(0.0223)
        chn /= 0.75


def lookup(img, **kwargs):
    """Assign values to channels based on a table."""
    luts = np.array(kwargs['luts'], dtype=np.float32) / 255.0

    for idx, ch in enumerate(img.channels):
        np.ma.clip(ch, 0, 255, out=ch)
        img.channels[idx] = np.ma.array(
            luts[:, idx][ch.astype(np.uint8)], copy=False, mask=ch.mask)


def colorize(img, **kwargs):
    """Colorize the given image."""
    full_cmap = _merge_colormaps(kwargs)
    img.colorize(full_cmap)


def palettize(img, **kwargs):
    """Palettize the given image (no color interpolation)."""
    full_cmap = _merge_colormaps(kwargs)
    img.palettize(full_cmap)


def _merge_colormaps(kwargs):
    """Merge colormaps listed in kwargs."""
    full_cmap = None

    for itm in kwargs["palettes"]:
        cmap = create_colormap(itm)
        cmap.set_range(itm["min_value"], itm["max_value"])
        if full_cmap is None:
            full_cmap = cmap
        else:
            full_cmap = full_cmap + cmap

    return full_cmap


def create_colormap(palette):
    """Create colormap of the given numpy file, color vector or colormap."""
    from trollimage.colormap import Colormap
    fname = palette.get('filename', None)
    if fname:
        data = np.load(fname)
        cmap = []
        num = 1.0 * data.shape[0]
        for i in range(int(num)):
            cmap.append((i / num, (data[i, 0] / 255., data[i, 1] / 255.,
                                   data[i, 2] / 255.)))
        return Colormap(*cmap)

    colors = palette.get('colors', None)
    if isinstance(colors, list):
        cmap = []
        values = palette.get('values', None)
        for idx, color in enumerate(colors):
            if values:
                value = values[idx]
            else:
                value = idx / float(len(colors) - 1)
            cmap.append((value, tuple(color)))
        return Colormap(*cmap)

    if isinstance(colors, basestring):
        from trollimage import colormap
        import copy
        return copy.copy(getattr(colormap, colors))

    return None


def three_d_effect(img, **kwargs):
    """Create 3D effect using convolution"""
    from scipy.signal import convolve2d
    LOG.debug("Applying 3D effect")
    kernel = np.array([[-1, 0, 1],
                       [-1, 1, 1],
                       [-1, 0, 1]])

    for i in range(len(img.channels)):
        mask = img.channels[i].mask
        img.channels[i] = np.ma.masked_where(mask,
                                             convolve2d(img.channels[i],
                                                        kernel, mode='same'))
