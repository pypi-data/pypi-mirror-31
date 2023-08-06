**Description:**

RM-Synthesis is technique used to transform polarised intensity measured in wavelength-space (lambda) to polarised intensity in Faraday-space (RM) -- see Brentjen & de Bruyn (2005) for more details.  Or vice versa.

**Motivation and the Approach**

This technqiue can become computationally expensive particularly in modern days of data-driven cutting edge radio instruments. For example, wide-field images (or observations) would imply a large number of line-of-sights (pixels) to evaluate for Faraday Rotated emission, and wide spectral-bandwidth observations -- a necessity for this technique -- would imply a large number of channels to average across. The combination of these two will result in an enourmous amount of data -- making optimization of RM-Synthesis technqiue very important -- especially for those that need to finish their PhDs in 3 years. Particularly for all-sky surveys such as VLASS, whereby all pixels need to be evaluated. In some cases though, if a user is mainly interested in a subset of pixels located in a particular region of the pixel map, e.g a radio galaxy/compact or extended emission, then the computation for this can be minimized by specifying a mask. The former is the main motivation to this work but serves both purposes.

In the original implementation of this technique and to my best of knowledge, all pixels within a channel are evaluated at once or say "per frame". Although this is might have been optimum approach at that time, the large dataset (in this case data cubes) produced by current radio instruments makes such matrix multiplication either computationally expensive or even impossible.

In our RM-Synthesis code, we evaluate each pixel at a time. This is the less optimum approach on earth but fortunately, due to multi-core CPUs, we have incorporated multiprocessing (and we intend to extend this to GPUs) -- to process multiple pixels in parallel. This is in hope that single-core computers are all extinct. We tested this on the 2048x2048x1000 cube images of Cyngus A (i.e 1000 channels).  Without parallel processing, this task takes over > 20 hours to run and with multi-processing using 6 cores this takes no more than 2 hours. When using the original approach we described above, we encounter Memory Error since the combined data size of our Stokes Q and U is 33 GB. And these data themselves are not in data-size standard we expect with the SKA. 

**Installation:**

pip install rm-synthesis

**Dependencies:**

1. Numpy
2. Multiprocessing
3. Astropy


**Data Requirements:**

1. Stokes Q and U FITS data cubes - shape 312 that is frequency, ra and dec.

2. Frequencies file - only text file is supported. 

NB:The number of frequencies in 2 myst be the same as in 1.

**How to run the code:**

1. You can check for all the inputs using:

                                  ``rmsynthesis -h``
            
2. The required inputs are (non-optional inputs are Stokes Q and U, and a frequency file): 

                                  ``rmsynthesis -q Q.fits -u U.fits -f freq.txt``
            
3. If you want your outputs to have a certain name, then you can specify the prefix by adding:

                                  ``rmsynthesis -q Q.fits -u U.fits -f freq.txt -o myprefix``
            
4. You have an option to specify the range of Faraday depth by specifying the maximum, mininum and the sample width. These are in rad/m^2. Others these will be determined internally -- but we do not gurantee optimum values so be mindful of this.

                                 ``rmsynthesis -q Q.fits -u U.fits -f freq.txt -rn -3000 -rx 3000 -rs 30``

5. Another option is to include multiprocessing. This is highly recommended for speeding up the process especially if you going to be dealing with large images. 
    
                                 ``rmsynthesis -q Q.fits -u U.fits -f freq.txt -np 3``

NB: 3 is the number of cores to use.


