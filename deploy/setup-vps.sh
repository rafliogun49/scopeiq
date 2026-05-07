#!/usr/bin/env bash
# VPS initial bootstrap — Jetorbit Ubuntu 24.04
# Owner: Member C (C-PR8)
# Run ONCE as root immediately after VPS provisioning (PRD §23.4).
# Usage: bash deploy/setup-vps.sh

set -euo pipefail

# 1. Update system
apt update && apt upgrade -y

# 2. Create non-root user
adduser scopeiq
usermod -aG sudo scopeiq
mkdir -p /home/scopeiq/.ssh
# Paste team public keys (one per line) into authorized_keys:
# nano /home/scopeiq/.ssh/authorized_keys
chown -R scopeiq:scopeiq /home/scopeiq/.ssh
chmod 700 /home/scopeiq/.ssh
chmod 600 /home/scopeiq/.ssh/authorized_keys

# 3. Harden SSH
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart ssh

# 4. Firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# 5. Unattended security updates
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

# 6. Docker
curl -fsSL https://get.docker.com | sh
usermod -aG docker scopeiq

# 7. fail2ban (optional)
apt install -y fail2ban

# 8. Swap (recommended — 4GB RAM cuts close during Synthesizer runs, PRD §23.8)
if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

echo "Done. Switch to the scopeiq user: ssh scopeiq@<vps-ip>"
