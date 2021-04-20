#!/usr/bin/env python3

import json
import os
import sys
import re
import subprocess as sp
import flywheel

from utils import args, log

if __name__ == "__main__":
    context = flywheel.GearContext()
    context.log = log.get_custom_logger("[flywheel:fsl-stats]")

    # grab environment for gear
    with open('/tmp/gear_environ.json', "r") as f:
        environ = json.load(f)
    context.custom_dict ={}
    context.custom_dict["environ"] = environ

    try:
        args.handleMultiImgs(context)
        args.parseParams(context)
        args.validate(context)
        args.execute(context)

        context.log.info("Commands successfully executed!")
        os.sys.exit(0)

    except Exception as e:
        context.log.error(e)
        context.log.error('Cannot execute fslstats command.')
        os.sys.exit(1)
