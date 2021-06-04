import os.path as op
from os import name
from nipype.interfaces.base import (
    CommandLineInputSpec,
    CommandLine,
    File,
    TraitedSpec,
    Str,
    traits
)


### HD-BET ###
# Documentation: https://github.com/MIC-DKFZ/HD-BET


class HDBETInputSpec(CommandLineInputSpec):
    in_file = File(desc="Input volume", exists=True,
                   mandatory=True, position=0, argstr="-i %s")
    device = Str(mandatory=False, argstr="-device %s",
                 default_value="cpu", usedefault=True)
    mode = Str(mandatory=False, argstr="-mode %s",
               default_value="fast", usedefault=True)
    tta = traits.Int(mandatory=False, argstr="-tta %s",
                     default_value=0, usedefault=True)
    out_file = File(desc="Output volume", position=1, argstr="-o %s")
    mask_file = File(desc="Output mask")


class HDBETOutputSpec(TraitedSpec):
    out_file = File(desc="Output volume", exists=True)
    mask_file = File(desc="Output mask", exists=True)


class HDBET(CommandLine):
    input_spec = HDBETInputSpec
    output_spec = HDBETOutputSpec
    _cmd = "hd-bet"

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["out_file"] = op.abspath(self.inputs.out_file)
        outputs["mask_file"] = op.abspath(self.inputs.mask_file)
        return outputs


### SynB0 ###
# Documentation: https://github.com/MASILab/Synb0-DISCO
# Fork used here: https://github.com/jakepalmer/Synb0-DISCO


class SynB0InputSpec(CommandLineInputSpec):
    in_file = File(exists=True, argstr="%s", mandatory=True,
                   position=0, desc="Distorted B0 image")
    in_T1 = File(exists=True, argstr="%s", mandatory=True,
                 position=1, desc="Input T1 image")
    in_T1mask = File(exists=True, argstr="%s",   position=2,
                     desc="Input T1 mask image")
    run_topup = Str(mandatory=False, argstr="%s",
                    default_value="--notopup", usedefault=True)
    out_file = File(mandatory=True, desc="Undistorted b0")


class SynB0OutputSpec(TraitedSpec):
    out_file = File(desc="Undistorted B0")


class SynB0(CommandLine):
    input_spec = SynB0InputSpec
    output_spec = SynB0OutputSpec
    _cmd = "/opt/Synb0-DISCO/src/pipeline.sh"

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["out_file"] = op.abspath(self.inputs.out_file)
        return outputs


### MRGRID ###
# Documentation: https://mrtrix.readthedocs.io/en/latest/reference/commands/mrgrid.html#mrgrid


class MRGridInputSpec(CommandLineInputSpec):
    in_file = File(desc="Input volume", exists=True,
                   mandatory=True, position=0, argstr="%s")
    operation = Str(mandatory=False, argstr="%s", position=1,
                    default_value="regrid", usedefault=True)
    voxel_size = traits.Float(mandatory=True, argstr="-vox %s", position=2)
    out_file = Str(desc="Output volume", position=3, argstr="%s")


class MRGridOutputSpec(TraitedSpec):
    out_file = File(desc="Output volume", exists=True)


class MRGrid(CommandLine):
    input_spec = MRGridInputSpec
    output_spec = MRGridOutputSpec
    _cmd = "mrgrid"

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["out_file"] = op.abspath(self.inputs.out_file)
        return outputs


### SS3T CSD ###
# Documentation: https://3tissue.github.io/doc/


class SS3TInputSpec(CommandLineInputSpec):
    in_file = File(desc="Prepped DWI input", exists=True,
                   mandatory=True, position=0, argstr="%s")
    wm_response = File(desc="WM response function", exists=True,
                       mandatory=True, position=1, argstr="%s")
    wmfod_out = Str(desc="WMFOD image out", exists=True,
                    mandatory=True, position=2, argstr="%s")
    gm_response = File(desc="GM response function", exists=True,
                       mandatory=True, position=3, argstr="%s")
    gm_out = Str(desc="GM image out", exists=True,
                 mandatory=True, position=4, argstr="%s")
    csf_response = File(desc="CSF response function",
                        exists=True, mandatory=True, position=5, argstr="%s")
    csf_out = Str(desc="CSF image out", exists=True,
                  mandatory=True, position=6, argstr="%s")
    in_mask = File(desc="DWI mask", exists=True, mandatory=True,
                   position=7, argstr="-mask %s")


