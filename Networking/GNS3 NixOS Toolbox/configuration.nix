#
## Script Name: NixOS Toolbox 
## Author:      unkn0wnAPI [https://github.com/unkn0wnAPI]
## Information: Custom NixOS Configuration for use in GNS3 environments.
#

{ config, lib, pkgs, ... }:

{
  imports = [ ./hardware-configuration.nix ];

  # Use the systemd-boot EFI boot loader.
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  # Allow access to PTY over serial (gns3 telnet)
  boot.kernelParams = [ "console=ttyS0,115200n8" ];
  systemd.services."serial-getty@ttyS0" = {
    enable = true;
    wantedBy = [ "getty.target" ];
    serviceConfig.Restart = "always";
  };

  # Systemd Configuration
  systemd.enableEmergencyMode = false;
  systemd.sleep.extraConfig = ''
    AllowSuspend=no
    AllowHibernation=no
  '';

  # NTP Configuration
  services.timesyncd = {
    enable = true;
    servers = [ "time.cloudflare.com" "0.nixos.pool.ntp.org" ];
  };

  # Networking
  networking.hostName = "nixtoolbox";
  networking.firewall.enable = false;
  networking = {
    useDHCP = true;
    useNetworkd = true;
  };

  # Networking Kernel Tweaks
  boot.kernel.sysctl = {
    "net.core.default_qdisc" = "fq";
    "net.ipv4.tcp_congestion_control" = "bbr";
  };

  # Disable containers
  boot.enableContainers = false;

  # Hardware Configuration
  hardware.cpu = {
    intel.updateMicrocode = true;
    amd.updateMicrocode = true;
  };

  # Sound Configuration
  xdg.sounds.enable = false;

  # Timezone and keyboard
  time.timeZone = "Europe/Warsaw";
  i18n.defaultLocale = "en_US.UTF-8";

  # Packages
  environment.systemPackages = with pkgs; [
    microcodeIntel
    microcodeAmd
    curl
    iperf
    inetutils
    mtr
    dig
    bash
    screen
    newt
    bash-completion
    iproute2
  ];

  # Documentation Configuration
  documentation = {
    dev.enable = false;
    man.enable = false;
    nixos.enable = false;
  };

  # Font Configuration
  fonts.fontconfig.enable = false;

  # SUID Fixes for MTR
  programs.mtr.enable = true;
  
  # Enable autologin
  services.getty.autologinUser = "root";
  
  # Enable TRIM
  services.fstrim.enable = true;

  # Enable deduplication and optimization of nix store
  nix.settings.auto-optimise-store = true;

  # SYSTEM VARIABLES DO NOT EDIT !
  system.copySystemConfiguration = true;
  system.stateVersion = "24.05";
}

