#!/usr/bin/env python3

import json
import os
import sys
import re
import subprocess as sp
import flywheel

from utils import args, results, log

if __name__ == '__main__':
    context = flywheel.GearContext()
    context.log = log.get_custom_logger('[flywheel:fsl-stats]')
