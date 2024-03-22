# ngs_platform

this projects goal is to build a bioinformatics platform for new clinical diagnosis.

we target an unimpeded integration experience for new diagnosis methods.

success will be indicated through a low time and engineering effort when deploying new diagnosis.

this project is mostly for documentation, but secondly aimed at bioinformatic clinicians, researchers and brave developers wanting to run their own analysis platform.

it contains a webapp for controlling analysis pipelines and some data management.

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

note: meson dist creates a tarball from the latest commit, not the current dir

```
# when changing the buildscripts sometimes you might need to run:
meson --reconfigure /tmp/builddir
```

## development

when developing, consider enabeling the provided git-hooks:
```
cp git_hooks/* .git/hooks
```
