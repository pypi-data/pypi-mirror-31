RM-Synthesis is technique used to transform polarized intensity between wavelength-space (lambda) and faraday-space (RM). See Brentjen & de Bruyn (2005) for more detail. 

This technqiue can become computationally expensive. For example, wide-field views imply a large number of line-of-sights (pixels) to evaluate, and wide spectral-bandwidth, although necessary, imply a large number of channels to average across. Thus, optimizing RM-Synthesis technqiue is important. Particularly for all-sky surveys such as VLASS, whereby all pixels need to be evaluated -- this is unlike the case where specific pixel locations are known and of interest.
In the original implementation, all pixels within lambda^2-plane are evaluated at once, although this is may have been optimum at that time, the large dataset of modern instruments makes it infeasible.

In our RM-Synthesis code, we evaluate each pixel at a time. This approach as is is the less optimum thus, we have incorporated multiprocessing (and we intend to extend this to GPUs) so that multiple pixels can we evaluated at once. This was tested on Cyngus A 2k by 2k images with 2-18 GHz bandwidth (~1000 channels). Without parallel processing, this task takes over > 20 hours to run and with multi-processing using 6 cores this takes exactly 2 hours. When using the original approach, we encounter Memory Error since the combined data size of our Stokes Q and U is 33 GB. 

1. Installation:

pip install RMSYNTHESIS


Dependencies:

1. Numpy
2. Multiprocessing
3. Astropy

