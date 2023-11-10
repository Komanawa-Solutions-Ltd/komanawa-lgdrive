"""
created matt_dumont 
on: 9/11/23
"""

import fire
from lgdrive.utils.util_functions import LGDrive
import os

os.environ["PAGER"] = "cat"
if __name__ == '__main__':
    fire.Fire(LGDrive())
