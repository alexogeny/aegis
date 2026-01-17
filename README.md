# Aegis Linux

A security-focused Arch Linux distribution designed for privacy enthusiasts who want comprehensive protection without extensive manual configuration.

## Features

### Security
- **AppArmor** - Comprehensive mandatory access control with 1500+ profiles
- **Kernel Hardening** - Extensive sysctl configuration for kernel security
- **nftables Firewall** - Default-deny inbound policy with sensible exceptions
- **Audit Framework** - Complete system auditing for security monitoring
- **LUKS2 Encryption** - Full disk encryption with strong defaults
- **Lockdown Mode** - Kernel lockdown in confidentiality mode

### Desktop
- **Hyprland** - Modern Wayland compositor with smooth animations
- **Catppuccin Mocha** - Beautiful, consistent dark theme across all apps
- **Waybar** - Customizable status bar
- **Fuzzel** - Fast application launcher
- **Swaync** - Notification center

### Hardware Support
- **NVIDIA** - Full support via open kernel modules
- **ZFS** - Native ZFS filesystem support (optional)
- **Modern Hardware** - Intel and AMD CPU microcode included

## Quick Start

### Requirements
- 64-bit x86 processor
- 2GB RAM minimum (4GB+ recommended)
- 20GB storage minimum
- UEFI or BIOS boot

### Building the ISO

```bash
# Clone the repository
git clone https://github.com/aegis-linux/aegis.git
cd aegis

# Build the ISO (requires root)
sudo ./scripts/build-iso.sh

# Test in VM
./scripts/test-vm.sh
```

### Installation

1. Boot from the ISO
2. Click "Install Aegis Linux" on the desktop
3. Follow the Calamares installer
4. Select encryption options (LUKS recommended)
5. Reboot and enjoy!

## Security Configuration

### AppArmor Profiles

Profiles start in **complain mode** by default. To transition to enforce mode:

```bash
# Check current status
sudo aa-status

# Enforce a specific profile
sudo aa-enforce /etc/apparmor.d/usr.bin.firefox

# Enforce all profiles (after testing)
sudo aa-enforce /etc/apparmor.d/*
```

### Firewall

The nftables firewall is enabled by default with a restrictive ruleset:

```bash
# View current rules
sudo nft list ruleset

# Allow a specific port
sudo nft add rule inet aegis_filter input tcp dport 22 accept

# Make changes persistent
sudo nft list ruleset > /etc/nftables.conf
```

### Security Check

Run the built-in security checker:

```bash
sudo aegis-hardening-check
```

## Customization

### Adding Custom AppArmor Rules

Create local overrides in `/etc/apparmor.d/local/`:

```bash
# Example: Allow Firefox to access a custom directory
echo '/home/*/.custom-data/** rw,' | sudo tee /etc/apparmor.d/local/usr.bin.firefox
sudo apparmor_parser -r /etc/apparmor.d/usr.bin.firefox
```

### Modifying Kernel Parameters

Edit `/etc/sysctl.d/10-aegis-kernel.conf` or create your own file:

```bash
sudo nano /etc/sysctl.d/99-custom.conf
sudo sysctl --system
```

## Package Sources

- **Official Arch** - Core, extra, multilib repositories
- **ArchZFS** - ZFS filesystem support
- **Chaotic-AUR** - Pre-built AUR packages (Catppuccin themes, etc.)

## Directory Structure

```
aegis/
├── archiso/           # ISO build profile
│   ├── profiledef.sh  # Build configuration
│   ├── packages.x86_64# Package list
│   └── airootfs/      # Root filesystem overlay
├── scripts/           # Build and test scripts
├── pkgbuilds/         # Custom packages
└── docs/              # Documentation
```

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Arch Linux](https://archlinux.org/) - The foundation
- [Catppuccin](https://catppuccin.com/) - Beautiful color scheme
- [Hyprland](https://hyprland.org/) - Amazing Wayland compositor
- [apparmor.d](https://github.com/roddhjav/apparmor.d) - Comprehensive AppArmor profiles
