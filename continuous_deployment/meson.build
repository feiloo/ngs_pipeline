executable('update_pipeline', 'update_pipeline.sh', install : true) #install_dir : 'my/special/dir')
install_data('update_pipeline.sh', install_mode : 'r-xr-xr--', install_dir : get_option('prefix') / get_option('bindir'))

# installing as systemd system service for now, as use services don't seem to be supported
install_data('continuous_deploy.service', install_mode : 'r--r--r--', install_dir : '/etc' / 'systemd' / 'system')
install_data('continuous_deploy.timer', install_mode : 'r--r--r--', install_dir : '/etc' / 'systemd' / 'system')

meson.add_install_script('systemd_enable.sh')
