#
## Script Name:  Unattended ArchLinux Server Deployment (PyInfra)
## Author:       unkn0wnAPI [https://github.com/unkn0wnAPI]
## Contributors: Jakub Majcherski [https://github.com/majcher01]
## Information:  Automation for the post-deploy server configuration tasks
#

#
## Imports
#
from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts.server import User
from pyinfra.facts.files import Directory
from pyinfra.operations import pacman, server, git, systemd, files

#
## Configuration is done using inventory.py
#

#
## PyInfra Functions
#
@deploy("Initial pacman Operations")
def prepare_pacman():
    pacman.packages(
        name = "Installing initial packages",
        packages = ["archlinux-keyring", "rsync", "rebuild-detector", "reflector"],
        present = True,
        update = True,
        _sudo = True
    )

    server.shell(
        name = "Changing pacman mirrors to the fastest available in the specified region",
        commands = [f"reflector -c {host.data.get("MIRROR_REGION")} -p https,rsync --delay 12 --sort rate --save /etc/pacman.d/mirrorlist"],
        _sudo = True
    )

    pacman.update(
        name = "Syncing local mirror cache with remote sources",
        _sudo = True
    )

@deploy("Packages Installation")
def install_packages():
    pacman.packages(
        name = "System",
        packages = [
            "linux-lts-headers", "pacman-contrib", "base-devel", "dmidecode",
            "dkms", "amd-ucode", "linux-firmware", "lm_sensors", "curl",
            "e2fsprogs", "exfatprogs", "iproute2", "mtr", "lsof", "smartmontools",
            "udisks2", "dosfstools", "less", "wget", "inetutils"],
        present = True,
        update = False,
        _sudo = True
    )

    pacman.packages(
        name = "AMD APU/GPU",
        packages = [
            "mesa", "xf86-video-amdgpu", "vulkan-radeon", "libva-mesa-driver",
            "mesa-vdpau", "nvtop", "radeontop"],
        present = True,
        update = False,
        _sudo = True
    )

    pacman.packages(
        name = "Services",
        packages = [
            "docker", "docker-compose", "samba", "zerotier-one", "openssh",
            "clamav", "mariadb-clients", "openldap", "smbclient", "vsftpd"],
        present = True,
        update = False,
        _sudo = True
    )

    pacman.packages(
        name = "Archiving & Compression",
        packages = ["tar", "bzip2", "unrar", "gzip", "unzip", "zip", "p7zip"],
        present = True,
        update = False,
        _sudo = True
    )

    pacman.packages(
        name = "Code Runtime",
        packages = ["jre17-openjdk-headless", "jre21-openjdk-headless", "python", "rustup"],
        present = True,
        update = False,
        _sudo = True
    )

    pacman.packages(
        name = "User Specific",
        packages = ["eza", "neovim", "speedtest-cli", "trash-cli", "git",
            "dos2unix", "screen", "iperf3","lolcat", "zsh", "zsh-autosuggestions",
            "zsh-syntax-highlighting", "beep", "ffmpeg", "influx-cli", "uwufetch",
            "yt-dlp", "duf", "htop", "ncdu", "borg"],
        present = True,
        update = False,
        _sudo = True
    )

@deploy("AUR Integration")
def preparing_aur_support():
    files.directory(
        name=f"Creating .local directory",
        path=f'/home/{host.get_fact(User)}/.local',
        present=True,
        group=host.data.get("ssh_user"),
        user=host.data.get("ssh_user")
    )

    server.shell(
        name = "Fixing ownership of the `.local` user folder",
        commands = [f"chown {host.get_fact(User)}:{host.get_fact(User)} /home/{host.get_fact(User)}/.local -R"],
        _sudo = True
    )

    server.shell(
        name = "Installing rust toolchain",
        commands = ["rustup default stable"],
    )

    git.repo(
        name = "Downloading `paru` from Github",
        src = "https://aur.archlinux.org/paru.git",
        dest = f"/home/{host.get_fact(User)}/paru",
        branch = "master",
        pull = True
    )

    server.shell(
        name = "Bypassing `sudo: a terminal is required to read the password`",
        commands = [f"echo '{host.get_fact(User)} ALL = NOPASSWD: /usr/bin/pacman' >> /etc/sudoers"],
        _sudo = True
    )

    server.shell(
        name = "Building `paru` from source",
        commands = [f"cd /home/{host.get_fact(User)}/paru; makepkg -sci --noconfirm"]
    )

    server.shell(
        name = "Removing `paru-debug` package",
        commands = ["pacman -R paru-debug --noconfirm"],
        _sudo = True
    )

@deploy("Packages Installation (AUR)")
def install_aur_packages():
    server.shell(
        name = "Services & Firmware",
        commands = ["paru -S --noconfirm --cleanafter mkinitcpio-firmware telegraf-bin"],
    )

    server.shell(
        name = "User Specific",
        commands = ["paru -S --noconfirm --cleanafter autojump"],
    )

    server.shell(
        name = "ZFS Modules",
        commands = ["paru -S --noconfirm --cleanafter zfs-dkms zfs-utils"]
    )

@deploy("User Environment Configuration")
def user_configuration():
    server.shell(
        name = "Changing shell to ZSH",
        commands = [f"chsh -s /usr/bin/zsh {host.get_fact(User)}"],
        _sudo = True
    )

    server.shell(
        name = "Joining `docker` system group",
        commands = [f"usermod -aG docker {host.get_fact(User)}"],
        _sudo = True
    )

