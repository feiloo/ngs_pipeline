container_engine = find_program('podman')
python_bin = find_program('python3.11','python3.10','python3.9','python3.8')
bash_bin = find_program('bash')


pyfiles = [
	'pyproject.toml',
	'setup.py',
	'src/app/app.py',
	'src/app/config.py',
	'src/app/constants.py',
	'src/app/db.py',
	'src/app/filemaker_api.py',
	'src/app/__init__.py',
	'src/app/model.py',
	'src/app/parsers.py',
	'src/app/tasks_impl.py',
	'src/app/tasks.py',
	'src/app/tasks_utils.py',
	'src/app/templates/pipeline_dashboard.html',
	'src/app/templates/raw_db_document.html',
	'src/app/templates/raw_db_view.html',
	'src/app/ui.py',
	'src/app/workflow_backends.py',
	'src/__init__.py',
	]

testfiles = [
	'tests/conftest.py',
	'tests/test_app.py',
	'tests/test_db.py',
	'tests/test_filemaker_api.py',
	'tests/test_parsers.py',
	'tests/test_tasks_impl.py',
	'tests/test_tasks.py',
	'tests/test_tasks_utils.py',
	'tests/test_ui.py',
	'tests/test.wdl',
	'tests/test_workflow_backends.py',
	]

testdata = [
	'tests/fake_sequencer_output_dir/220101_M00000_0000_000000000-XXXXX/Alignment_1/20220101_000000/Fastq/2500-22_S01_L001_R1_001.fastq.gz',
	'tests/fake_sequencer_output_dir/220101_M00000_0000_000000000-XXXXX/Alignment_1/20220101_000000/Fastq/2500-22_S01_L001_R2_001.fastq.gz',
	'tests/fake_sequencer_output_dir/220101_M00000_0000_000000000-XXXXX/Alignment_1/20220101_000000/Fastq/2600-22-wdh_S01_L001_R1_001.fastq.gz',
	'tests/fake_sequencer_output_dir/220101_M00000_0000_000000000-XXXXX/Alignment_1/20220101_000000/Fastq/2600-22-wdh_S01_L001_R2_001.fastq.gz',
	]

# this has the python sources as inputs, for triggering change detection and caching
# even though they arent used in the cp command
# Warning, this copies all local files, not just the python sources
copy_py_sources = custom_target('copy_py_sources',
	input : pyfiles + testfiles + testdata,
	output : 'app',
	command : ['cp', '-r', '@CURRENT_SOURCE_DIR@/../app/', '@OUTDIR@'],
	install : false,
	)

buildtype = get_option('buildtype')
if buildtype == 'debug'
	message('buildtype is @0@ enabeling tests'.format(buildtype))
	containerfile = 'containers/ngs_pipeline_tests.containerfile'
	container_image = 'ngs_pipeline_container_tests.tar'
else
	message('buildtype is @0@ disabeling tests'.format(buildtype))
	containerfile = 'containers/ngs_pipeline.containerfile'
	container_image = 'ngs_pipeline_container.tar'
endif

packaging_format = get_option('packaging_format')

if packaging_format == 'container'
	# note, this runs from the meson build directory, therefore '.' as build context
	container_target = custom_target('ngs_pipeline_container',
		input : [containerfile] + pyfiles,
		output : container_image,
		depends : [copy_py_sources],
		command : [container_engine, 'build', '-t', 'ngs_pipeline_container:latest', '-f', '@INPUT0@', '-o', 'type=tar,dest=@OUTPUT@', '.'],
		build_by_default : true,
		install : false,
		)
elif packaging_format == 'rpm'
	error('not supported yet')

elif packaging_format == 'pip'
	pip_package_target = custom_target('pip_package',
		input : pyfiles,
		output : container_image,
		depends : [copy_py_sources],
		command : [python_bin, '-m', 'pip', 'wheel', '@BUILD_ROOT@/app/app'],
		build_by_default : true,
		install : false,
		)


else
	error('invalid packaging type')
endif

apppath = join_paths(meson.source_root(), 'app')
testdir = join_paths(apppath, 'tests')

if packaging_format == 'pip'
	test('pytest', python_bin, args : [
		'-m',
		'pytest', 
		apppath,
		'--testdir',
		testdir
		], 
		timeout: 600)

elif packaging_format == 'container'
	test('container_pytest_pod', 
		bash_bin,
		args : [
			'app/app/scripts/run_tests.sh'
		], 
		depends : [container_target],
		timeout: 600)
endif

#meson.add_install_script
#meson.add_dist_script
#meson.add_postconf_script


#testcombs:
#local,venv,containerized
#whitebox,blackbox (package-installed or not)
#clcbackend,wdlbackend,nextflow, or multiple
#python,cython,pypy
