# setting up the testserver:
opensuse leap 15.4

create a btrfs partition for podman-data:
sudo mkfs.btrfs -L podman /dev/data/podman

manually mount it:
sudo mount -t btrfs /dev/data/podman /data/podman

automatically mout it:
add to /etc/fstab:
`/dev/mapper/data-podman /data/podman btrfs defaults 0 0`




running miniwdl with rootless podman

- use my miniwdl fork that doesnt invoke podman with sudo and doesnt chown
- check if resource limit delegation is enabled for user (needed for --cpu option to work)

find /sys/fs/cgroup/* | grep "user@$(id -u).service/cgroup.controllers"

if its in a /unified/ folder, hybrid cgroups (default for opensuse leap 15.4) are used:
switch to unified:
add:
'systemd.unified_cgroup_hierarchy=1'
to '/etc/default/grub' and run 'sudo grub2-mkconfig -o /boot/grub2/grub.cfg'

now also add the systemd drop-in to enable user cgroups:

first install libcgroup
cgroup-tools

add a file with:
```
[Service]
Delegate=memory pids cpu cpuset
```
to
/etc/systemd/system/user@.service.d/delegate.conf

sources:
https://github.com/containers/podman/blob/main/troubleshooting.md#26-running-containers-with-resource-limits-fails-with-a-permissions-error
https://askubuntu.com/questions/1434209/how-can-i-enable-resource-limit-delegation-for-my-not-root-user-using-cgroups


