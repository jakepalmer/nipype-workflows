#!/opt/miniconda-latest/envs/dwi_preproc/bin/python3

#####
# SS3T DWI preprocessing
#####

import os.path as op
from os import name
from pathlib import Path
from nipype import (
    Node,
    JoinNode,
    Workflow,
    IdentityInterface,
    SelectFiles,
    DataSink
)
import nipype.interfaces.mrtrix3 as mrt
import nipype.interfaces.fsl as fsl
import src.custom_classes as custom


# ----- SETUP -----
# Make sure these paths are updated as needed

# base_dir = Path("/home")  # DOCKER
base_dir = Path("/path/to/base/on/HPC")  # SINGULARITY on Artemis
input_dir = base_dir / "imaging_data" / "input"
deriv_dir = base_dir / "imaging_data" / "output"
code_dir = base_dir / "code"

# Make derivs if not exist
deriv_dir.mkdir(parents=True, exist_ok=True)


# ----- DATA SOURCES -----


subjects = [s.name for s in input_dir.iterdir() if s.is_dir()
            and "sub-" in str(s)]

templates = {
    "anat": "{subject_id}/anat/{subject_id}_T1w.nii.gz",
    "dwi": "{subject_id}/dwi/{subject_id}_dwi.nii.gz",
    "bval": "{subject_id}/dwi/{subject_id}_dwi.bval",
    "bvec": "{subject_id}/dwi/{subject_id}_dwi.bvec"
}

# Data input
infosource = Node(IdentityInterface(fields=["subject_id"]), name="infosource")
infosource.iterables = [("subject_id", subjects)]

selectfiles = Node(SelectFiles(templates), name="selectfiles")
selectfiles.inputs.base_directory = str(input_dir)

# Data output
substitutions = [("_subject_id_", "")]
subjFolders = [("dwi/sub-%s" % (sub), "sub-%s" % (sub))
               for sub in subjects]
substitutions.extend(subjFolders)

datasink = Node(DataSink(), name="datasink")
datasink.inputs.base_directory = str(deriv_dir)
datasink.inputs.substitutions = substitutions


# ----- WORKFLOW NODES -----


# Get b0"s
dwiextract = Node(mrt.DWIExtract(), name="dwiextract")
dwiextract.inputs.bzero = True
dwiextract.inputs.out_file = "b0_vols.nii.gz"

# Mean b0's
mrmath = Node(mrt.MRMath(), name="mrmath")
mrmath.inputs.axis = 3
mrmath.inputs.operation = "mean"
mrmath.inputs.out_file = "b0_mean.nii.gz"

# Brain extraction nodes
hdbet_T1 = Node(custom.HDBET(), name="hdbet_T1")
hdbet_T1.inputs.out_file = "T1_brain.nii.gz"
hdbet_T1.inputs.mask_file = "T1_brain_mask.nii.gz"

# hdbet_dwi = Node(custom.HDBET(), name="hdbet_dwi")
# hdbet_dwi.inputs.out_file = "dwi_brain.nii.gz"
# hdbet_dwi.inputs.mask_file = "dwi_brain_mask.nii.gz"

hdbet_dwi_upsamp = Node(custom.HDBET(), name="hdbet_dwi_upsamp")
hdbet_dwi_upsamp.inputs.out_file = "dwi_upsamp_brain.nii.gz"
hdbet_dwi_upsamp.inputs.mask_file = "dwi_upsamp_brain_mask.nii.gz"

# Synb0
synb0 = Node(custom.SynB0(), name="synb0")
synb0.inputs.out_file = "b0_all.nii.gz"
synb0.inputs.run_topup = "--notopup"

