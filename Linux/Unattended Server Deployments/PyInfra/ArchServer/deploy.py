#
## Script Name: Unattended ArchLinux Server Deployment (PyInfra)
## Author:      unkn0wnAPI [https://github.com/unkn0wnAPI]
## Information: Automation for the post-deploy server configuration tasks
#

#
## Imports
#
from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts.server import User
from pyinfra.operations import pacman, server, git, systemd

#
## Configuration is done using inventory.py
#

#
## PyInfra Functions
#
@deploy("Pacman mirror preparation")
def prepare_pacman():
    pacman.update(
        name = "Updating pacman repositories",
        _sudo = True
    )

    pacman.packages(
        name = "Installing bootstrap packages",
        packages = ["archlinux-keyring", "rsync", "rebuild-detector", "reflector"],
        present = True,
        update = False,
        _sudo = True,
    )

    server.shell(
        name = "Updating arch mirrors",
        commands = [f"reflector -c {host.data.get("MIRROR_REGION")} -p https,rsync --delay 12 --sort rate --save /etc/pacman.d/mirrorlist"],
        _sudo = True
    )

    pacman.update(
        name = "Updating newly synced pacman repositories",
        _sudo = True
    )

@deploy("Package Management")
def install_packages():
    pacman.packages(
        name = "Installing system packages",
        packages = ["linux-lts-headers", "pacman-contrib", "base-devel", "dmidecode", "dkms", "amd-ucode", 
                    "linux-firmware", "lm_sensors", "curl", "e2fsprogs", "exfatprogs", "iproute2", "mtr",
                    "lsof", "smartmontools", "udisks2", "dosfstools"],
        present = True,
        update = False,
        _sudo = True,
    )

    pacman.packages(
        name = "Installing AMDGPU drivers",
        packages = ["mesa", "xf86-video-amdgpu", "vulkan-radeon", "libva-mesa-driver", "mesa-vdpau", "nvtop"],
        present = True,
        update = False,
        _sudo = True,
    )

    pacman.packages(
        name = "Installing Services packages",
        packages = ["docker", "docker-compose", "samba", "zerotier-one", "openssh", "clamav", 
                    "mariadb-clients", "openldap", "smbclient"],
        present = True,
        update = False,
        _sudo = True,
    )

    pacman.packages(
        name = "Installing Archiving & Compression packages",
        packages = ["tar", "bzip2", "unrar", "gzip", "unzip", "zip", "p7zip"],
        present = True,
        update = False,
        _sudo = True,
    )

    pacman.packages(
        name = "Installing Runners & SDK packages",
        packages = ["jre17-openjdk-headless", "jre21-openjdk-headless", "python"],
        present = True,
        update = False,
        _sudo = True,
    )

    pacman.packages(
        name = "Installing User packages",
        packages = ["eza", "neovim", "rustup", "speedtest-cli", "trash-cli", "git", "dos2unix", "screen", "iperf3",
                    "lolcat", "zsh", "zsh-autosuggestions", "zsh-syntax-highlighting", "beep", "ffmpeg", "influx-cli",
                    "speedtest-cli", "uwufetch", "yt-dlp"],
        present = True,
        update = False,
        _sudo = True,
    )

@deploy("AUR Configuration Support")
def preparing_aur_support():
    server.shell(
        name = "Installing rust toolchain",
        commands = ["rustup default stable"],
    )

    git.repo(
        name = "Downloading paru from Github",
        src = "https://aur.archlinux.org/paru.git",
        dest = f"/home/{host.get_fact(User)}/paru",
        branch = "master",
        pull = True,
        
    )

    server.shell(
        name = "Bypassing `sudo: a terminal is required to read the password` error",
        commands = [f"echo '{host.get_fact(User)} ALL = NOPASSWD: /usr/bin/pacman' >> /etc/sudoers"],
        _sudo = True
    )

    server.shell(
        name = "Building paru from source",
        commands = [f"cd /home/{host.get_fact(User)}/paru; makepkg -sci --noconfirm"]
    )

    server.shell(
        name = "Removing `paru-debug` package",
        commands = ["pacman -R paru-debug --noconfirm"],
        _sudo = True
    )

@deploy("Package Management (AUR)")
def install_aur_packages():
    server.shell(
        name = "Installing AUR packages",
        commands = ["paru -S --noconfirm --cleanafter autojump mkinitcpio-firmware telegraf-bin"],
    )

@deploy("User Configuration")
def user_configuration():
    server.shell(
        name = "Changing shell to ZSH",
        commands = [f"chsh -s /usr/bin/zsh {host.get_fact(User)}"],
        _sudo = True
    )

@deploy("Service Configuration")
def service_configuration():
    server.shell(
        name = "Joining Zerotier network",
        commands = [f"zerotier-cli join {host.data.get("ZEROTIER_NETWORK_ID")}"],
        _sudo = True
    )

    server.shell(
        name = "Installing oh-my-zsh",
        commands = [f"sh -c $(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh) --unattended"],
    )

@deploy("System service management")
def system_services():
    systemd.service(
        name = "Enabling SSH service",
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
        name = "Enabling SMB service",
        service = "smb.service",
        running = True,
        enabled = True,
       _sudo = True
    )

    systemd.service(
        name = "Enabling NMB service",
        service = "nmb.service",
        running = True,
        enabled = True,
       _sudo = True
    )

    systemd.service(
        name = "Enabling Zerotier-one service",
        service = "zerotier-one.service",
        running = True,
        enabled = True,
        _sudo = True
    )

    systemd.service(
        name = "Enabling Telegraf service",
        service = "telegraf.service",
        running = True,
        enabled = True,
        _sudo = True
    )

@deploy("Deploy Cleanup")
def session_cleanup():
    server.shell(
        name = "Removing `sudo` bypass",
        commands = [f"sed '$d' /etc/sudoers"],
        _sudo = True
    )

    server.shell(
        name = "Removing paru-src leftovers",
        commands = [f"rm /home/{host.get_fact(User)}/paru -r"],
        _sudo = True
    )
    
    server.shell(
        name = "Removing backups from `/`",
        commands = ["rm *.tgz"],
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
    session_cleanup()

#
## Init Point
#
main()