class SS3TOutputSpec(TraitedSpec):
    wmfod_out = Str(desc="WMFOD image", exists=True)
    gm_out = Str(desc="GM image", exists=True)
    csf_out = Str(desc="CSF image", exists=True)


class SS3T(CommandLine):
    input_spec = SS3TInputSpec
    output_spec = SS3TOutputSpec
    _cmd = "/opt/MRtrix3Tissue/bin/ss3t_csd_beta1"

    # def _run_interface(self, runtime):
    #     import os
    #     # Add ss3t branch to path
    #     path = "/opt/MRtrix3Tissue/bin"
    #     os.environ["PATH"] += path + os.pathsep
    #     return runtime

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["wmfod_out"] = op.abspath(self.inputs.wmfod_out)
        outputs["gm_out"] = op.abspath(self.inputs.gm_out)
        outputs["csf_out"] = op.abspath(self.inputs.csf_out)
        return outputs


### NORMALISATION ###
# Documentation: https://mrtrix.readthedocs.io/en/latest/reference/commands/mtnormalise.html


class MTNormaliseInputSpec(CommandLineInputSpec):
    wmfod_in = File(desc="WMFOD file", exists=True,
                    mandatory=True, position=0, argstr="%s")
    wmfod_norm_out = Str(desc="Normalised WMFOD file",
                         exists=True, mandatory=True, position=1, argstr="%s")
    gm_in = File(desc="GM file", exists=True,
                 mandatory=True, position=2, argstr="%s")
    gm_norm_out = Str(desc="Normalised GM file", exists=True,
                      mandatory=True, position=3, argstr="%s")
    csf_in = File(desc="CSF file", exists=True,
                  mandatory=True, position=4, argstr="%s")
    csf_norm_out = Str(desc="Normalised CSF file", exists=True,
                       mandatory=True, position=5, argstr="%s")
    in_mask = File(desc="DWI mask", exists=True, mandatory=True,
                   position=6, argstr="-mask %s")


class MTNormaliseOutputSpec(TraitedSpec):
    wmfod_norm_out = Str(desc="WMFOD image", exists=True)
    gm_norm_out = Str(desc="GM image", exists=True)
    csf_norm_out = Str(desc="CSF image", exists=True)


class MTNormalise(CommandLine):
    input_spec = MTNormaliseInputSpec
    output_spec = MTNormaliseOutputSpec
    _cmd = "mtnormalise"

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["wmfod_norm_out"] = op.abspath(self.inputs.wmfod_norm_out)
        outputs["gm_norm_out"] = op.abspath(self.inputs.gm_norm_out)
        outputs["csf_norm_out"] = op.abspath(self.inputs.csf_norm_out)
        return outputs


### MEAN RESPONSE ###
# Documentation: https://mrtrix.readthedocs.io/en/latest/reference/commands/responsemean.html#responsemean


class MeanResponseInputSpec(CommandLineInputSpec):
    in_files = traits.List(desc="List of files to average", exists=True,
                           mandatory=True, position=0, argstr="%s")
    out_file = Str(desc="Mean response function",
                   exists=True, mandatory=True, position=-1, argstr="%s")


class MeanResponseOutputSpec(TraitedSpec):
    out_file = Str(desc="Mean response function", exists=True)


class MeanResponse(CommandLine):
    input_spec = MeanResponseInputSpec
    output_spec = MeanResponseOutputSpec
    _cmd = "responsemean"

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["out_file"] = op.abspath(self.inputs.out_file)
        return outputs


### MRTRIX DWI PREPROCESS ###