# Topup and eddy via MRtrix preprocess
dwipreproc = Node(custom.DWIPreproc(), name="dwipreproc")
dwipreproc.inputs.rpe_options = "pair"
dwipreproc.inputs.pe_dir = "AP"
dwipreproc.inputs.align_seepi = True
dwipreproc.inputs.export_grad_fsl = True
dwipreproc.inputs.out_grad_fsl = ("dwi_preproc.bvec", "dwi_preproc.bval")
dwipreproc.inputs.eddy_options = " --slm=linear --repol"
dwipreproc.inputs.out_file = "dwi_preproc.mif"

# Bias correct
biascorrect = Node(mrt.DWIBiasCorrect(), name="biascorrect")
biascorrect.inputs.use_ants = True

# Compute response function
response_func = Node(mrt.ResponseSD(), name="response_fuc")
response_func.inputs.algorithm = "dhollander"
response_func.inputs.wm_file = "response_wm.txt"
response_func.inputs.gm_file = "response_gm.txt"
response_func.inputs.csf_file = "response_csf.txt"

# Upsample
upsample = Node(custom.MRGrid(), name="upsample")
upsample.inputs.operation = "regrid"
upsample.inputs.voxel_size = 1.5
upsample.inputs.out_file = "dwi_preproc_biascorrect_upsamp.mif"

# Mask upsampled and preprocessed DWI
dwiextract_upsamp = Node(mrt.DWIExtract(), name="dwiextract_upsamp")
dwiextract_upsamp.inputs.bzero = True
dwiextract_upsamp.inputs.out_file = "b0_vols_upsamp.nii.gz"

mrmath_upsamp = Node(mrt.MRMath(), name="mrmath_upsamp")
mrmath_upsamp.inputs.axis = 3
mrmath_upsamp.inputs.operation = "mean"
mrmath_upsamp.inputs.out_file = "b0_upsamp.nii.gz"

# Compute group average response function
response_mean_wm = JoinNode(custom.MeanResponse(), name="response_mean_wm",
                            joinsource=infosource, joinfield=["in_files"])
response_mean_wm.inputs.out_file = "mean_response_wm.txt"

response_mean_gm = JoinNode(custom.MeanResponse(), name="response_mean_gm",
                            joinsource=infosource, joinfield=["in_files"])
response_mean_gm.inputs.out_file = "mean_response_gm.txt"

response_mean_csf = JoinNode(custom.MeanResponse(), name="response_mean_csf",
                             joinsource=infosource, joinfield=["in_files"])
response_mean_csf.inputs.out_file = "mean_response_csf.txt"

# # Compute FOD with ss3t
ss3t = Node(custom.SS3T(), name="ss3t")
ss3t.inputs.wmfod_out = "wmfod.mif"
ss3t.inputs.gm_out = "gm.mif"
ss3t.inputs.csf_out = "csf.mif"

# Joint intensity normalisation
mtnormalise = Node(custom.MTNormalise(), name="mtnormalise")
mtnormalise.inputs.wmfod_norm_out = "wmfod_norm.mif"
mtnormalise.inputs.gm_norm_out = "gm_norm.mif"
mtnormalise.inputs.csf_norm_out = "csf_norm.mif"


# ----- WORKFLOW -----


wf = Workflow(name="dwi_ss3t_preproc_wf")
wf.base_dir = str(deriv_dir)

