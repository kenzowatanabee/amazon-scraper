import os, csv, asyncio

from typing import Dict, List, Any

from config.config import *
from file_handler import FileHandler

class AmazonScraper:
    def __init__(self) -> None:
        try:
            print(f"Loading EAN list: {EAN_LIST}")
            self.ean_list: List = FileHandler.load_eans_from_csv(str(EAN_LIST))
            
        except Exception as e:
            print(f"Error loading EANS: {e}")
        
    async def main(self) -> None:
        if not self.ean_list: 
            return
        else:
            print("Starting Amazon Scraper... \n" + "-" * 40)
        
        os.makedirs(IMAGES_DIR, exist_ok=True)
        
        semaphore = asyncio.Semaphore(5)
        tasks = []
        nested_results = await asyncio.gather(*tasks)
        
if __name__ == "__main__":
    asyncio.run(AmazonScraper().main())