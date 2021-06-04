#!/bin/bash

#PBS -P HBA
#PBS -N sif_build
#PBS -l select=1:ncpus=3:mem=16GB
#PBS -l walltime=10:00:00
#PBS -j oe
#PBS -M jake.palmer@sydney.edu.au
#PBS -m ae
#PBS -q defaultQ

module load singularity/3.7.0

img_name="docker_image_name"
sing_dir="/path/to/sif/file"
scratch_dir="/path/to/scratch/dir"
export SINGULARITY_CACHEDIR=${scratch_dir}
export SINGULARITY_TMPDIR=${scratch_dir}
export HOME=${scratch_dir}

cd ${sing_dir} || exit

echo ""
echo "--------------------"
echo "Building dwi-SS3T-preproc"
echo "--------------------"
echo ""

# Will overwrite existing sif file

singularity pull --force docker://${img_name}
