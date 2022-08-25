# ngs_pipeline

this projects goal is to build a bioinformatics pipeline for new clinical diagnosis methods.

we target an unimpeded integration experience for new diagnosis methods.

success will be indicated through a low time and engineering effort when deploying new diagnosis.

in the next few months, we want to have an automatic workflow containing:
    * liftover/remap
    * ensembleorg/vep
    * copy number variation analysis
    
this project is mostly for documentation, but secondly aimed at bioinformatic clinicians, researchers and brave developers wanting to run their own pipeline.


## build

# dependencies

* meson
* ninja-build

## build commands

```
meson setup builddir
meson configure -Doption=value

# might need to additionally run when changin the buildscripts
meson --reconfigure builddir

cd builddir

meson compile -v
meson test
```
