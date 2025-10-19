#!/usr/bin/env python3
"""
Simple example script for testing Universal Starter GUI.
This script prints messages and exits after a short time.
"""

import time
import sys


def main():
    print("Simple example script started")
    print(f"Python version: {sys.version}")
    
    for i in range(10):
        print(f"Message {i+1}/10: Hello from Universal Starter GUI!")
        time.sleep(1)
    
    print("Simple example script completed")


if __name__ == "__main__":
    main()