@deploy("Service Preparation")
def service_configuration():
    if host.data.get("ZEROTIER_NETWORK_ID") != "":
        server.shell(
            name = "Joining Zerotier network",
            commands = [f"zerotier-cli join {host.data.get("ZEROTIER_NETWORK_ID")}"],
            _sudo = True
        )

    server.shell(
        name = "Enabling telegraf docker integration",
        commands = ["usermod -aG docker telegraf"],
        _sudo = True
    )

@deploy("System Configuration")
def system_services():
    systemd.service(
        name = "Enabling SSH",
        service = "sshd.service",
        running = True,
        enabled = True,
        _sudo = True
    )

    systemd.service(
        name = "Enabling Docker container support",
        service = "docker.service",
        running = True,
        enabled = True,
        _sudo = True
    )

    systemd.service(
        name = "Enabling SMB",
        service = "smb.service",
        running = True,
        enabled = True,
       _sudo = True
    )

    systemd.service(
        name = "Enabling NMB",
        service = "nmb.service",
        running = True,
        enabled = True,
       _sudo = True
    )

    systemd.service(
        name = "Enabling Zerotier",
        service = "zerotier-one.service",
        running = True,
        enabled = True,
        _sudo = True
    )

    systemd.service(
        name = "Enabling Telegraf",
        service = "telegraf.service",
        running = True,
        enabled = True,
        _sudo = True
    )

    systemd.service(
        name = "Enabling vsftpd",
        service = "vsftpd.service",
        running = True,
        enabled = True,
        _sudo = True
    )

    server.shell(
        name = "Creating SWAP file",
        commands = [f"mkswap -U clear --size {host.data.get("SWAPFILE_SIZE")} --file /swapfile"],
        _sudo = True
    )

    server.shell(
        name = "Enabling SWAP file",
        commands = ["swapon /swapfile", "echo '/swapfile none swap defaults 0 0' >> /etc/fstab"],
        _sudo = True
    )

    server.shell(
        name = "Setting `LC_TIME` to user defined locale",
        commands = [f"localectl set-locale LC_TIME={host.data.get("LC_TIME_LOCALE")}"],
        _sudo = True
    )

    server.shell(
        name = "Setting `net.ipv4.tcp_congestion_control` to `bbr`",
        commands = [
            "echo 'tcp_bbr' > /etc/modules-load.d/modules.conf",
            "echo 'net.core.default_qdisc=fq' > /etc/sysctl.d/bbr.conf",
            "echo 'net.ipv4.tcp_congestion_control=bbr' >> /etc/sysctl.d/bbr.conf"],
        _sudo = True
    )

    server.shell(
        name = "Disabling system ability to sleep & hibernate",
        commands = [
            "mkdir /etc/systemd/sleep.conf.d",
            "echo '[Sleep]' > /etc/systemd/sleep.conf.d/disable-sleep.conf",
            "echo 'AllowSuspend=no' >> /etc/systemd/sleep.conf.d/disable-sleep.conf",
            "echo 'AllowHibernation=no' >> /etc/systemd/sleep.conf.d/disable-sleep.conf",
            "echo 'AllowHybridSleep=no' >> /etc/systemd/sleep.conf.d/disable-sleep.conf",
            "echo 'AllowSuspendThenHibernate=no' >> /etc/systemd/sleep.conf.d/disable-sleep.conf"],
        _sudo = True
    )

    server.shell(
        name="Add zfs to mkinitcpio.conf MODULES=() line if not present",
        commands=[r"sed -i '/^MODULES=/ {/zfs/! s/)/ zfs)/}' /etc/mkinitcpio.conf"],
        _sudo = True
    )

    server.shell(
        name="Regenerate initramfs with mkinitcpio for ZFS Modules",
        commands=["mkinitcpio -P"],
        _sudo = True
    )

    systemd.service(
        name = "Enabling ZFS",
        service = "zfs.target",
        running = True,
        enabled = True,
        _sudo = True
    )

    systemd.service(
        name = "Enabling ZFS Import Scan",
        service = "zfs-import-scan.service",
        running = True,
        enabled = True,
        _sudo = True
    )

    systemd.service(
        name = "Enabling ZFS Volume Wait",
        service = "zfs-volume-wait.service",
        running = True,
        enabled = True,
        _sudo = True
    )


@deploy("Post-deployment Tasks")
def post_deployment():
    server.shell(
        name = "Removing sudo bypass",
        commands = [f"sed -i '/NOPASSWD/d' /etc/sudoers"],
        _sudo = True
    )

    server.shell(
        name = "Removing `paru-src` leftovers",
        commands = [f"rm /home/{host.get_fact(User)}/paru -r"],
        _sudo = True
    )

    server.shell(
        name = "Removing `pam_motd.so` from /etc/pam.d/system-login",
        commands = ["cp /etc/pam.d/system-login /etc/pam.d/system-login.bak", "sed -i '/pam_motd.so/d' /etc/pam.d/system-login"],
        _sudo = True
    )

    server.shell(
        name = "Changing systemd-boot timeout value to 0",
        commands = ["sed -i 's/3/0/' /boot/loader/loader.conf"],
        _sudo = True
    )

    server.shell(
        name = "Adding hostname & IP to login screen",
        commands = [
            "echo '===SERVER INFORMATION===' >> /etc/issue",
            'printf "Hostname: \\cdx" >> /etc/issue', # PyInfra changes \\n to \n (newline), this is a bypass which will be fixed with `sed`
            "echo -e '\nIPv4: \\4\n' >> /etc/issue",
            "sed -i 's/cdx/n/' /etc/issue"],
        _sudo = True
    )

#
## Deployment execution tree
#
def main():
    prepare_pacman()
    install_packages()
    preparing_aur_support()
    install_aur_packages()
    user_configuration()
    system_services()
    service_configuration()
    post_deployment()

#
## Init Point
#
main()
