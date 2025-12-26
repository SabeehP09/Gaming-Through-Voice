import subprocess
import sys

result = subprocess.run([sys.executable, "test_performance.py"], env={"PYTEST_CURRENT_TEST": ""})
sys.exit(result.returncode)
