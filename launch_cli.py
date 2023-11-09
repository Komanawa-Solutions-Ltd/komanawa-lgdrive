"""
created matt_dumont 
on: 9/11/23
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
import fire
from utils.util_functions import LGDrive
import os
os.environ["PAGER"] = "cat"
if __name__ == '__main__':

    fire.Fire(LGDrive())