#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:et:ts=4:sw=4:cc=73,80

import re
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).absolute().parents[1]
TOP_LIST_PATH = REPO_ROOT / "CMakeLists.txt"


def main():
    contents = TOP_LIST_PATH.read_text(encoding='utf-8')
    files = []
    matches = re.findall(
        r'^#\[(=+)\[([\w.]+)\[[\s]*?$\n((?:.|\n)*?)^#\]\2\]\1\]',
        contents,
        re.MULTILINE)
    for _, name, content in matches:
        files.append(name)
        file = REPO_ROOT / name
        file.write_text(content, encoding='utf-8', newline='\n')
    subprocess.run(['git', 'add', '--'] + files, check=True, cwd=REPO_ROOT)
    print("Updated:", ", ".join(files))
    print("Check the diff by the command: git diff --cached")


if __name__ == "__main__":
    main()
