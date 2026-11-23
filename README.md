# Micro-segmentation lab guide

Website: https://0nlymohammed.github.io/ghufran-fyp-guide/

A build guide for the graduation project "Implementation of a micro-segmented network to prevent lateral movement", in English and Arabic. It builds a Kubernetes lab on one Windows laptop (kind, Cilium and Hubble inside WSL 2), attacks a small university portal on a flat network, then applies Cilium network policies and shows the same attack stopped after its first step.

What is in this repository:

- `index.html` and `ar/index.html`: the home page, a 10-stage path with a tick box for every step
- `guide/` and `ar/guide/`: the full guide, one page per chapter
- `downloads.html` and `ar/downloads.html`: links to every file below
- `files/`: the build guide and the slides as PDF, the ready project files as a ZIP, and the 12 figures as PNG
- `project/microseg/`: the same project files as the ZIP, readable here one by one

Tested versions: Windows 11, WSL 3.0.5, Ubuntu 24.04, Docker Engine 29, kind 0.33.0 with Kubernetes 1.36.4, Cilium 1.20.5, cilium CLI 0.20.3, hubble CLI 1.20.4.

Screenshot credits: the Task Manager and Snipping Tool pictures are from Microsoft Support. The PowerShell search, Run as administrator and Ubuntu user-name pictures are from Microsoft Learn (CC BY 4.0), cropped. The other screenshots were taken on the test laptop.
