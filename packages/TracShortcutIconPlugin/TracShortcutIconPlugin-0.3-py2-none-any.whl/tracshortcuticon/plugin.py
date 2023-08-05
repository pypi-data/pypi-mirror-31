# -*- coding: utf-8 -*-
""" Copyright (c) 2008 Martin Scharrer <martin@scharrer-online.de>
    $Id: plugin.py 17135 2018-04-16 19:44:04Z rjollos $
    $HeadURL: https://trac-hacks.org/svn/shortcuticonplugin/0.11/tracshortcuticon/plugin.py $

    This is Free Software under the GPL v3!
"""

import os
from trac.core import Component, implements
from trac.web.api import IRequestHandler, IRequestFilter, RequestDone
from trac.web.chrome import add_link
from trac.config import Option, BoolOption
try:  # PathOption exists only since Trac 0.11.5
    from trac.config import PathOption
except:
    from trac.config import Option as PathOption


class ShortcutIconRequestPlugin(Component):
    """Implements the /favicon.ico handler."""
    implements(IRequestFilter, IRequestHandler)

    iconpath = PathOption('shortcuticon', 'iconpath', None,
                          "Filesystem path of shortcut icon")

    _mimetype = Option('shortcuticon', 'mimetype', None,
                       "Mimetype of shortcut icon")

    ishandler = BoolOption('shortcuticon', 'handler',
                           True, "Handler for '/favicon.ico'")

    isfilter = BoolOption('shortcuticon', 'linkheader', ishandler,
                          "Add 'link' tags for icon into HTML pages")

    path = r'/favicon.ico'

    exttypes = {
        '.ico': 'image/x-icon',
        '.png': 'image/png',
        '.jpg': 'image/jpg',
        '.gif': 'image/gif',
    }

    def __init__(self):
        if self._mimetype:
            self.mimetype = self._mimetype
        else:
            try:
                iconpath = self.iconpath
                idx = iconpath.rindex('.', -4)
                self.mimetype = self.exttypes[iconpath[idx:]]
                self.mimetype = 'image/x-icon'
            except:
                self.mimetype = 'image/x-icon'

    # IRequestHandler methods

    def match_request(self, req):
        if not self.ishandler:
            return False
        return req.path_info == self.path \
            or req.path_info == req.base_path + self.path

    def process_request(self, req):
        iconpath = self.iconpath
        iconok = False
        if iconpath:
            if os.path.isfile(iconpath) and os.access(iconpath, os.R_OK):
                iconok = True
            else:
                self.log.warning(
                    "Icon '%s' isn't a readable file!", iconpath)
        else:
            self.log.warning("No icon file configured!")

        if iconok:
            req.send_file(self.iconpath, self.mimetype)
        else:
            req.send_response(404)
            req.end_headers()
        raise RequestDone

    # IRequestFilter methods

    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, data, content_type):
        if self.isfilter:
            path = req.base_path + self.path
            add_link(req, 'shortcut icon', path, None, self.mimetype)
            add_link(req, 'icon', path, None, self.mimetype)

        return template, data, content_type
