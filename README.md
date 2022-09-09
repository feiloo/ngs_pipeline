# ngs_pipeline

this projects goal is to build a bioinformatics pipeline for new clinical diagnosis methods.

we target an unimpeded integration experience for new diagnosis methods.

success will be indicated through a low time and engineering effort when deploying new diagnosis.

in the next few months, we want to have an automatic workflow containing:
    * liftover/remap
    * ensembleorg/vep
    * copy number variation analysis
    
this project is mostly for documentation, but secondly aimed at bioinformatic clinicians, researchers and brave developers wanting to run their own pipeline.

## compliance

to avoid commiting possibly sensitive data, there is a scanning script in compliance.
it's executed during `meson test` and pre-commit.

it's recommended to regularily check and extend that script with aggressive patterns for sensitive data detection.


## build

# dependencies

* meson
* ninja-build

## build commands

```
meson setup /tmp/builddir
cd /tmp/builddir
meson configure -Doption=value
meson compile -v
meson test
./continuous_deployment/release.sh
```

note: release.sh doesn't deploy, but marks a commit as a release
the productions server automatically try pulling the latest releases with update_pipeline.sh 
the production server then switches blue/green to the new version
if monitoring detects a failure, production is automatically rolled back to previous code version

# when changing the buildscripts sometimes you might need to run:
```
meson --reconfigure /tmp/builddir
```


