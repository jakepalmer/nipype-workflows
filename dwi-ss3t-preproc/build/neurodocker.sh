#!/bin/bash

img_name="docker_image_name_with_tag"
push = "no"

if [ ! -f "license.txt" ]; then
    echo "ERROR: Freesurfer license not found in build directory"
    exit 1
else
    echo ">> Generating"
    docker run --rm repronim/neurodocker:master generate docker \
        --base=ubuntu:16.04 \
        --pkg-manager=apt \
        --fsl version=6.0.4 method=binaries \
        --ants version=2.3.0 method=binaries \
        --convert3d version=1.0.0 method=binaries \
        --freesurfer version=7.1.1 method=binaries --copy license.txt /opt/freesurfer-7.1.1/ \
        --miniconda \
            conda_install="python=3.9 pip" \
            pip_install="nipype" \
            create_env="dwi_preproc" \
            activate=true \
        --run "mkdir /project && mkdir /scratch && touch /usr/bin/nvidia-smi && \
              apt-get update && apt-get install -y \
                git \
                g++ \
                libeigen3-dev \
                zlib1g-dev \
                libqt4-opengl-dev \
                libfftw3-dev \
                libtiff5-dev \
                libpng-dev \
                libopenblas-dev \
                graphviz \
                libgraphviz-dev \
                curl && \
              conda install -y -q --name dwi_preproc -c mrtrix3 mrtrix3 && \
              conda install -y -q --name dwi_preproc -c pytorch torchvision && \
              git clone https://github.com/MIC-DKFZ/HD-BET /opt/HD-BET && \
                cd /opt/HD-BET && \
                /opt/miniconda-latest/envs/dwi_preproc/bin/pip install -e ." \
        --run "git clone https://github.com/jakepalmer/Synb0-DISCO /opt/Synb0-DISCO" \
        --run "git clone https://github.com/3Tissue/MRtrix3Tissue.git /opt/MRtrix3Tissue && \
                cd /opt/MRtrix3Tissue && \
                ./configure -nogui && \
                ./build" > Dockerfile

    # BUILD
    echo ">> Building"
    docker build -t ${img_name} .

    # PUSH
    if [ push == "yes" ]; then
      echo ">> Pushing"
      docker push ${img_name}
    else
      echo ">> Pushing skipped"
    fi
    echo ">> Finished"
fi
