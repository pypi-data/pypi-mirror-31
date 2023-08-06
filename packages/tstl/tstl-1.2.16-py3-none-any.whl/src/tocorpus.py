from __future__ import print_function

import random
import struct
import time
import sys
import os

# Appending current working directory to sys.path
# So that user can run randomtester from the directory where sut.py is located
current_working_dir = os.getcwd()
sys.path.append(current_working_dir)

import sut as SUT

def main():
    if "--help" in sys.argv:
        print("Usage:  tstl_toafl <outputdir> <files>")
        sys.exit(0)

    sut = SUT.sut()

    outputDir = sys.argv[1]
    files = sys.argv[2:]

    acts = sut.actions()

    i = 0
    for f in files:
        t = sut.loadTest(f)
        sut.saveTest(t,outputDir+"/"+os.path.basename(f)+".afl",afl=True)
        i += 1


