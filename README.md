# ngs_pipeline

this projects goal is to build a bioinformatics pipeline for new clinical diagnosis methods.

we target an unimpeded integration experience for new diagnosis methods.

success will be indicated through a low time and engineering effort when deploying new diagnosis.

this project is mostly for documentation, but secondly aimed at bioinformatic clinicians, researchers and brave developers wanting to run their own pipeline.

it also contains a webapp for controlling the pipeline execution and data management.

## build

### build dependencies

basic:

* meson
* ninja
* plantuml

submodule dependencies can be found in the submodule directories

## build commands

```
meson setup /tmp/builddir --wipe
cd /tmp/builddir
meson configure -Doption=value
meson compile -v
meson test
meson dist
```

meson dist creates a tarball from the latest commit, not the current dir
the productions server automatically tries pulling the latest dist tarball

```
# when changing the buildscripts sometimes you might need to run:
meson --reconfigure /tmp/builddir
```

## development

when developing make sure to run:
```
cp git_hooks/* .git/hooks
```

this enables pre commit checks to automatically ensure compliance

## compliance

to avoid commiting possibly sensitive data, there is a scanning script in compliance.
it's executed during `meson test` and pre-commit.

it's recommended to regularily check and extend that script with aggressive patterns for sensitive data detection.
