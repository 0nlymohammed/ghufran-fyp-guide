#!/bin/bash
# Checks that the lab environment is ready. Run from WSL:  bash ~/microseg/check-env.sh
# Each check prints OK or FAIL. The last line counts the OKs.
passed=0
total=0

check() {
  total=$((total + 1))
  if eval "$2" >/dev/null 2>&1; then
    echo "OK    $1"
    passed=$((passed + 1))
  else
    echo "FAIL  $1"
  fi
}

check "systemd is running"                 '[ "$(ps -p 1 -o comm=)" = "systemd" ]'
check "WSL has at least 9 GB of memory"    '[ $(free -g | awk "/Mem:/ {print \$2}") -ge 9 ]'
check "WSL has 4 CPUs"                     '[ $(nproc) -ge 4 ]'
check "kernel module xt_TPROXY is loaded"  'lsmod | grep -q "^xt_TPROXY"'
check "kernel module xt_socket is loaded"  'lsmod | grep -q "^xt_socket"'
check "inotify watch limit is raised"      '[ $(sysctl -n fs.inotify.max_user_watches) -ge 524288 ]'
check "docker works without sudo"          'docker info'
check "docker is version 29"               'docker version --format "{{.Server.Version}}" | grep -q "^29\."'
check "kind is v0.33.0"                    'kind version | grep -q "v0.33.0"'
check "kubectl is v1.36"                   'kubectl version --client | grep -q "v1.36"'
check "cilium CLI is v0.20.3"              'cilium version --client | grep -q "v0.20.3"'
check "hubble CLI is v1.20.4"              'hubble version | grep -q "v1.20.4"'
check "jq is installed"                    'jq --version'
check "python venv has flask"              '~/microseg/.venv/bin/python -c "import flask, requests"'

echo "$passed of $total checks passed"
