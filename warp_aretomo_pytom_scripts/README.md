## Automated processing of Warp stacks with AreTomo and pytom-tm

In here are some scripts to automatically process Warp stacks: tilt-series are aligned with AreTomo and 
particles are subsequently localized with template matching via pytom.

Some notes:
* Automated processing is very dependent on the alignment with AreTomo, for this its essential to remove 
  bad tilts first in Warp so that they do not end up in the stacks. With the `-DarkTol 0.01` option AreTomo is 
  prevented from automatically attempting to remove dark tilts which makes uploading alignments back to Warp much 
  easier. The option `-OutImod 2` generates necessary outputs for Warp.
* There is a special script for K3 detector images. Cropping the stacks to square images before alignment makes 
  AreTomo function a lot better. This script first squares the stacks to calculate the alignment and then 
  applies it to the original stack to create a tomogram for template matching.
* Template matching here is aimed at batch processing of large macromolecular structures (ribosomes). The tomograms 
  are not dose-weighted, CTF-corrected, or patch-aligned which loses high-res signal. For these reasons, the 
  template generation cuts the CTF after the first zero crossing and a low-pass filter of 40A resolution is 
  applied during template matching.
* Particle assignment via `pytom_extract_candidates.py` uses a base cut-off estimation that is liberal in picking. If 
  you want higher selectivity you could include the `--tophat-filter` parameter to the script. pytom also produces 
  some graphs in the output directory that you can inspect to get an idea of how liberal the picking is. If the 
  picking needs to be more liberal increase `--number-of-false-positives` (works for both base and tophat extraction).
  See the pytom docs for specifics.
