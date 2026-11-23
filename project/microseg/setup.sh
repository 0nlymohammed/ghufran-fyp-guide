#!/bin/bash
# One-time setup. Run from WSL:  bash ~/microseg/setup.sh
set -e
cd ~/microseg

kind create cluster --config kind-config.yaml

cilium install --version 1.20.5 \
  --set kubeProxyReplacement=false \
  --set ipam.mode=kubernetes \
  --set hubble.relay.enabled=true \
  --set hubble.ui.enabled=true
cilium status --wait --wait-duration 15m

docker pull nginx:1.28
docker pull postgres:17
mkdir -p images
docker image save --platform linux/amd64 --output images/nginx.tar nginx:1.28
docker image save --platform linux/amd64 --output images/postgres.tar postgres:17
kind load image-archive images/nginx.tar
kind load image-archive images/postgres.tar

kubectl get nodes --show-labels
