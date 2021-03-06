# VMware Vagrant Box Builder

Simplifies the process of having to manually create Vagrant BOX files for VMware



## Installation Steps

Install Vagrant
```
https://www.vagrantup.com/downloads
```

Install Vagrant VMware utility tool
```
https://www.vagrantup.com/vmware/downloads
```

Install VMware Vagrant provider plugin
```bash
vagrant plugin install vagrant-vmware-desktop
````


### Optional Install
Download vmware utility needed for defragmenting and shrinking VMDKs
```
https://kb.vmware.com/s/article/1023856
```
OR
```
https://drive.google.com/drive/folders/1XnEevr_5UN8xg7NUj0HTPAVwQwfuI6CX?usp=sharing
```

## Tool Setup

Clone the project

```bash
git clone https://github.com/0xDeadcell/VMware-Vagrant-Box-Builder.git
```

Go to the project directory

```bash
cd VMware-Vagrant-Box-Builder
```

## VMware_Box_Builder Options

```bash
VMware_Box_Builder.py -h
usage: VMware_Box_Builder.py [-h] [-b BOX_NAME] [-d [VM_DIRECTORY_PATH]] [-v] [--skip_defrag] [--skip_shrink]
                             [--vagrantify]

Create a .BOX archive from VMware files to be used with Vagrant.

options:
  -h, --help            show this help message and exit
  -b BOX_NAME, --box_name BOX_NAME
                        The name of the BOX file that should be created or used
  -d [VM_DIRECTORY_PATH], --vm_directory_path [VM_DIRECTORY_PATH]
                        The source VM Directory that will be used to create a .BOX archive. Defaults to the current
                        directory.
  -v, --verbose         Print verbose output
  --skip_defrag         Skip defragmenting the VMDKs
  --skip_shrink         Skip shrinking the VMDKs
  --vagrantify          Prepare the .BOX archive for vagrant and to be uploaded

```

## Tool usage:

Defragment and shrink the VMDKs, and then box up the VMware files required by Vagrant
```bash
python VMware_Box_Builder.py -b ParrotOS -d "C:\Users\0xDeadcell\Path\To\VM\Directory\"
```

Skip to boxing up valid files needed by packer, will choose a box name based off of the DisplayName in the .VMX file.
```bash
python VMware_Box_Builder.py --skip_defrag --skip_shrink -d "C:\Users\0xDeadcell\Path\To\VM\Directory\"
```


Provision the .BOX file to be ran with vagrant up or uploaded to hashicorp's cloud
```bash
python VMware_Box_Builder.py --vagrantify
```
For details on how you might use this tool in conjuction with building a homelab checkout my blog post on [vmware homelab automation](https://kaladin.dev/blog/vmware-homelab-automation-with-vagrant) at https://kaladin.dev/
