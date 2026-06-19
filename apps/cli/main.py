import os, csv, asyncio, argparse, logging

from typing import Dict, List, Any

from config.settings import *
from utils.file_handler import FileHandler

class CLIscraper:
    @staticmethod
    def parse_arguments():
        """
        Handles CLI input parsing configurations.
        """
        parser = argparse.ArgumentParser(description="EAN Web Scraper")
        
        parser.add_argument(
            "target",
            choices=["amazon"],
            help="E-commerce platform you want to target."
        )
        
        parser.add_argument(
            "-i", "--input",
            type=str,
            default=str(EAN_LIST),
            help="Path to a custom CSV file containing target EANS."
        )
        
        parser.add_argument(
            "-c", "--concurrency",
            type=int,
            default=5,
            help="Maximum number of concurrent network connections (Default: 5)."
        )
        
        parser.add_argument(
            "-e", "--ean",
            type=str,
            help="Pass a specific single EAN to search instead of loading a CSV file."
        )
        
        return parser.parse_args()
        
    async def run(self) -> None:
        args = self.parse_arguments()
        os.makedirs(IMAGES_DIR, exist_ok=True)
        
        # determine EAN target input type
        if args.ean:
            print(f"🎯 Single EAN Mode initialized. Targeting: [{args.ean}]")
            # wrap the single string in a list so the engine gets the array it expects
            ean_list = [args.ean.strip()]
        else:
            print(f"📋 File Mode initialized. Loading input source: {args.input}")
            try:
                ean_list = FileHandler.load_eans_from_csv(args.input)
            except Exception as e:
                print(f"Critical Error reading input source: {e}")
                return
        
        # validation guard clause
        if not ean_list:
            print("❌ EAN List/Target is empty. Task aborted.")
            return  
        
        # fire up the Engine
        if args.target == "amazon":
            from core.targets.amazon.worker import AmazonScraper
            
            # since args.concurrency defaults to 5, we can override it to 1 for a single item
            concurrency_limit = 1 if args.ean else args.concurrency
            
            engine = AmazonScraper(ean_list=ean_list, max_concurrent=concurrency_limit)
            scraped_data = await engine.main()
            
            output_path = "data/output/amazon_results.json"
            FileHandler.save_results_to_json(output_path, scraped_data)
        
if __name__ == "__main__":
    asyncio.run(CLIscraper().run())