python_bin = find_program('python3.11','python3.10','python3.9','python3.8')
#e = run_command('python3', 'sensitive_data_check.py', '@ROOT@', check : true)
#e = run_command('echo', 'bla')
scriptpath = join_paths(meson.source_root(), 'compliance', 'sensitive_data_check.py')

# contains white and blacklists
blacklist_mimetypes = join_paths(meson.source_root(), 'compliance', 'blacklist_mimetypes')
blacklist_files = join_paths(meson.source_root(), 'compliance', 'blacklist_files')
whitelist_files = join_paths(meson.source_root(), 'compliance', 'whitelist_files')

test('sensitive_data_check', 
	python_bin, 
	args : [scriptpath, 
		meson.source_root(),
		blacklist_mimetypes,
		blacklist_files,
		whitelist_files
		]
	)
