import os, asyncio, urllib.parse
from typing import List, Dict, Any

from core.targets.amazon.parser import AmazonParser

from scrapling.fetchers import StealthyFetcher, AsyncStealthySession

"""
    async def scrape_worker(self, ean:str, session: AsyncStealthySession) -> Any:
        async with self.semaphore:
            print(f"Searching Amazon for EAN [{ean}]")
            search_url = f"https://www.amazon.com.br/s?k={urllib.parse.quote_plus(ean)}"
            
            try:
                page = await session.fetch(search_url)
                if self.is_captcha_blocked(page.text) or page.status != 200:
                    return None
                
                # use parser to extract target
                search_parser = AmazonParser(page)
                product_link = search_parser.extract_product_link()
                if not product_link:
                    return None
                
                # fetch product page
                product_page = await session.fetch(product_link)
                if self.is_captcha_blocked(product_page.text) or product_page.status != 200:
                    return None
                
                # parse final data to Data Model
                product_parser = AmazonParser(product_page)
                product_model = product_parser.extract_product_details(ean, product_link)
                
                raw_data = product_model.to_dict()
                
                # handle image downloader
                if raw_data.get("img_url"):
                    filename = f"AMZ_{ean}.jpg" 
                    try:
                        img_response = await session.fetch(raw_data["img_url"])
                        # Handle saving files cleanly in an async block here...
                        raw_data["image_filename"] = filename
                    except Exception:
                        raw_data["image_filename"] = None
                else:
                    raw_data["image_filename"] = None

                raw_data.pop("img_url", None)
                return raw_data
                
            except Exception as e:
                print(f"Error on Amazon engine for EAN [{ean}]")
                return None
        
    async def main(self) -> List[Dict[str, Any]]:
        print(f"Launching amazon engine with {len(self.ean_list)} items.")
        
        async with AsyncStealthySession(headless=True) as session:
            tasks = [
                asyncio.create_task(self.scrape_worker(ean, session))
                for ean in self.ean_list
            ]
            
            # gather results from all workers
            results = await asyncio.gather(*tasks)
            
            clean_results = [
                res for res in results
                if res is not None and not isinstance(res, Exception)
            ]
            
            print(f"Target run completed. Sucessfully scraped {len(clean_results)}")
            
            return clean_results
"""