#!/bin/bash
# Checks that the portal still works for real users. Run from WSL:  bash ~/microseg/check-portal.sh
# Each check prints OK or FAIL. The last line counts the OKs.
PORTAL=http://127.0.0.1:30080
passed=0

check() {
  if [ "$2" = "$3" ]; then
    echo "OK    $1"
    passed=$((passed + 1))
  else
    echo "FAIL  $1 (expected '$3', got '$2')"
  fi
}

check "portal page loads" "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 $PORTAL/)" "200"
check "news list has 3 items" "$(curl -s --max-time 5 $PORTAL/news | jq length)" "3"

TOKEN=$(curl -s --max-time 5 -H 'Content-Type: application/json' -d '{"username":"sara","password":"sara2026"}' $PORTAL/api/login | jq -r .token)
check "sara can log in" "${#TOKEN}" "32"
check "sara sees her profile" "$(curl -s --max-time 5 -H "Authorization: Bearer $TOKEN" $PORTAL/api/profile | jq -r .full_name)" "Sara Ahmed"
check "sara sees her 2 grades" "$(curl -s --max-time 5 -H "Authorization: Bearer $TOKEN" $PORTAL/api/grades | jq length)" "2"
check "ops can open the admin panel" "$(kubectl -n campus exec deploy/ops -- curl -s --max-time 5 http://admin:5002/users | jq length)" "4"

echo "PORTAL: $passed/6 OK"
