#!/bin/bash
# Installs everything the lab needs inside Ubuntu: Docker, kind, kubectl, cilium, hubble, jq and Python.
# Run it once, from the microseg folder:  bash install-tools.sh
# It asks for your Ubuntu password once (for sudo). It takes about 5 to 10 minutes.
set -e

echo "== 1/6 Raising the file-watch limits kind needs"
echo -e "fs.inotify.max_user_watches=524288\nfs.inotify.max_user_instances=512" | sudo tee /etc/sysctl.d/99-kind.conf >/dev/null
sudo sysctl --system >/dev/null

echo "== 2/6 Installing curl, jq and Python's venv"
sudo apt-get update -qq
sudo apt-get install -y -qq ca-certificates curl jq python3-venv >/dev/null

echo "== 3/6 Installing Docker Engine from Docker's own repository"
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null <<EOT
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOT
sudo apt-get update -qq
sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin >/dev/null
sudo usermod -aG docker "$USER"

echo "== 4/6 Installing kind v0.33.0 and kubectl v1.36.6"
cd /tmp
curl -fsSLo kind https://kind.sigs.k8s.io/dl/v0.33.0/kind-linux-amd64
sudo install -m 0755 kind /usr/local/bin/kind
curl -fsSLO https://dl.k8s.io/release/v1.36.6/bin/linux/amd64/kubectl
curl -fsSLO https://dl.k8s.io/release/v1.36.6/bin/linux/amd64/kubectl.sha256
echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check
sudo install -m 0755 kubectl /usr/local/bin/kubectl

echo "== 5/6 Installing the cilium (v0.20.3) and hubble (v1.20.4) commands"
curl -fsSL --remote-name-all https://github.com/cilium/cilium-cli/releases/download/v0.20.3/cilium-linux-amd64.tar.gz{,.sha256sum}
sha256sum --check cilium-linux-amd64.tar.gz.sha256sum
sudo tar xzfC cilium-linux-amd64.tar.gz /usr/local/bin
curl -fsSL --remote-name-all https://github.com/cilium/hubble/releases/download/v1.20.4/hubble-linux-amd64.tar.gz{,.sha256sum}
sha256sum --check hubble-linux-amd64.tar.gz.sha256sum
sudo tar xzfC hubble-linux-amd64.tar.gz /usr/local/bin
rm -f kind kubectl kubectl.sha256 cilium-linux-amd64.tar.gz* hubble-linux-amd64.tar.gz*

echo "== 6/6 Creating the Python environment for the dashboard"
cd ~/microseg
python3 -m venv .venv
.venv/bin/pip install --quiet flask==3.1.0 requests==2.32.3

echo
echo "DONE. Now close this Ubuntu window, run   wsl --terminate Ubuntu-24.04   in PowerShell,"
echo "open Ubuntu again and run:   bash ~/microseg/check-env.sh"
