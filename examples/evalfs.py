import sys
import traceback

from stat import S_IRUSR, S_IXUSR, S_IWUSR, S_IRGRP, S_IXGRP, S_IXOTH, S_IROTH
from errno import ENOENT

import fuse

from fs import FS, BaseMetadata

fs = FS.get()

class Out(object):
    def __init__(self):
        self.out = ''

    def write(self, data):
        self.out += data

    def read(self):
        return self.out

def evalcode(code):
    old_stdout = sys.stdout
    try:
        new_stdout =  Out()
        sys.stdout = new_stdout
        eval(compile(code, "<eval>", "exec"))
        return new_stdout.read()
    except:
        error = traceback.format_exc().strip().split("\n")[-1]
        return error
    finally:
        sys.stdout = old_stdout


@fs.route('/eval')
@fs.route('/eval/<filepath>.py')
class Eval(object):
    def __init__(self):
        file_mode = S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH
        self.file_metadata = BaseMetadata(file_mode, False)

        root_mode = S_IRUSR|S_IXUSR|S_IWUSR|S_IRGRP|S_IXGRP|S_IXOTH|S_IROTH
        self.dir_metadata = BaseMetadata(root_mode, True)

        self.files = {}

    def create(self, *args, **kwargs):
        self.files[kwargs['filepath']] = ''
        return 0

    def open(self, flags, **kwargs):
        return 0

    def getattr(self, *args, **kwargs):
        if 'filepath' in kwargs:
            data = kwargs['filepath']
            if data not in self.files:
                return -ENOENT
            data = evalcode(self.files[data])
            self.file_metadata.st_size = len(data)
            return self.file_metadata
        return self.dir_metadata

    def readdir(self, *args, **kwargs):
        for i in self.files:
            yield fuse.Direntry('%s.py' % i)

    def read(self, size, offset, *args, **kwargs):
        key = kwargs['filepath']
        data = evalcode(self.files[key])
        return data[offset:size+offset]

    def write(self, buf, offset, fh=None, **kwargs):
        key = kwargs['filepath']

        prev_data = self.files[key]
        new_data = prev_data[:offset] + buf + prev_data[offset+len(buf):]

        if offset + len(new_data) > len(prev_data):
            self.truncate(offset + len(new_data), filepath=key)

        self.files[key] = new_data
        return len(buf)

    def truncate(self, size, fh=None, **kwargs):
        key = kwargs['filepath']

        prev_data = self.files[key]
        prev_size = len(prev_data)

        if size > prev_size:
            new_data = prev_data + (size - prev_size)*"0"
        else:
            new_data = prev_data[0:size]

        self.files[key] = new_data
