# -*- coding: utf-8 -*-
"""Module of commonly use python objects

**Disclaimer**

Copyright (C) 2018-2019  Philipp S. Sommer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
import asyncio
import logging
from functools import wraps

from docrep import DocstringProcessor

docstrings = DocstringProcessor()


def rgba2rgb(image, color=(255, 255, 255)):
    """Alpha composite an RGBA Image with a specified color.

    Source: http://stackoverflow.com/a/9459208/284318

    Parameters
    ----------
    image: PIL.Image
        The PIL RGBA Image object
    color: tuple
        The rgb color for the background

    Returns
    -------
    PIL.Image
        The rgb image
    """
    from PIL import Image
    image.load()  # needed for split()
    background = Image.new('RGB', image.size, color)
    background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
    return background


def nearest_index_position(index, value):
    """Return the integer position of the nearest numeric index entry."""
    if not len(index):
        raise KeyError(value)
    position = index.get_indexer([value], method='nearest')[0]
    if position < 0:
        raise KeyError(value)
    return int(position)


def nearest_index_value(index, value):
    """Return the nearest numeric value from a pandas-like index."""
    return index[nearest_index_position(index, value)]


def ensure_asyncio_event_loop():
    """Return a usable event loop for GUI startup on modern Python versions.

    Python 3.14 no longer creates a default event loop implicitly for the
    main thread, but psyplot-gui still expects ``asyncio.get_event_loop()``
    to succeed during console initialization.
    """
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def patch_psyplot_gui_asyncio():
    """Patch psyplot-gui's console startup for Python 3.14+ on Windows.

    psyplot-gui resets the Windows asyncio policy during console startup.
    On Python 3.14 that policy switch leaves the main thread without a current
    loop, so the subsequent ``asyncio.gather(...)`` call fails immediately.
    """
    try:
        import psyplot_gui.console as console
    except ImportError:
        return False

    original = console.init_asyncio_patch
    if getattr(original, '_straditize_patched', False):
        return True

    @wraps(original)
    def wrapped(*args, **kwargs):
        ret = original(*args, **kwargs)
        ensure_asyncio_event_loop()
        return ret

    wrapped._straditize_patched = True
    console.init_asyncio_patch = wrapped
    return True


def patch_psyplot_gui_entrypoints():
    """Use importlib.metadata entry points for modern psyplot-gui sessions."""
    try:
        from importlib import metadata
        from psyplot_gui.config.rcsetup import GuiRcParams
    except ImportError:
        return False

    original = GuiRcParams._load_plugin_entrypoints
    if getattr(original, '_straditize_patched', False):
        return True

    class _CompatEntryPoint(object):
        def __init__(self, entry_point):
            self._entry_point = entry_point
            self.name = entry_point.name
            self.value = entry_point.value
            self.group = entry_point.group
            self.module = entry_point.module
            self.module_name = entry_point.module
            self.attrs = (
                [] if entry_point.attr is None else entry_point.attr.split('.'))

        def load(self):
            return self._entry_point.load()

        def __str__(self):
            return str(self._entry_point)

    @wraps(original)
    def wrapped(self):
        inc = self["plugins.include"]
        exc = self["plugins.exclude"]
        logger = logging.getLogger('psyplot_gui.config.rcsetup')
        self._plugins = self._plugins or []
        for raw_ep in metadata.entry_points(group='psyplot_gui'):
            ep = _CompatEntryPoint(raw_ep)
            plugin_name = "%s:%s:%s" % (
                ep.module, ":".join(ep.attrs), ep.name)
            include_user = None
            if inc:
                include_user = (
                    ep.module in inc
                    or ep.name in inc
                    or "%s:%s" % (ep.module, ":".join(ep.attrs)) in inc
                )
            if include_user is None and exc == 'all':
                include_user = False
            elif include_user is None:
                include_user = not (
                    ep.module in exc
                    or ep.name in exc
                    or "%s:%s" % (ep.module, ":".join(ep.attrs)) in exc
                )
            if not include_user:
                logger.debug(
                    "Skipping plugin %s: Excluded by user", plugin_name)
            else:
                logger.debug("Loading plugin %s", plugin_name)
                self._plugins.append(str(ep))
                yield ep

    wrapped._straditize_patched = True
    GuiRcParams._load_plugin_entrypoints = wrapped
    return True
