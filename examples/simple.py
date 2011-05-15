import fuse
from stat import S_IRUSR, S_IXUSR, S_IWUSR, S_IRGRP, S_IXGRP, S_IXOTH, S_IROTH

from fs import FS, BaseMetadata


fs = FS.get()

@fs.route('/')
class Root(object):
    def __init__(self):
        root_mode = S_IRUSR|S_IXUSR|S_IWUSR|S_IRGRP|S_IXGRP|S_IXOTH|S_IROTH
        self.dir_metadata = BaseMetadata(root_mode, True)

    def getattr(self, *args, **kwargs):
        return self.dir_metadata

    def readdir(self, *args, **kwargs):
        yield fuse.Direntry('eval')
        for i in xrange(4):
            yield fuse.Direntry('test%s' % i)


@fs.route('/<filepath>')
class Files(object):
    def __init__(self):
        file_mode = S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH
        self.file_metadata = BaseMetadata(file_mode, False)

    def getattr(self, *args, **kwargs):
        data = kwargs['filepath']
        self.file_metadata.st_size = len(data*4)
        return self.file_metadata

    def read(self, size, offset, *args, **kwargs):
        data = kwargs['filepath']*4
        return data[offset:size+offset]
