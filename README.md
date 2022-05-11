# VMware Vagrant Box Builder

Simplifies the process of having to manually create Vagrant BOX files for VMware


## Installation Steps

Clone the project

```bash
git clone https://github.com/0xDeadcell/VMware-Vagrant-Box-Builder.git
```

Go to the project directory

```bash
cd VMware-Vagrant-Box-Builder
```

```bash
python VMware_Box_Builder.py -h

usage: VMware_Box_Builder.py [-h] [-b BOX_NAME] [-d [VM_DIRECTORY_PATH]] [-v] [--skip_defrag] [--skip_shrink]

Create a .BOX archive from VMware files to be used with Vagrant.

options:
  -h, --help            show this help message and exit
  -b BOX_NAME, --box_name BOX_NAME
                        The name of the BOX file that should be created
  -d [VM_DIRECTORY_PATH], --vm_directory_path [VM_DIRECTORY_PATH]
                        The source VM Directory that will be used to create a .BOX archive. Defaults to the current directory.
  -v, --verbose         Print verbose output
  --skip_defrag         Skip defragmenting the VMDKs
  --skip_shrink         Skip shrinking the VMDKs
```

## Example usage:


```bash
python VMware_Box_Builder.py -b ParrotOS -d "C:\Users\0xDea\VM\Directory\"

```
For deails on how you might use this tool in conjuction with building a homelab checkout my blog post on (vmware-homelab-automation)[https://kaladin.dev/blog/vmware-homelab-automation-with-vagrant/] at https://kaladin.dev