class DWIPreprocInputSpec(CommandLineInputSpec):
    in_file = File(
        exists=True, argstr="%s", position=0, mandatory=True, desc="input DWI image"
    )
    out_file = File(
        "preproc.mif",
        argstr="%s",
        mandatory=True,
        position=1,
        usedefault=True,
        desc="output file after preprocessing",
    )
    rpe_options = traits.Enum(
        "none",
        "pair",
        "all",
        "header",
        argstr="-rpe_%s",
        position=2,
        mandatory=True,
        desc='Specify acquisition phase-encoding design. "none" for no reversed phase-encoding image, "all" for all DWIs have opposing phase-encoding acquisition, "pair" for using a pair of b0 volumes for inhomogeneity field estimation only, and "header" for phase-encoding information can be found in the image header(s)',
    )
    pe_dir = traits.Str(
        argstr="-pe_dir %s",
        mandatory=True,
        desc="Specify the phase encoding direction of the input series, can be a signed axis number (e.g. -0, 1, +2), an axis designator (e.g. RL, PA, IS), or NIfTI axis codes (e.g. i-, j, k)",
    )
    ro_time = traits.Float(
        argstr="-readout_time %f",
        desc="Total readout time of input series (in seconds)",
    )
    in_epi = File(
        exists=True,
        argstr="-se_epi %s",
        desc="Provide an additional image series consisting of spin-echo EPI images, which is to be used exclusively by topup for estimating the inhomogeneity field (i.e. it will not form part of the output image series)",
    )
    align_seepi = traits.Bool(
        argstr="-align_seepi",
        desc="Achieve alignment between the SE-EPI images used for inhomogeneity field estimation, and the DWIs",
    )
    eddy_options = traits.Str(
        argstr='-eddy_options "%s"',
        desc="Manually provide additional command-line options to the eddy command",
    )
    topup_options = traits.Str(
        argstr='-topup_options "%s"',
        desc="Manually provide additional command-line options to the topup command",
    )
    export_grad_mrtrix = traits.Bool(
        argstr="-export_grad_mrtrix", desc="export new gradient files in mrtrix format"
    )
    export_grad_fsl = traits.Bool(
        argstr="-export_grad_fsl", desc="export gradient files in FSL format", position=-4
    )
    out_grad_mrtrix = File(
        "grad.b",
        argstr="%s",
        usedefault=False,
        requires=["export_grad_mrtrix"],
        desc="name of new gradient file",
    )
    out_grad_fsl = traits.Tuple(
        File("grad.bvecs", usedefault=True, desc="bvecs"),
        File("grad.bvals", usedefault=True, desc="bvals"),
        argstr="%s %s",
        requires=["export_grad_fsl"],
        desc="Output (bvecs, bvals) gradients FSL format",
        position=-3
    )
    in_bvec = File(
        exists=True, argstr="-fslgrad %s", desc="bvecs file in FSL format", position=-2
    )
    in_bval = File(
        exists=True, argstr="%s", desc="bvals file in FSL format", position=-1
    )


class DWIPreprocOutputSpec(TraitedSpec):
    out_file = File(argstr="%s", desc="output preprocessed image series")
    out_grad_mrtrix = File(
        "grad.b",
        argstr="%s",
        usedefault=False,
        desc="preprocessed gradient file in mrtrix3 format",
    )
    out_fsl_bvec = File(
        "grad.bvecs",
        argstr="%s",
        usedefault=True,
        desc="exported fsl gradient bvec file",
    )
    out_fsl_bval = File(
        "grad.bvals",
        argstr="%s",
        usedefault=True,
        desc="exported fsl gradient bval file",
    )


class DWIPreproc(CommandLine):
    _cmd = "dwifslpreproc"
    input_spec = DWIPreprocInputSpec
    output_spec = DWIPreprocOutputSpec

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["out_file"] = op.abspath(self.inputs.out_file)
        if self.inputs.export_grad_mrtrix:
            outputs["out_grad_mrtrix"] = op.abspath(
                self.inputs.out_grad_mrtrix)
        if self.inputs.export_grad_fsl:
            outputs["out_fsl_bvec"] = op.abspath(self.inputs.out_grad_fsl[0])
            outputs["out_fsl_bval"] = op.abspath(self.inputs.out_grad_fsl[1])

        return outputs
