import os
import pathlib
import typing as tp


def repo_find(workdir: tp.Union[str, pathlib.Path] = ".") -> pathlib.Path:
    name = os.environ.get("GIT_DIR", ".git")
    workdir = pathlib.Path(workdir).absolute()
    next_dir = workdir
    flag = False
    while next_dir != os.path.abspath(".").split(os.path.sep)[0] + os.path.sep:
        ls = os.listdir(next_dir)
        if name in ls:
            flag = True
            way = str(next_dir) + os.path.sep + name
            return pathlib.Path(way).absolute()
        next_dir = os.path.split(next_dir)[0]
    if not flag:
        raise Exception0("Not a git repository")


class Exception0(Exception):
    def __init__(self, text):
        self.txt = text


def repo_create(workdir: tp.Union[str, pathlib.Path]) -> pathlib.Path:
    workdir = pathlib.Path(workdir)
    if os.path.isfile(workdir):
        raise Exception0(f"{workdir} is not a directory")
    elif not os.path.exists(workdir):
        raise Exception0("Not a git repository")
    name = os.environ.get("GIT_DIR", ".git")
    gitdir = workdir / name
    gitdir.mkdir(parents=True)
    nextdir = gitdir / "HEAD"
    f = open(nextdir, "w")
    f.write("ref: refs/heads/master\n")
    f.close()
    nextdir = gitdir / "config"
    f = open(nextdir, "w")
    f.write(
        "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = false\n"
    )
    f.close()
    nextdir = gitdir / "description"
    f = open(nextdir, "w")
    f.write("Unnamed pyvcs repository.\n")
    f.close()
    nextdir = gitdir / "objects"
    nextdir.mkdir()
    nextdir = gitdir / "refs" / "heads"
    nextdir.mkdir(parents=True)
    nextdir = gitdir / "refs" / "tags"
    nextdir.mkdir(parents=True)
    return gitdir
