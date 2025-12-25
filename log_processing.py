"""
Problem 1: The Log File "Top Talker" (Data Processing)
Scenario: You are dealing with a massive legacy application log file. You need to identify potential DDoS attacks or misbehaving services by analyzing traffic patterns.

The Task: Write a Python script that reads a log file (for this exercise, assume a list of strings) where each line is in the format: "TIMESTAMP IP_ADDRESS REQUEST_PATH RESPONSE_CODE"

Example: "2023-10-27 10:01:01 192.168.1.5 /api/v1/login 200"

Your script should return the Top 3 IP addresses that have the highest number of 4xx or 5xx error codes.

Bonus: How would you handle a file that is too large to fit into memory (e.g., 50GB)?
"""

import sys
from collections import defaultdict

def read_log_file(filename):

    error_counts = defaultdict(int)

    try:
        with open(filename, 'r') as file:
            for line_num,line in enumerate(file, 1):

                clean_line = line.strip()
                if not clean_line:
                    continue

                parts = clean_line.split()

                if len(parts) != 5:
                    print(f"Skipping malformed data at line {line_num}: {clean_line}")
                    continue

                ip_address = parts[2]
                status_code_str = parts[4]

                try:
                    status_code = int(status_code_str)

                    if 400 <= status_code <= 599:
                        error_counts[ip_address] += 1

                except ValueError:
                    print(f"Skipping line {line_num}: Invalid status code '{status_code_str}'")
                    continue

        top_ips = sorted(error_counts.items(), key=lambda item: item[1], reverse=True)[:3]

        print("\n--- Top 3 IP Addresses with Most Errors ---")
        if not top_ips:
            print("No 4xx or 5xx errors found.")
        else:
            for ip, count in top_ips:
                print(f"IP: {ip:<15} | Errors: {count}")

    except FileNotFoundError:
        print(f"The file {filename} was not found.")
    except Exception as e:
        print(f"An error occurred {e}")

if __name__ == "__main__":
    log_file = "app.log"
    read_log_file(log_file)