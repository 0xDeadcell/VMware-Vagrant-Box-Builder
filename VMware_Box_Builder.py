import os
import sys
import pathlib
import argparse
from subprocess import PIPE, STDOUT, run, check_call



# The files that are strictly required for a VMware machine to function are: nvram, vmsd, vmx, vmxf, and vmdk files.
def get_valid_files(vm_directory_path, verbose=False):
    os.chdir(vm_directory_path)


    # Check for metadata.json file (required for Vagrant to recognize the provider)
    if not os.path.exists(os.path.join(vm_directory_path, "metadata.json")):
        # Create metadata.json if file doesn't exist
        with open(os.path.join(vm_directory_path, "metadata.json"), 'w') as f:
            f.write("""{ "provider" : "vmware_desktop" }""")


    if verbose:
        print(f'[*] Checking \"{args.vm_directory_path}\" for valid files...')

    valid_vmware_extensions = [".nvram", ".vmsd", ".vmx", ".vmxf", ".vmdk", ".json"]
    valid_vmware_files = [pathlib.Path.joinpath(vm_directory_path, f) for f in os.listdir(vm_directory_path) if os.path.splitext(f)[1] in valid_vmware_extensions]
    
    if verbose and valid_vmware_files:
        print(f"[*] {len(valid_vmware_files)} Valid VMware files found")
        for i, valid_file in enumerate(valid_vmware_files):
            print(f"    {i+1}. {os.path.split(valid_file)[1]}")

    elif not valid_vmware_files:
        exit("[!] No valid VMware files found")

    return valid_vmware_files


