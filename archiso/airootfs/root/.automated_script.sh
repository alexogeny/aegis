#!/usr/bin/env bash
# Aegis Linux - Live Session Setup Script
# =============================================================================
# This script runs when the live ISO boots
# =============================================================================

# Start the display manager for live session
systemctl start sddm.service

# Create live user if it doesn't exist
if ! id -u liveuser &>/dev/null; then
    useradd -m -G wheel,video,audio,network,storage,optical -s /usr/bin/fish liveuser
    echo "liveuser:liveuser" | chpasswd
fi

# Enable password-less sudo for live user
echo "liveuser ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/liveuser
chmod 440 /etc/sudoers.d/liveuser

# Copy skel to liveuser home if empty
if [[ -d /etc/skel/.config ]] && [[ ! -d /home/liveuser/.config ]]; then
    cp -r /etc/skel/.config /home/liveuser/
    chown -R liveuser:liveuser /home/liveuser
fi

# Create desktop shortcut for installer
mkdir -p /home/liveuser/Desktop
cat > /home/liveuser/Desktop/install-aegis.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Install Aegis Linux
Comment=Launch the Aegis Linux installer
Exec=sudo calamares
Icon=calamares
Terminal=false
Categories=System;
EOF
chmod +x /home/liveuser/Desktop/install-aegis.desktop
chown liveuser:liveuser /home/liveuser/Desktop/install-aegis.desktop
