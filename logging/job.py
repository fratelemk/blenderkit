"""
Simulate a job ending in error
"""


import sys, time


for i in range(1000):
    print(f"P:{float(i)/1000}")
    sys.stdout.flush()
    time.sleep(0.01)

sys.exit(0)