wf.connect([
    # Get files
    (infosource, selectfiles, [("subject_id", "subject_id")]),
    # Get b0's
    (selectfiles, dwiextract, [("dwi", "in_file")]),
    (selectfiles, dwiextract, [("bval", "in_bval")]),
    (selectfiles, dwiextract, [("bvec", "in_bvec")]),
    # Mean b0's
    (dwiextract, mrmath, [("out_file", "in_file")]),
    # T1 mask
    (selectfiles, hdbet_T1, [("anat", "in_file")]),
    # Synb0
    (selectfiles, synb0, [("anat", "in_T1")]),
    (hdbet_T1, synb0, [("out_file", "in_T1mask")]),
    (mrmath, synb0, [("out_file", "in_file")]),
    # Topup/eddy via mrtrix3
    (selectfiles, dwipreproc, [("dwi", "in_file")]),
    (selectfiles, dwipreproc, [("bval", "in_bval")]),
    (selectfiles, dwipreproc, [("bvec", "in_bvec")]),
    (synb0, dwipreproc, [("out_file", "in_epi")]),
    # Bias correction
    (dwipreproc, biascorrect, [("out_file", "in_file")]),
    (dwipreproc, biascorrect, [("out_fsl_bval", "in_bval")]),
    (dwipreproc, biascorrect, [("out_fsl_bvec", "in_bvec")]),
    # Compute response function
    (biascorrect, response_func, [("out_file", "in_file")]),
    (dwipreproc, response_func, [("out_fsl_bval", "in_bval")]),
    (dwipreproc, response_func, [("out_fsl_bvec", "in_bvec")]),
    # Upsample
    (biascorrect, upsample, [("out_file", "in_file")]),
    # Get upsample b0's
    (upsample, dwiextract_upsamp, [("out_file", "in_file")]),
    (dwipreproc, dwiextract_upsamp, [("out_fsl_bval", "in_bval")]),
    (dwipreproc, dwiextract_upsamp, [("out_fsl_bvec", "in_bvec")]),
    # Mean upsample b0's
    (dwiextract_upsamp, mrmath_upsamp, [("out_file", "in_file")]),
    # Mask upsample DWI
    (mrmath_upsamp, hdbet_dwi_upsamp, [("out_file", "in_file")]),
    # Compute group mean response
    (response_func, response_mean_wm, [("wm_file", "in_files")]),
    (response_func, response_mean_gm, [("gm_file", "in_files")]),
    (response_func, response_mean_csf, [("csf_file", "in_files")]),
    # Compute FODs w SS3T
    (upsample, ss3t, [("out_file", "in_file")]),
    (hdbet_dwi_upsamp, ss3t, [("out_file", "in_mask")]),
    (response_mean_wm, ss3t, [("out_file", "wm_response")]),
    (response_mean_gm, ss3t, [("out_file", "gm_response")]),
    (response_mean_csf, ss3t, [("out_file", "csf_response")]),
    # Joint intensity normalisation
    (hdbet_dwi_upsamp, mtnormalise, [("out_file", "in_mask")]),
    (ss3t, mtnormalise, [("wmfod_out", "wmfod_in")]),
    (ss3t, mtnormalise, [("gm_out", "gm_in")]),
    (ss3t, mtnormalise, [("csf_out", "csf_in")]),
    # Save data
    (dwipreproc, datasink, [("out_fsl_bval", "dwi_ss3t_preproc.@bval")]),
    (dwipreproc, datasink, [("out_fsl_bvec", "dwi_ss3t_preproc.@bvec")]),
    (hdbet_T1, datasink, [
     ("mask_file", "dwi_ss3t_preproc.@T1_mask")]),
    (upsample, datasink, [
     ("out_file", "dwi_ss3t_preproc.@dwi_preproc_upsamp")]),
    (hdbet_dwi_upsamp, datasink, [
     ("mask_file", "dwi_ss3t_preproc.@dwi_preproc_upsamp_mask")]),
    (mtnormalise, datasink, [
     ("wmfod_norm_out", "dwi_ss3t_preproc.@wmfod_norm")]),
    (mtnormalise, datasink, [("gm_norm_out", "dwi_ss3t_preproc.@gm_norm")]),
    (mtnormalise, datasink, [("csf_norm_out", "dwi_ss3t_preproc.@csf_norm")])
])


# ----- RUN -----


if __name__ == "__main__":
    wf.write_graph(graph2use="colored", format="png", simple_form=True)
    wf.config['execution'] = {'keep_inputs': 'True',
                              'crashfile_format': 'txt',
                              'remove_unnecessary_outputs': 'False'}
    wf.run(plugin="MultiProc")
