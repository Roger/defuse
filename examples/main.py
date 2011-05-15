import sys
sys.path.insert(0, '../')
from fs import FS
import evalfs, simple

fs = FS.get()

if __name__ == '__main__':
    fs.parse(values=fs, errex=1)
    fs.main()
