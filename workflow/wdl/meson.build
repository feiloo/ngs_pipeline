container_runtime = find_program('docker')

container1 = custom_target('container1',
	input : ['Dockerfile'],
	output : ['str'],
	command : [container_runtime, 'build', '-t', 'wdl1', '-f', '@INPUT@', '.']
	)
