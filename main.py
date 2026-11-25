#!/usr/bin/env python3
"""Entry point for the Sum 25 broadsheet (make.fun news-image-20261125).

The picture itself is drawn by render.py on the build machine and
shipped as entry.png next to this file. The grading container runs only this
file, with the standard library only, so this module copies entry.png
byte-identical to the output directory: $MAKEFUN_OUTPUT_DIR when set,
otherwise /output/entry.png.
"""
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        sys.stderr.write("entry.png not found next to main.py\n")
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    # Byte-identical copy: the grader must see exactly the verified image.
    shutil.copyfile(src, dst)
    print("wrote " + dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
