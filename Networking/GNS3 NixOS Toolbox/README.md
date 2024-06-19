# NixOS Toolbox (GNS3 Template)

Custom and minimal configuration for NixOS instance, which I use when working with virtual environments created using [GNS3](https://gns3.com/).

## Getting Started

In order to use this predefined NixOS configuration in GNS3, you are required to build and install NixOS in a virtual environment first and after that import it into GNS3.

## Prerequisites

Software and/or other elements required:
* NixOS Installation Medium (Recommended: [Latest build of `Small 24.05`](https://releases.nixos.org/?prefix=nixos/24.05-small/))
* `configuration.nix` file from this repository
* Virtualization enabled in the BIOS
* Software capable of making virtual machines (Recommended: `VMware Workstation Pro` or `virt-manager (KVM + QEMU)`)
* GNS3

## Installation & Configuration

Installation process might be differ when using different platform for creating virtual machines, but some key tasks should be the same:

* Create new virtual machine (Either based on Legacy or UEFI Bios)
* Install NixOS according with the [official manual](https://nixos.org/manual/nixos/stable/#sec-installation-manual)
* Export the disk image (Remember to target the platform you are using to create GNS3 appliances and virtual machines)
* Import and create a new appliance. [Example guide on how to do it](https://www.whitewinterwolf.com/posts/2017/08/14/gns3-how-to-add-virtual-machines-end-devices-nodes/)

After that, you will be able to use the created image with GNS3. The VM will work both with GNS3 telnet or VNC connection and will auto-login as the `root` user. 