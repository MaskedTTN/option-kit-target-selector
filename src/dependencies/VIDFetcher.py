from models import VehicleSelectionRequest
from typing import Optional

import asyncio
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=4)

class VIDFetcher:
    """Fetches VIDs from RealOEM using nodriver"""
    
    BASE_URL = "https://www.realoem.com"
    
    @staticmethod
    def fetch_vid_sync(selection: VehicleSelectionRequest) -> Optional[dict]:
        """Synchronous VID fetcher (runs in thread pool)"""
        import nodriver as uc
        
        async def _fetch():            
            browser = None
            try:
                # Build URL
                url = f"{VIDFetcher.BASE_URL}/bmw/enUS/select?product=P&archive=0&series={selection.series}"
                
                if selection.body:
                    url += f"&body={selection.body}"
                if selection.model:
                    url += f"&model={selection.model}"
                if selection.market:
                    url += f"&market={selection.market}"
                if selection.production:
                    url += f"&prod={selection.production}"
                if selection.engine:
                    url += f"&engine={selection.engine}"
                if selection.steering:
                    url += f"&steering={selection.steering}"
                
                print(f"Fetching: {url}")
                
                # Start browser
                browser = await uc.start()
                page = await browser.get(url)
                await asyncio.sleep(10)
                
                # Get HTML and parse
                html = await page.get_content()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find VID in hidden input
                vid_input = soup.find('input', type="hidden")

                if vid_input and vid_input.get('value'):
                    vid = vid_input['value']
                    print(f"Found VID: {vid}")

                    # Just return the data, don't save here
                    return {
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
                else:
                    print("VID not found on page")
                    return None
                    
            except Exception as e:
                print(f"Error fetching VID: {e}")
                return None
            finally:
                if browser:
                    browser.stop()
        
        # Run in new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_fetch())
        finally:
            loop.close()
    
    @staticmethod
    async def fetch_vid(selection: VehicleSelectionRequest) -> Optional[dict]:
        """Async wrapper for fetch_vid_sync"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            executor,
            VIDFetcher.fetch_vid_sync,
            selection
        )