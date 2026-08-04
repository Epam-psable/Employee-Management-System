import json
import glob
from collections import Counter

paths = glob.glob(r"reports/allure-results/*-result.json")
print("result_files", len(paths))

statuses = Counter()
start = None
stop = None
failed = []

for p in paths:
    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)

    st = d.get("status", "unknown")
    statuses[st] += 1

    s = d.get("start")
    e = d.get("stop")
    if s is not None:
        start = s if start is None else min(start, s)
    if e is not None:
        stop = e if stop is None else max(stop, e)

    if st in ("failed", "broken"):
        failed.append((d.get("name"), d.get("fullName")))

print("statuses", dict(statuses))
if start is not None and stop is not None:
    print("duration_ms", stop - start)
print("failed_or_broken", len(failed))
for n, fn in failed[:20]:
    print("-", n, "::", fn)
