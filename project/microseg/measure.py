# Latency with vs. without policies. Run from ~/microseg with:  .venv/bin/python measure.py
import csv
import os
import statistics
import subprocess
import time

import requests

PORTAL = "http://127.0.0.1:30080"
RUNS = 5
REQUESTS = 1000          # timed requests per endpoint per run
WARMUP = 50              # requests sent first and thrown away
ENDPOINTS = ["/news", "/api/grades"]
CONDITIONS = ["no-policies", "policies"]


def set_policies(condition):
    if condition == "policies":
        subprocess.run(["kubectl", "apply", "-f", "k8s/policies/"], check=True)
    else:
        subprocess.run(["kubectl", "delete", "-f", "k8s/policies/", "--ignore-not-found"], check=True)
    time.sleep(15)       # give Cilium time to update every pod


def login(session):
    answer = session.post(PORTAL + "/api/login", json={"username": "sara", "password": "sara2026"}, timeout=10)
    return answer.json()["token"]


def measure(session, path, token):
    times = []
    for i in range(WARMUP + REQUESTS):
        start = time.perf_counter()
        answer = session.get(PORTAL + path, headers={"Authorization": "Bearer " + token}, timeout=10)
        elapsed_ms = (time.perf_counter() - start) * 1000
        answer.raise_for_status()          # stop on any error, never time a failed request
        if i >= WARMUP:
            times.append(elapsed_ms)
    cuts = statistics.quantiles(times, n=100)   # cuts[94] = p95, cuts[98] = p99
    return [round(statistics.median(times), 2), round(cuts[94], 2), round(cuts[98], 2),
            round(statistics.mean(times), 2)]


os.makedirs("results", exist_ok=True)
session = requests.Session()

rows = []
for run_number in range(1, RUNS + 1):
    for condition in CONDITIONS:
        set_policies(condition)
        token = login(session)
        for path in ENDPOINTS:
            numbers = measure(session, path, token)
            print(run_number, condition, path, "median/p95/p99/mean ms:", numbers)
            rows.append([condition, path, run_number] + numbers)

with open("results/latency.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["condition", "endpoint", "run", "median_ms", "p95_ms", "p99_ms", "mean_ms"])
    writer.writerows(rows)

print("\nMean of the run medians:")
for path in ENDPOINTS:
    result = {}
    for condition in CONDITIONS:
        medians = [row[3] for row in rows if row[0] == condition and row[1] == path]
        result[condition] = statistics.mean(medians)
        print(f"  {path:12} {condition:12} {result[condition]:7.2f} ms  (stdev {statistics.stdev(medians):.2f})")
    overhead = result["policies"] - result["no-policies"]
    print(f"  {path:12} overhead     {overhead:7.2f} ms  ({100 * overhead / result['no-policies']:.1f} %)")