def get_vdiskmanager(verbose=False):
    # Attempt to find VMware Disk Manager on the system
    try:
        if verbose:
            print("[*] Attempting to locate vdiskmanager, and the required dlls...")

        vdiskmanager_path = run('dir /a /b /s "C:\Program Files (x86)\VMware\*vdiskmanager.exe"', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True).stdout.replace("\n", "").replace('\\\\', '/')
        libeay_path = run('dir /a /b /s "C:\Program Files (x86)\VMware\*libeay32.dll"', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True).stdout.rstrip("\n").split("\n")[-1]
        ssleay_path = run('dir /a /b /s "C:\Program Files (x86)\VMware\*ssleay32.dll"', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True).stdout.rstrip("\n").split("\n")[-1]

        if verbose:
            print("[*] Required files found:")
            print(f"   1. {vdiskmanager_path}")
            print(f"   2. {libeay_path}")
            print(f"   3. {ssleay_path}")

        libeay_copy_results = run(f'copy "{libeay_path}" "{os.path.join(os.path.split(vdiskmanager_path)[0], os.path.split(libeay_path)[1])}"', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        ssleay_copy_results = run(f'copy "{ssleay_path}" "{os.path.join(os.path.split(vdiskmanager_path)[0], os.path.split(ssleay_path)[1])}"', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    except Exception as e:
        print(e)
    if not (vdiskmanager_path and libeay_path and ssleay_path):
        exit("[!] Was unable to locate vdiskmanager.exe and/or required dlls, you may download vdiskmanager.exe from 'https://kb.vmware.com/s/article/1023856'")
    
    return vdiskmanager_path


def get_box_name_from_vmx(vm_directory_path, verbose=False):
    print("[*] Box name not set, choosing box name from VMX file.")

    if not len([vmx for vmx in get_valid_files(vm_directory_path=vm_directory_path)]):
        exit("[!] VMX file not found in directory!")

    vmx_file = [vmx for vmx in get_valid_files(vm_directory_path=vm_directory_path) if os.path.splitext(vmx)[1] == ".vmx"][0] # Only get the first VMX file in the directory
    if verbose:
        print(f"[*] Found VMX File: {vmx_file}")
    with open(vmx_file, 'r') as f:
        vmx_lines = f.read().splitlines()
        

    for line in vmx_lines:
        if line.lower().startswith("displayname"):
            box_name = line.replace('"', '').strip("\n").split("=")[1].lstrip(" ").replace(" ", "_")
            print(f"[+] A Box name of '{box_name}' will be used.")
            return box_name
            
    else:
        exit("[!] Could not determine box name from VMX file, please specify one with --box_name")
                 

def create_box_archive(vm_directory_path, box_name, verbose=False, skip_shrink=False, skip_defrag=False):
    valid_vmware_files = get_valid_files(vm_directory_path=vm_directory_path, verbose=verbose)
    vdisk_manager_path = get_vdiskmanager(verbose=verbose)
    
    if not [i for i in valid_vmware_files if os.path.splitext(i)[1] == ".vmdk"]:
        exit("\n[!] Missing VMDK")

    # check for VMDKs
    for vmdk in [i for i in valid_vmware_files if os.path.splitext(i)[1] == ".vmdk"]:

        defrag_command = r'"C:\Program Files (x86)\VMware\VMware Workstation\vmware-vdiskmanager.exe" -d ' + '"' + str(vmdk) + '"'
        shrink_command = r'"C:\Program Files (x86)\VMware\VMware Workstation\vmware-vdiskmanager.exe" -k ' + '"' + str(vmdk) + '"'
        
        print(f'[*] Defragmenting VMDK "{vmdk}"')

        # Defragment the VMDKs
        if not skip_defrag:
            if verbose:
                print(f"[*] {defrag_command}")
            check_call(defrag_command, stdout=sys.stdout, stderr=STDOUT)
        print(f'[*] Shrinking VMDK "{vmdk}"')
        
        # Compress/shrink the VMDKs
        if not skip_shrink:
            if verbose:
                print(f"[*] {shrink_command}")
            check_call(shrink_command, stdout=sys.stdout, stderr=STDOUT)

    # Create the BOX Archive
    print(f"[*] Compressing files to create the BOX file archive.")
    
    files_to_compress =  ' '.join([os.path.split(i.__str__())[-1] for i in valid_vmware_files])
    if verbose:
        print(f"[*] Files to compress: {files_to_compress}")
    box_creation = run(f"tar -cvzf {str(os.path.splitext(box_name)[0])}.box {files_to_compress}", stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    print(box_creation.stdout)


def prepare_box_for_vagrant(vm_directory_path, box_name=None, verbose=False):
    if verbose:
        print(f"[*] Checking {vm_directory_path} for .Box files")
    
    if not box_name:
        box_filepath = [os.path.join(vm_directory_path, f) for f in os.listdir(vm_directory_path) if os.path.splitext(f)[1].lower() == ".box"][0]
    else:
        box_filepath = os.path.join(vm_directory_path, box_name)

    if verbose:
        print(f"[*] Provisioning '{os.path.split(box_filepath)[1].lower()}' file.")
    check_call(f"vagrant box add {box_filepath} --provider vmware_desktop --name {os.path.split(box_filepath)[1].lower()} --force", stdout=sys.stdout, stderr=STDOUT)
    #check_call(f"vagrant box list", stdout=sys.stdout, stderr=STDOUT)
    check_call(f"vagrant init {os.path.split(box_filepath)[1].lower()} --force", stdout=sys.stdout, stderr=STDOUT)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a .BOX archive from VMware files to be used with Vagrant.')
    parser.add_argument("-b", "--box_name", help="The name of the BOX file that should be created or used", action="store", default=None)
    parser.add_argument("-d", "--vm_directory_path", help="The source VM Directory that will be used to create a .BOX archive. Defaults to the current directory.", nargs='?', default=os.getcwd(), type=pathlib.Path)
    parser.add_argument("-v", "--verbose", help="Print verbose output", action="store_true")
    parser.add_argument("--skip_defrag", help="Skip defragmenting the VMDKs", action="store_true")
    parser.add_argument("--skip_shrink", help="Skip shrinking the VMDKs", action="store_true")
    parser.add_argument("--vagrantify", help="Prepare the .BOX archive for vagrant and to be uploaded", action="store_true")
    args = parser.parse_args()


    if args.vagrantify:
        prepare_box_for_vagrant(vm_directory_path=args.vm_directory_path, box_name=args.box_name, verbose=args.verbose)
        exit(0)
    

    if args.box_name:
        if args.verbose:
            print(f"[*] Box name set to {args.box_name}")
        create_box_archive(vm_directory_path=args.vm_directory_path, box_name=args.box_name, skip_defrag=args.skip_defrag, skip_shrink=args.skip_shrink, verbose=args.verbose)
    else:
        specific_box_name = get_box_name_from_vmx(vm_directory_path=args.vm_directory_path, verbose=args.verbose)
        create_box_archive(vm_directory_path=args.vm_directory_path, box_name=specific_box_name, skip_defrag=args.skip_defrag, skip_shrink=args.skip_shrink, verbose=args.verbose)