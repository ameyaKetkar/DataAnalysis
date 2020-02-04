from Models.Models.CommitInfo_pb2 import CommitInfo
from Models.Models.Project_pb2 import Project
from os.path import join as join
from os.path import dirname as parent
from os.path import realpath as realPath


def readFile(filename):
    try:
        filehandle = open(filename)
        s = filehandle.read()
        filehandle.close()
        return s
    except:
        print(filename,  ' Not found')
        return ''

fileDir = parent(parent(parent(realPath('__file__'))))
pathToProtos = join(fileDir, 'TypeChangeMiner/Input/ProtosOut/')


def readAll(fileName, kind):
    sizes = list(map(lambda s: int(s),filter(lambda s: s != '', readFile(join(pathToProtos, fileName + 'BinSize.txt')).split(" "))))
    buf = join(pathToProtos, fileName + '.txt')
    l = []
    with open(buf, 'rb') as f:
        buf = f.read()
        n = 0
        for s in sizes:
            msg_buf = buf[n:n+s]
            n += s
            c = None
            if kind == "Commit":
                c = CommitInfo()
            if kind == "Project":
                c = Project()
            if c is not None:
                c.ParseFromString(msg_buf)
                l.append(c)
        return l





