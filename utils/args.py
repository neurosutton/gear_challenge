import re
import os, os.path as op
import subprocess as sp


def handle_multiple_imgs(context):
    """
    fslstats allows multiple nii's to be submited as the (a) input image,
    (b) mask image, and (c) difference image. To accomodate multiple nii's,
    create a custom-user field to build the custom_dict with arg:nii pairs.
    """
    # Grab the primary image
    context.custom_dict["input_image"] = context.get_input("input_image")["location"][
        "name"
    ]

    # If secondary images are provided, grab the inputs
    if context.get_input("mask_image"):
        context.custom_dict["mask_image"] = context.get_input("mask_image")["location"][
            "name"
        ]
    if context.get_input("difference_image"):
        context.custom_dict["difference_image"] = context.get_input("difference_image")[
            "location"
        ]["name"]


def parse_params(context):
    """
    Parse the statistical arguments given to fslstats so the command can be built.
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
            if config[key] != 0 and config[key] != "":
                params[key] = config[key]
    context.custom_dict["params"] = params

def validate(context):
    """
    Raises: Throw errors for setting violations.
    """

    log = context.log
    params = context.custom_dict['params']
    keys = params.keys()

    if not keys:
        print(dir(context))
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

    custom_tag_dict = {"upper_threshold": "-u",
        "lower_threshold": "-l",
        "output_nth_percentile": "-p",
        "output_nth_percentile_nonzero": "-P",
        "output_nbins_histogram": "-h",
        "output_nbins_minMax_histogram": "-H",
    }
    return [custom_tag_dict[key], str(context.custom_dict["params"][key])]


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
    if "t" in context.custom_dict["params"].keys():
        command.append("-t")

    # Add main image
    command.append(context.custom_dict["input_image"])

    # Add any subsequent image file options
    if "mask_image" in context.custom_dict:
        command.extend(["-k", context.custom_dict["mask_image"]])
    if "difference_image" in context.custom_dict:
        command.extend(["-d", context.custom_dict["difference_image"]])
    if context.custom_dict["params"].keys():
        for k,v in context.custom_dict["params"].items():
            if v==True:
                command.extend(['-'+k])
            else:
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
