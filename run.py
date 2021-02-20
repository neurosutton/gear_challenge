#!/usr/bin/env python3

import json
import os
import sys
import re
import subprocess as sp
import flywheel

context = flywheel.GearContext()

# grab environment for gear
with open('/tmp/gear_environ.json', 'r') as f:
    environ = json.load(f)

# This gear will use a "custom_dict" dictionary as a custom-user field 
# on the gear context.
context.custom_dict ={}

context.custom_dict['environ'] = environ

# Grab the primary image
context.custom_dict['input_image'] = context.get_input("input_image")['location']['name']

# If secondary images are provided, grab the inputs
if context.get_input("mask_image"):
    context.custom_dict['mask_image'] = context.get_input("mask_image")['location']['name']
if context.get_input("difference_image"):
    context.custom_dict['difference_image'] = context.get_input("difference_image")['location']['name']

#########################################
# NOTE: Adapted from fsl-anat/utils/args.py
# Build a dictionary of key:value command-line parameter names:values
# These will be validated and assembled into a command-line below.
config = context.config
params = {}
for key in config.keys():
    # Use only those boolean values that are True
    if type(config[key]) == bool:
        if config[key]:
            params[key] = True
    else:
        # if the key-value is zero, we skip and use the defaults
        if config[key] != 0 and config[key] != '':
            params[key] = config[key]
context.custom_dict['params'] = params
########################################

# Base command
command=['fslstats']

# Add a pre-option of splitting a timeseries
if '-t' in context.custom_dict['params']['function_options']:
    command.append('-t')
    context.custom_dict['params']['function_options'] = context.custom_dict['params']['function_options'].replace('-t','')

# Add main image
command.append(context.custom_dict['input_image'])

# Add any subsequent image file options
if 'mask_image' in context.custom_dict:
    command.extend(['-k', context.custom_dict['mask_image']])
if 'difference_image' in context.custom_dict:
    command.extend(['-d', context.custom_dict['difference_image']])

custom_tag_dict = {'upper_threshold':'-u',
                    'lower_threshold': '-l',
                    'output_nth_percentile':'-p',
                    'output_nth_percentile_nonzero':'-P',
                    'output_nbins_histogram':'-h',
                    'output_nbins_minMax_histogram':'-H'}

#####################################
# Adapted again, until the end.
# Build the user-specfied options into the command.
if not context.custom_dict['params'].keys():
    print("{} requires at least one option is chosen.".format(command))
    sp.run(['fslstats'], stdout=sp.PIPE, stderr=sp.PIPE, universal_newlines=True, env=environ)
    os.sys.exit()
else:
    for key in context.custom_dict['params'].keys():
        if key=='function_options':
            # Since this is a string of options, strip all the
            # non-alphabet characters and create an argument-by-
            #argument list. (fslstats compliant format)
            print(context.custom_dict['params'][key])
            options = list(re.sub(r'\W+','', context.custom_dict['params'][key]))
            print(options)
            for el in options:
                command.append('-'+str(el))
        else:
            command.extend([custom_tag_dict[key],str(context.custom_dict['params'][key])])

    result = sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE,
                            universal_newlines=True, env=context.custom_dict['environ'])

    if result.returncode == 0:
        print(result.stdout) # Report out the requested stats.
    else:
        print('The command:\n ' +
                            ' '.join(command) +
                            '\nfailed.')
        print(result.stderr)  # Give some indication of why the calculation failed.
        os.sys.exit(result.returncode)