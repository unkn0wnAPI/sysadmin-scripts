#!/bin/bash

#
## Script Name: Unattended ArchLinux Server Deployment 
## Author:      unkn0wnAPI [github.com/unkn0wnAPI]
## Information: To be used after installing Arch Linux with archinstall
#

#
## Configuration
#
server_user="" # Name of the main administrator user
reflector_region="" # ArchLinux mirror region
zerotier_network_id="" # Auto-join given zerotier network
additional_pkgs="lolcat zsh zsh-autosuggestions zsh-syntax-highlighting" # Additional user packages you wish to install

#
## Script Start point
#
echo "======Automated Archlinux Server Deployment======"
echo "===Packages Installation==="
echo "[PART 1/5] - System Packages"
sudo pacman -S --needed --noconfirm linux-lts-headers pacman-contrib base-devel dmidecode dmraid rsync rebuild-detector dkms amd-ucode &>/dev/null

echo "[PART 2/5] - Services"
sudo pacman -S --needed --noconfirm docker docker-compose samba zerotier-one openssh &>/dev/null

echo "[PART 3/5] - Archiving & Compression"
sudo pacman -S --needed --noconfirm tar bzip2 unrar gzip unzip zip p7zip &>/dev/null

echo "[PART 4/5] - User Packages"
sudo pacman -S --needed --noconfirm eza neovim reflector rustup speedtest-cli trash-cli git dos2unix smbclient screen iperf3 &>/dev/null

echo "[PART 5/5] - Additional User Packages"
sudo pacman -S --needed --noconfirm $additional_pkgs &>/dev/null

echo "===AUR Packages Installation==="
echo "[PART 1/3] - AUR Manager"
rustup default stable &>/dev/null
git clone https://aur.archlinux.org/paru.git &>/dev/null
cd paru
makepkg -sci --noconfirm &>/dev/null
paru -S --noconfirm paru-bin &>/dev/null

echo "[PART 2/3] - Basic AUR Packages"
paru -S --noconfirm --cleanafter autojump mkinitcpio-firmware speedometer &>/dev/null

echo "[PART 3/3] - ZFS"
paru -S --noconfirm --cleanafter zfs-dkms &>/dev/null
sudo modprobe zfs
sudo depmod -a
sudo mkinitcpio -P
sudo sed -i 's/MODULES=()/MODULES=(zfs)/' /etc/mkinitcpio.conf

echo "===Operator User Adjustments==="
echo "[PART 1/2] - Add user to docker group"
sudo usermod -aG docker $server_user

echo "[PART 2/2] - Change user shell to /usr/bin/zsh"
sudo chsh -s /usr/bin/zsh $server_user
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh) --unattended" &>/dev/null

echo "===Core Services Configuration==="
echo "[PART 1/5] - Zerotier"
sudo systemctl enable zerotier-one.service --now
sudo zerotier-cli join $zerotier_network_id

echo "[PART 2/5] - Reflector"
sudo reflector -c $reflector_region -p 'https,rsync' --delay 12 --sort rate --save /etc/pacman.d/mirrorlist

echo "[PART 3/5] - Docker"
sudo systemctl enable docker.service --now

echo "[PART 4/5] - ZFS"
sudo systemctl enable zfs-mount.service zfs-import-cache.service

echo "[PART 5/5] - Samba"
sudo systemctl enable smb.service nmb.service

echo "======Automated Server Deployment was Successful======"
echo "===Manual Configuration==="
echo "Services to start after restoring configuration: "
echo " - ZFS => ZFS Scrub timer for RAID arrays"
echo "Possible missing configuration files:"
echo " - Docker container files"
echo " - Service configurations"
