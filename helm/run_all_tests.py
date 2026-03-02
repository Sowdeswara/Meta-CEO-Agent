"""Run all HELM test modules and report summary for CI."""

import subprocess
import sys
import glob


def run_test(path):
    print(f"\n=== Running {path} ===")
    result = subprocess.run([sys.executable, path], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    return result.returncode


def main():
    tests = glob.glob('helm/tests/test_*.py')
    failures = 0
    for t in tests:
        ret = run_test(t)
        if ret != 0:
            failures += 1
    print(f"\n=== SUMMARY ===")
    print(f"Total tests: {len(tests)}")
    print(f"Failures: {failures}")
    if failures > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
