p = find_program('/data/fhoelsch/.venv/bin/python3.9')
#e = run_command('python3', 'sensitive_data_check.py', '@ROOT@', check : true)
#e = run_command('echo', 'bla')
apppath = join_paths(meson.source_root(), 'app')

test('pytest', p, args : [
	'-m',
	'pytest', 
	apppath,
	])
