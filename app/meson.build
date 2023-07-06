container_engine = find_program('podman')
python_bin = find_program('/data/fhoelsch/.venv/bin/python3.9')

pyfiles = [
	'pyproject.toml',
	'setup.py',
	'src/__init__.py',
	'src/app/app.py',
	'src/app/config.py',
	'src/app/constants.py',
	'src/app/db.py',
	'src/app/domain_model.py',
	'src/app/filemaker_api.py',
	'src/app/__init__.py',
	'src/app/model.py',
	'src/app/parsers.py',
	'src/app/samplesheet.py',
	'src/app/tasks_impl.py',
	'src/app/tasks.py',
	'src/app/tasks_utils.py',
	'src/app/templates/pipeline_dashboard.html',
	'src/app/templates/raw_db_document.html',
	'src/app/templates/samplesheet_template.csv',
	'src/app/templates/tracking_form.html',
	'src/app/ui.py',
	'src/app/workflow_backends.py'
	]

# this has the python sources as inputs, for triggering change detection and caching
# even though they arent used in the cp command
# Warning, this copies all local files, not just the python sources
copy_py_sources = custom_target('copy_py_sources',
	input : pyfiles,
	output : 'app',
	command : ['cp', '-r', '@CURRENT_SOURCE_DIR@/../app/', '@OUTDIR@'],
	install : false,
	)

worker_infile = 'containers/ngs_pipeline_tests.containerfile'
worker_outfile = 'ngs_pipeline_test.tar'

# note, this runs from the meson build directory, therefore '.' as build context
container_target = custom_target('ngs_pipeline_container_tests',
	input : worker_infile,
	output : worker_outfile,
	depends : [copy_py_sources],
	command : [container_engine, 'build', '-t', 'ngs_pipeline_test:latest', '-f', '@INPUT@', '-o', 'type=tar,dest=@OUTPUT@', '.'],
	install : false,
	)



apppath = join_paths(meson.source_root(), 'app')
testdir = join_paths(apppath, 'tests')

test('pytest', python_bin, args : [
	'-m',
	'pytest', 
	apppath,
	'--testdir',
	testdir
	], 
	timeout: 600)

bash = find_program('bash')
test('container_pytest_pod', 
	bash,
	args : [
		'app/app/scripts/run_tests.sh'
	], 
	timeout: 600)

test('container_pytest', 
	container_engine,
	args : [
	'run',
	'--rm',
	'-ti',
	'--pod',
	'test_ngs_pipeline_pod',
	'ngs_pipeline_test:latest',
	'python3.10',
	'-m',
	'pytest', 
	'/root/app',
	'--testdir',
	'/root/app/tests',
	], 
	timeout: 600)

#meson.add_install_script
#meson.add_dist_script
#meson.add_postconf_script


#testcombs:
#local,venv,containerized
#whitebox,blackbox (package-installed or not)
#clcbackend,wdlbackend,nextflow, or multiple
#python,cython,pypy
