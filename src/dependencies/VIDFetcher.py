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
                
                # Start browser with proper config
                browser = await uc.start(
                    browser_executable_path='/usr/bin/google-chrome-stable',
                    headless=True,
                    browser_args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-software-rasterizer'
                    ]
                )
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
                import traceback
                traceback.print_exc()
                return None
            finally:
                if browser:
                    try:
                        await browser.stop()
                    except:
                        pass
        
        # Run in new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(_fetch())
            return result
        except Exception as e:
            print(f"Loop error: {e}")
            return None
        finally:
            try:
                # Properly cleanup pending tasks
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                loop.close()
            except:
                pass
    
    @staticmethod
    async def fetch_vid(selection: VehicleSelectionRequest) -> Optional[dict]:
        """Async wrapper for fetch_vid_sync"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            executor,
            VIDFetcher.fetch_vid_sync,
            selection
        )