
import subprocess
import sys

def run_test(date, time, gender, target):
    cmd = [
        ".venv/bin/python", "scripts/generate_report.py",
        "--date", date,
        "--time", str(time),
        "--gender", gender,
        "--target", target
    ]
    print(f"Testing: {date} {time} {gender} for target {target}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FAILED: {result.stderr}")
        return False
    print("PASSED")
    return True

if __name__ == "__main__":
    tests = [
        ("1998-10-05", 1, "男", "2026-04-03"),
        ("1985-06-12", 5, "女", "2024-01-01"),
        ("2000-01-01", 0, "男", "2023-12-31"),
    ]
    
    all_passed = True
    for t in tests:
        if not run_test(*t):
            all_passed = False
            
    if not all_passed:
        sys.exit(1)
    print("\nAll baseline tests passed successfully.")
