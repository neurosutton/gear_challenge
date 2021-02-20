# Create a base container that can run fslstats
#

# Use prepared fsl-base:6.0.1 based on ubuntu:xenial
# Build takes awhile because the image is about 10GB
FROM flywheel/fsl-base:6.0.1

MAINTAINER Flywheel <support@flywheel.io>

# Configure FSL environment
ENV FSLDIR=/usr/share/fsl/6.0
ENV FSL_DIR="${FSLDIR}"
ENV PATH=/usr/lib/fsl/6.0:$PATH
ENV POSSUMDIR=/usr/share/fsl/6.0
ENV LD_LIBRARY_PATH=/usr/lib/fsl/6.0:$LD_LIBRARY_PATH
ENV FSLOUTPUTTYPE=NIFTI_GZ

# Save docker environ
RUN python -c 'import os, json; f = open("/tmp/gear_environ.json", "w"); json.dump(dict(os.environ), f)' && \
pip3 install flywheel-sdk
#############################################

# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
RUN mkdir -p ${FLYWHEEL}
COPY run.py ${FLYWHEEL}/run.py
COPY manifest.json ${FLYWHEEL}/manifest.json

#Configure entrypoint
ENTRYPOINT ["python3 run.py"]