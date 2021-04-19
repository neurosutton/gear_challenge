from pathlib import Path

nifti_file = Path(__file__).resolve().parents[0].joinpath(("nifti_file.nii.gz"))
t2_file = Path(__file__).resolve().parents[0].joinpath(("t2_file.nii.gz"))
raw_config = []
config = []
config_with_input = []
input_files = [
    ["/flywheel/v0/inputs/x_file.nii.gz"],
    [str(nifti_file)],
    [str(nifti_file), str(t2_file)],
]
output_files = [
    ["/flywheel/v0/inputs/x_file_output.nii.gz"],
    ["/flywheel/v0/inputs/x_file_output.nii.gz"],
    ["/flywheel/v0/inputs/x_file_output.nii.gz"],
]
for i, (func_opt, file) in enumerate(zip(["-R", "", "-A2"], input_files)):
    raw_config_val = {
        "skull_image": (False if i % 2 == 0 else True),
        "vtk_surface_mesh": (False if i % 2 == 1 else True),
        "binary_brain_mask": (False if i % 2 == 0 else True),
        "brain_surf_outline": (False if i % 2 == 1 else True),
        "apply_mask_thresholding": (False if i % 2 == 0 else True),
        "fractional_intensity_threshold": i * 0.3,
        "vertical_gradient_intensity_threshold": i * 0.2,
        "center": f"{i},{i + 1},{i + 2}",
        "radius": (i+1) * 2,
        "function_option": func_opt,
    }
    raw_config.append(raw_config_val)
    config_val = {
        "skull": (False if i % 2 == 0 else True),
        "mesh": (False if i % 2 == 1 else True),
        "mask": (False if i % 2 == 0 else True),
        "outline": (False if i % 2 == 1 else True),
        "threshold": (False if i % 2 == 0 else True),
        "frac": i * 0.3,
        "vertical_gradient": i * 0.2,
        "center": [i, i + 1, i + 2],
        "radius": (i+1) * 2,
        "function_option": func_opt,
    }
    config.append(config_val)
