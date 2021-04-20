import re
import os, os.path as op
import subprocess as sp


def handleMultiImgs(context):
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


def parseParams(context):
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
    Throw errors for setting violations.
    """

    log = context.log
    params = context.custom_dict['params']
    keys = params.keys()

    if not keys:
        print(dir(context))
        raise Exception ('fslstats requires at least one option is chosen.')

        os.sys.exit()


def _setStats(context, key):
    """
    Users select stats to run from config field in manifest.json. All string options
    are handled by the "function_options" field. Other types (with input values) are
    handled by this method.

    Parameters
    ----------
    key : str
        Statistic requested, which is not handled by the "function_options" field

    Returns
    -------
    list
        values (option and value) to be appended to the fslstats command
    """

    custom_tag_dict = {"upper_threshold": "-u",
        "lower_threshold": "-l",
        "output_nth_percentile": "-p",
        "output_nth_percentile_nonzero": "-P",
        "output_nbins_histogram": "-h",
        "output_nbins_minMax_histogram": "-H",
    }
    return [custom_tag_dict[key], str(context.custom_dict["params"][key])]


def _BuildCommandList(context, command=['fslstats']):
    """
    Create the command string to pass to subprocess.

    Parameters
    ----------
    command : list
        By default, the command will start with fslstats and be built from other
        parameters that have already been parsed (see parseParams and setStats)

    Returns
    -------
    formatted fslstats command
    """
    # Add an option of splitting a timeseries
    # Per fslstats usage, this tag comes before other image optionsin the command
    if "-t" in context.custom_dict["params"]["function_options"]:
        command.append("-t")
        # Remove '-t' from the remaining parsable options
        context.custom_dict["params"]["function_options"] = context.custom_dict[
            "params"
        ]["function_options"].replace("-t", "")

    # Add main image
    command.append(context.custom_dict["input_image"])

    # Add any subsequent image file options
    if "mask_image" in context.custom_dict:
        command.extend(["-k", context.custom_dict["mask_image"]])
    if "difference_image" in context.custom_dict:
        command.extend(["-d", context.custom_dict["difference_image"]])
    if context.custom_dict["params"].keys():
        for key in context.custom_dict["params"].keys():
            if key == "function_options":
                # Since this is a string of options, strip all the
                # non-alphabet characters and create an argument-by-
                # argument list. (fslstats compliant format)
                options = list(re.sub(r"\W+", "", context.custom_dict["params"][key]))
                for o in options:
                    command.append("-" + str(o))
            else:
                command.extend(_setStats(context, key))
    return command

def _reportOut(context, command, result):
    env = context.custom_dict["environ"]['FLYWHEEL']
    if op.isdir(op.join(env, 'output')):
        with open(op.join(env, 'output','fslstats.txt'),'w+') as f:
            f.write('{}\n{}'.format(' '.join(command), result.stdout))
    else:
        print(result.stdout)  # Report out the requested stats.

def execute(context, dry_run=False):
    command = _BuildCommandList(context)
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
            _reportOut(context, command, result)
        else:
            context.log.error("The command:\n " + " ".join(command) + "\nfailed.")
            # Give some indication of why the calculation failed.
            context.log.error(result.stderr)
            os.sys.exit(result.returncode)
