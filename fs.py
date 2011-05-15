#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import functools

from stat import S_IFDIR, S_IFREG

import fuse

fuse.fuse_python_api = (0, 2)

from routing import Rule

from util import Singleton


class BaseMetadata(fuse.Stat):
    def __init__(self, mode, is_dir):
        fuse.Stat.__init__(self)

        if is_dir:
            self.st_mode = S_IFDIR | mode
            self.st_nlink = 2
        else:
            self.st_mode = S_IFREG | mode
            self.st_nlink = 1

        now = int(time.time())
        self.st_atime = now
        self.st_mtime = now
        self.st_ctime = now
        self.st_uid   = os.getuid()
        self.st_gid   = os.getgid()
        self.st_size  = 0


_attrs = ['getattr', 'readlink', 'readdir', 'mkdir',
          'unlink', 'rmdir', 'symlink', 'rename', 'link', 'chmod',
          'chown', 'truncate', 'open', 'read', 'write', 'release',
          'fsync', 'create', 'opendir', 'releasedir', 'fsyncdir',
          'flush', 'fgetattr', 'ftruncate', 'access']

class FS(fuse.Fuse, Singleton):
    def __init__(self, *args, **kw):
        Singleton.__init__(self)
        self._kache = {}
        self._paths = []
        for attr in _attrs:
            setattr(self, attr, self.wrapper(attr))
        fuse.Fuse.__init__(self, *args, **kw)

    def wrapper(self, func):
        def funcwrap(path, *args, **kwargs):
            for rule, instance in self._paths:
                match = rule.match(path)
                if match is not None:
                    match.update(kwargs)
                    if hasattr(instance, func):
                        return getattr(instance, func)(*args, **match)
                    if func == 'fgetattr' and hasattr(instance, 'getattr'):
                        return getattr(instance, 'getattr')(*args, **match)

                    return 0
            return 0
        return funcwrap

    def route(self, path):
        def deco(klass):
            if klass not in self._kache:
                self._kache[klass] = klass()
            self._paths.append((Rule(path), self._kache[klass]))
            return klass
        return deco
