import os, asyncio, logging, urllib.parse
from typing import List, Dict, Any

from core.targets.amazon.parser import AmazonParser
from utils.logger import setup_custom_logger
from utils.file_handler import FileHandler
from config.settings import *

from scrapling.fetchers import AsyncFetcher

logging.getLogger("scrapling").setLevel(logging.CRITICAL)
logging.getLogger("scrapling.fetchers").setLevel(logging.CRITICAL)

class AmazonScraper:
    def __init__(self, ean_list: List[str], max_concurrent: int) -> None:
        self.ean_list = ean_list
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        self.logger = setup_custom_logger(name="AmazonEngine")
        
        AsyncFetcher.adaptive = True
        
    def is_captcha_blocked(self, text_content: str) -> bool:
        return "captcha" in text_content.lower()       
    
    async def scrape_worker(self, ean: str) -> Any:
        async with self.semaphore:
            self.logger.info(f"Tracking Amazon for EAN[{ean}]")
            search_url = f"https://www.amazon.com.br/s?k={urllib.parse.quote_plus(ean)}"
            
            try:
                page = await AsyncFetcher.get(search_url)
                if self.is_captcha_blocked(page.text) or page.status != 200:
                    self.logger.error(f"Failed processing processing EAN [{ean}], captcha or connection error.")
                
                search_parser = AmazonParser(page)
                product_link = search_parser.extract_product_link()
                if not product_link:
                    return None
                
                product_page = await AsyncFetcher.get(product_link)
                if self.is_captcha_blocked(product_page.text) or product_page.status != 200:
                    return None
                
                product_parser = AmazonParser(product_page)
                product_model = product_parser.extract_product_details(ean, product_link)
                
                raw_data = product_model.to_dict()
                
                if raw_data.get("img_url"):
                    filename = f"AMZ_{ean}.jpg" 
                    try:
                        img_response = await AsyncFetcher.get(raw_data["img_url"])
                        await asyncio.to_thread(FileHandler.save_image_to_disk, IMAGES_DIR, filename, img_response.body)
                        raw_data["image_filename"] = filename
                    except Exception:
                        raw_data["image_filename"] = None
                else:
                    raw_data["image_filename"] = None

                raw_data.pop("img_url", None)
                
                self.logger.info(f"Amazon Data saved for EAN [{ean}]")
                
                return raw_data
                
            except Exception as e:
                self.logger.error(f"Failed processing EAN [{ean}] due to error: {e}")
                return None
        
    async def main(self) -> List[Dict[str, Any]]:
        print(f"Starting AsyncFetcher engine with {len(self.ean_list)} items.")
        
        tasks = [
            asyncio.create_task(self.scrape_worker(ean))
            for ean in self.ean_list
        ]
        
        results = await asyncio.gather(*tasks)
        
        clean_results = [
            res for res in results
            if res is not None and not isinstance(res, Exception)
        ]
        
        print(f"Target run completed. Successfully scraped {len(clean_results)}")
        return clean_results