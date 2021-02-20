## fsl-stats

The fsl-stats gear calculates user-specified statistics on an image using the algorithms in FSL's fslstats.


### Quick start
To run the gear from the CLI
- Clone this repository.
- Login to the Flywheel Client with your API key.
- Search Dockerhub for flywheel/fsl-base
```
    docker pull flywheel/fsl-base
```
- Since this is not an authorized gear, go through the same process as the gear tutorial to run the Dockerfile and build a local gear.
```
    docker build -t <dockerhub_accountname>/fsl-stats:0.1.0 ./
```
- Make sure that you are in the top level of the gear directory.

If you are familiar with fslstats, you will be off and running in no time. This gear mirrors the syntax and arguments closely. If you would like the gear usage:
```
    fw gear local
```

### Example usage
Supposing you have sample images in the same level as the gear, you can get the mean and standard deviation of a specific scan.
```
    fw gear local --input_image=<your_local_image> --function_options='MS'
```
Note: the function_options need to have a single quote around all the options to be parsed. However, there are no constraints on whether you add '-' or ',' in the options that you would like. As fslstats is case-sensitive for the options, so is this gear.

Adding a mask to alter the volume that is used can be accomplished by adding a mask image.
```
    fw gear local --input_image=<your_local_image> --mask_image=<your_mask_image> --function_options='MS'
```
You will notice that, unless your mask encompasses the same voxels as your original image, the values have changed. If you are using a brain mask, your mean will likely go up, indicating that fewer low intensity voxels were included in the calculation and assuring you that a mask has been applied.

### Dependencies
This gear builds off the flywheel/fsl-base:6.0.1 image. Since this image takes care of installation of FSL (v.6.0.1) and all its dependencies, the initial pull takes a while.