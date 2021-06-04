# DWI SS3T Preprocessing

- Assumes being run with docker container or singularity built from docker on Artemis
- BIDS input
- Assumes general structure below where `code` directory is this repo:

```bash
|_code
| |____submit_run.pbs
| |____run.py
| |____build
| | |____build_sif.sh
| | |____neurodocker.sh
| | |____Dockerfile
| |____src
| | |____acqparams.txt
| | |____custom_classes.py
| | |____index.txt
|_imaging_data
| |____dicoms
| |____input
| |____output
```
