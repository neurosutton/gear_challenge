import re
import os
import subprocess as sp

def handleMultiImgs(context):
    """
    fslstats allows multiple nii's to be submited as the (a) input image,
    (b) mask image, and (c) difference image. To accomodate multiple nii's,
    create a custom-user field to build the custom_dict with arg:nii pairs.

    Parameters
    ----------
    context : context object from flywheel.GearContext; defined by manifest.json
    """

    # grab environment for gear
    with open('/tmp/gear_environ.json', 'r') as f:
        environ = json.load(f)

    context.custom_dict['environ'] = environ

    # Grab the primary image
    context.custom_dict['input_image'] = context.get_input("input_image")[
        'location']['name']

    # If secondary images are provided, grab the inputs
    if context.get_input("mask_image"):
        context.custom_dict['mask_image'] = context.get_input("mask_image")[
            'location']['name']
    if context.get_input("difference_image"):
        context.custom_dict['difference_image'] = context.get_input("difference_image")[
            'location']['name']


def build(context):
    """
    """
    config = context.config
    params = {}
    for key in config.keys():
        # Use only those boolean values that are True
        if isinstance(config[key], bool):
            if config[key]:
                params[key] = True
        else:
            # if the key-value is zero or an empty string, we skip and use the defaults
            if config[key] != 0 and config[key] != '':
                params[key] = config[key]
    context.custom_dict['params'] = params

    custom_tag_dict = {'upper_threshold': '-u',
                       'lower_threshold': '-l',
                       'output_nth_percentile': '-p',
                       'output_nth_percentile_nonzero': '-P',
                       'output_nbins_histogram': '-h',
                       'output_nbins_minMax_histogram': '-H'}

def validate(context):
    """
    """

def BuildCommandList(command, ParamList):
    """
    """
    # Base command
    command = ['fslstats']

    # Add a pre-option of splitting a timeseries, per fslstats usage
    if '-t' in context.custom_dict['params']['function_options']:
        command.append('-t')
        context.custom_dict['params']['function_options'] = context.custom_dict['params']['function_options'].replace(
            '-t', '')

    # Add main image
    command.append(context.custom_dict['input_image'])

    # Add any subsequent image file options
    if 'mask_image' in context.custom_dict:
        command.extend(['-k', context.custom_dict['mask_image']])
    if 'difference_image' in context.custom_dict:
        command.extend(['-d', context.custom_dict['difference_image']])
    if not context.custom_dict['params'].keys():
        print("{} requires at least one option is chosen.".format(command))
        sp.run(
            ['fslstats'],
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            universal_newlines=True,
            env=environ)
        os.sys.exit()
    else:
        for key in context.custom_dict['params'].keys():
            if key == 'function_options':
                # Since this is a string of options, strip all the
                # non-alphabet characters and create an argument-by-
                # argument list. (fslstats compliant format)
                options = list(
                    re.sub(
                        r'\W+',
                        '',
                        context.custom_dict['params'][key]))
                for o in options:
                    command.append('-' + str(o))
            else:
                command.extend([custom_tag_dict[key], str(
                    context.custom_dict['params'][key])])

    return command


def execute(context, dry_run=False):
    """
    """
    result = sp.run(
        command,
        stdout=sp.PIPE,
        stderr=sp.PIPE,
        universal_newlines=True,
        env=context.custom_dict['environ'])

    if result.returncode == 0:
        print(result.stdout)  # Report out the requested stats.
    else:
        print('The command:\n ' +
              ' '.join(command) +
              '\nfailed.')
        # Give some indication of why the calculation failed.
        print(result.stderr)
        os.sys.exit(result.returncode)