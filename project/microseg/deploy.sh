#!/bin/bash
# Build, load and (re)deploy the app. Deletes namespace campus first, so the DB is reset
# and all policies are gone (flat network). Run:  bash ~/microseg/deploy.sh
set -e
cd ~/microseg

docker build -t campus-app:1.0 apps/
docker build -t campus-news:1.0 -f apps/Dockerfile.news apps/
mkdir -p images
docker image save --platform linux/amd64 --output images/campus-app.tar campus-app:1.0
docker image save --platform linux/amd64 --output images/campus-news.tar campus-news:1.0
kind load image-archive images/campus-app.tar
kind load image-archive images/campus-news.tar

kubectl delete namespace campus --ignore-not-found
kubectl create namespace campus
kubectl -n campus create configmap frontend-files --from-file=frontend/
kubectl -n campus create configmap db-init --from-file=db/init.sql
kubectl apply -f k8s/app.yaml
kubectl -n campus wait --for=condition=Available deployment --all --timeout=180s
kubectl -n campus get pods -o wide
