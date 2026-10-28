import os
import subprocess
import sys

def run():
    backend_dir = r"d:\KLH-Y3-ODD-SEM\CNAD\CNAD Project\CloudChange\backend"
    try:
        # Check python path
        python_exe = sys.executable
        print(f"Using python: {python_exe}")
        
        # Run pytest
        result = subprocess.run(
            [python_exe, "-m", "pytest", "tests/"],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        print(f"Return code: {result.returncode}")
    except Exception as e:
        print(f"Failed to run pytest: {e}")

if __name__ == "__main__":
    run()
