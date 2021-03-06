import re
import os, os.path as op
import subprocess as sp


def handle_multiple_imgs(context):
    """
    fslstats allows multiple nii's to be submited as the (a) input image,
    (b) mask image, and (c) difference image. To accomodate multiple nii's,
    create a custom-user field to build the custom_dict with arg:nii pairs.
    """
    inp_dir = op.join(context.custom_dict["environ"]['FLYWHEEL'],'input')
    for file_type in ['input_image','mask_image','difference_image']:
        if context.get_input(file_type):
            context.custom_dict[file_type] = op.join(inp_dir, file_type ,context.get_input(file_type)["location"]["name"])

def parse_params(context):
    """
    Parse the statistical arguments given to fslstats so the command can be built.
    """
    
    config = context.config
    params = {}
    for k, v in config.items():
        # Use only those boolean values that are True
        if isinstance(config[k], bool):
            if config[k]:
                params[k] = v
        else:
            # if the key-value is zero or an empty string, we skip and use the defaults
            if config[k] != 0 and config[k] != "":
                params[k] = config[k]
    context.custom_dict["params"] = params

def validate(context):
    """
    Raises: Throw errors for setting violations.
    """

    params = context.custom_dict['params']
    keys = params.keys()

    if not keys:
        context.log.info('No statistics were requested.')
        raise Exception ('fslstats requires at least one option is chosen.')
        os.sys.exit()


def _set_stats(context, key):
    """
    Users select stats to run from config field in manifest.json. All string options
    are handled by the "function_options" field. Other types (with input values) are
    handled by this method.

    Args:
        key (str): Statistic requested, which is not handled by the "function_options" field

    Returns:
        list of values (option and value) to be appended to the fslstats command
    """

    custom_tag_dict = {
        "Mean intensity": "-m",
        "Mean intensity (nonzero)": '-M',
        "Stdev": "-s",
        "Stdev (nonzero)":  "-S",
        "Upper threshold": "-u",
        "Lower threshold": "-l",
        "Percentile": "-p",
        "Percentile (nonzero)": "-P",
        "nbins for histogram": "-h",
        "Windowed nbins for histogram": "-H",
        "Robust min/max": "-r",
        "Min/max" : "-R",
        "Entropy": "-e",
        "Entropy (nonzero)": "-E",
        "Volume": '-v',
        "Volume (nonzero)": '-V',
        "ROI stats": "-w",
        "Max voxel coords": "-x",
        "Min voxel coords": "-X",
        "Center of gravity (mm)": "-c",
        "Center of gravity (voxels)": "-C",
        "Absolute values?": "-a",
        "NaN/Inf as zero?": "-n"
    }
    return [custom_tag_dict[key]]


def _build_command_list(context, command=['fslstats']):
    """
    Create the command string to pass to subprocess.

    Args:
        command (list): By default, the command will start with fslstats and be
        built from other parameters that have already been parsed (see parse_params
        and setStats)

    Returns:
        formatted fslstats command
    """
    # Add an option of splitting a timeseries
    # Per fslstats usage, this tag comes before other image optionsin the command
    if "Split by timepoint" in context.custom_dict["params"].keys():
        command.append("-t")
        # Eliminate reference to timepoint argument, since it is built into the 
        # command earlier than the other optional tags
        del context.custom_dict["params"]['Split by timepoint']

    # Add main image
    command.append(context.custom_dict["input_image"])

    # Add any subsequent image file options
    if "mask_image" in context.custom_dict:
        command.extend(["-k", context.custom_dict["mask_image"]])
    if "difference_image" in context.custom_dict:
        command.extend(["-d", context.custom_dict["difference_image"]])
    if context.custom_dict["params"].keys():
        for k in context.custom_dict["params"].keys():
            command.extend(_set_stats(context, k))
    return command

def _report_out(context, command, result):
    env = context.custom_dict["environ"]['FLYWHEEL']
    if op.isdir(op.join(env, 'output')):
        with open(op.join(env, 'output','fslstats.txt'),'w+') as f:
            f.write('{}\n{}'.format(' '.join(command), result.stdout))
    else:
        print(result.stdout)  # Report out the requested stats.

def execute(context, dry_run=False):
    command = _build_command_list(context)
    context.log.info("FSL Stats command: {}".format(' '.join(command)))
    if not dry_run:
        result = sp.run(
            command,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            universal_newlines=True,
            env=context.custom_dict["environ"],
        )
        context.log.info(result.returncode)
        context.log.info(result.stdout)

        if result.returncode == 0:
            _report_out(context, command, result)
        else:
            context.log.error("The command:\n " + " ".join(command) + "\nfailed.")
            # Give some indication of why the calculation failed.
            context.log.error(result.stderr)
            os.sys.exit(result.returncode)
