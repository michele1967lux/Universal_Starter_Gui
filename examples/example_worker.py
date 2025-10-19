#!/usr/bin/env python3
"""
Example worker script for testing Universal Starter GUI.
This script performs periodic tasks and stays alive.
"""

import time
import datetime
import random


def process_task(task_id):
    """Simulate processing a task."""
    duration = random.uniform(0.5, 2.0)
    print(f"[{datetime.datetime.now()}] Processing task #{task_id}...")
    time.sleep(duration)
    print(f"[{datetime.datetime.now()}] Task #{task_id} completed in {duration:.2f}s")


def main():
    print("Example worker started")
    print("Performing periodic tasks every 5 seconds")
    print("Press Ctrl+C to stop")
    
    task_counter = 1
    
    try:
        while True:
            process_task(task_counter)
            task_counter += 1
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nWorker stopped")


if __name__ == "__main__":
    main()
