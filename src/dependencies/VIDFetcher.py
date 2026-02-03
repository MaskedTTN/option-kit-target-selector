import nodriver as uc
from bs4 import BeautifulSoup
from typing import Optional
from models import VehicleSelectionRequest

class VIDFetcher:
    """Fetches VIDs from RealOEM using a persistent nodriver instance"""
    
    BASE_URL = "https://www.realoem.com"
    _browser = None

    @classmethod
    async def get_browser(cls):
        """Persistent browser instance with automatic restart if it crashes"""
        # Check if browser exists and is still connected
        if cls._browser is None or not cls._browser.connection or cls._browser.connection.closed:
            print("Starting (or restarting) browser instance...")
            cls._browser = await uc.start(
                headless=False,
                no_sandbox=True,
                browser_args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
            )
        return cls._browser

    @staticmethod
    async def fetch_vid(selection: VehicleSelectionRequest) -> Optional[dict]:
        """Async VID fetcher using the persistent browser instance"""
        try:
            browser = await VIDFetcher.get_browser()
            
            url = f"{VIDFetcher.BASE_URL}/bmw/enUS/select?product=P&archive=0&series={selection.series}"
            if selection.body: url += f"&body={selection.body}"
            if selection.model: url += f"&model={selection.model}"
            if selection.market: url += f"&market={selection.market}"
            if selection.production: url += f"&prod={selection.production}"
            if selection.engine: url += f"&engine={selection.engine}"
            if selection.steering: url += f"&steering={selection.steering}"

            page = await browser.get(url)
            
            # Wait for the specific element that contains the VID
            # Increasing timeout slightly for the second request
            await page.wait_for("input[name='id']", timeout=20)
            
            content = await page.get_content()
            soup = BeautifulSoup(content, 'html.parser')
            vid_input = soup.find('input', attrs={'name': 'id'})

            if vid_input and vid_input.get('value'):
                vid = vid_input['value']
                result = {
                    'vid': vid,
                    'series': selection.series,
                    'body': selection.body,
                    'model': selection.model,
                    'market': selection.market,
                    'production': selection.production,
                    'engine': selection.engine,
                    'steering': selection.steering,
                    'url': f"{VIDFetcher.BASE_URL}/bmw/enUS/partgrp?id={vid}"
                }
                return result
            
            return None

        except Exception as e:
            print(f"Scrape error details: {e}")
            # If the error is related to connection, clear the browser cache so next run restarts
            if "StopIteration" in str(e) or "connection" in str(e).lower():
                VIDFetcher._browser = None
            return None
        