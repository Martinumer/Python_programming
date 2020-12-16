import datetime
import os
import pathlib
import stat
import time
import typing as tp

from pyvcs.index import GitIndexEntry, read_index  # type: ignore
from pyvcs.objects import hash_object  # type: ignore
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref  # type: ignore


def write_tree(gitdir: pathlib.Path, index: tp.List[GitIndexEntry], dirname: str = "") -> str:
    tree_inputs = []
    for entry in index:
        _, title = os.path.split(entry.name)
        if dirname:
            titles = dirname.split("/")
        else:
            titles = entry.name.split("/")
        if len(titles) != 1:
            prefix = titles[0]
            title = f"/".join(titles[1:])
            mode = "40000"
            tree_input = f"{mode} {prefix}\0".encode()
            tree_input += bytes.fromhex(write_tree(gitdir, index, title))
            tree_inputs.append(tree_input)
        else:
            if dirname and entry.name.find(dirname) == -1:
                continue
            with open(entry.name, "rb") as file:
                info = file.read()
            mode = str(oct(entry.mode))[2:]
            tree_input = f"{mode} {title}\0".encode()
            tree_input += bytes.fromhex(hash_object(info, "blob", write=True))
            tree_inputs.append(tree_input)

    tree_binary = b"".join(tree_inputs)
    return hash_object(tree_binary, "tree", write=True)


def commit_tree(
    gitdir: pathlib.Path,
    tree: str,
    message: str,
    parent: tp.Optional[str] = None,
    author: tp.Optional[str] = None,
) -> str:
    now = int(time.mktime(time.localtime()))
    timezone = time.timezone
    if timezone > 0:
        formatted_timezone = "-"
    else:
        formatted_timezone = "+"
    formatted_timezone += f"{abs(timezone) // 3600:02}{abs(timezone) // 60 % 60:02}"
    commit_content = []
    commit_content.append(f"tree {tree}")
    if parent:
        commit_content.append(f"parent {parent}")
    if not author:
        author = f"{os.getenv('GIT_AUTHOR_NAME')} <{os.getenv('GIT_AUTHOR_EMAIL')}"
        commit_content.append(f"committer {author} {now} {formatted_timezone}")
        commit_content.append(f"author {author} {now} {formatted_timezone}")
    commit_content.append(f"\n{message}\n")
    data = "\n".join(commit_content).encode()
    return hash_object(data, "commit", write=True)
