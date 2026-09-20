from __future__ import annotations

import time

from mlops_platform.api.app import infer


def main() -> None:
    start = time.time()
    for _ in range(200):
        infer({"user_id": "perf", "features": {"f1": 1.0, "f2": 2.0}})
    duration = time.time() - start
    assert duration < 2.0, f"smoke load too slow: {duration:.3f}s"
    print(f"load smoke passed: {duration:.3f}s")


if __name__ == "__main__":
    main()
