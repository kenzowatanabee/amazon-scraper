import urllib.parse
from typing import Optional, List, Dict
from scrapling import Selector
from core.targets.amazon.models import AmazonProduct

class AmazonParser:
    def __init__(self, page_selector: Selector) -> None:
        self.selector = page_selector
        
    def extract_product_link(self) -> Optional[str]:
        """
        Parses the search result page to locate the product detail page link.
        """
        
        links = self.selector.xpath('//a[contains(@href, "/dp/")]/@href').getall()
        product_link = next(
            (f"https://www.amazon.com.br{l.split('?')[0]}" for l in links if "/dp/" in l and "/sspa/" not in l), 
            None
        )
        
        return product_link
    
    def extract_product_details(self, ean: str, product_url: str) -> AmazonProduct:
        """
        Parses the actual product detail page into an AmazonProduct data model.
        """
        
        # title extraction
        raw_title = self.selector.xpath('//*[@id="productTitle"]/text()').get()
        title = raw_title.strip() if raw_title else f"AMZ_PRODUCT_{ean}"
        
        # price extraction
        price_block = self.selector.xpath("//span[@aria-hidden='true']")
        w = price_block.xpath(".//span[@class='a-price-whole']/text()").get()
        f = price_block.xpath(".//span[@class='a-price-fraction']/text()").get()
        price_brl = float(f"{w.replace(',', '').replace('.', '').strip()}.{f}") if w and f else None
        
        # image url extraction
        img_url = self.selector.xpath('//*[@id="landingImage"]/@data-old-hires').get() or self.selector.xpath('//*[@id="landingImage"]/@src').get()
        
        # specifications extraction
        # fallback 1: normal micro-spacing tables
        specs = {}
        for row in self.selector.xpath('//table[contains(@class, "a-normal") and contains(@class, "a-spacing-micro")]//tr'):
            k = "".join(row.xpath('./td[1]//text()').getall())
            v = "".join(row.xpath('./td[2]//text()').getall())
            if k and v: specs[k.replace("\u200e", "").strip()] = v.replace("\u200e", "").strip()
            
        # fallback2: general product details table
        if not specs:
            for row in self.selector.xpath('//table[contains(@class, "prodDetTable") or contains(@id, "productDetails")]//tr'):
                k = "".join(row.xpath('.//th//text()').getall())
                v = "".join(row.xpath('.//td//text()').getall())
                if k and v: specs[k.replace("\u200e", "").strip()] = v.replace("\u200e", "").strip()
                
        # fallback 3: bullet points lists
        if not specs:
            for bullet in self.selector.xpath('//div[@id="detailBullets_feature_div"]//ul/li/span[@class="a-list-item"]'):
                k = "".join(bullet.xpath('./span[@class="a-text-bold"]//text()').getall())
                v = "".join(bullet.xpath('./span[not(@class="a-text-bold")]//text()').getall())
                if k and v: specs[k.replace("\u200e", "").replace(":", "").strip()] = v.replace("\u200e", "").strip()
                
        return AmazonProduct(
            ean=ean,
            marketplace="Amazon",
            url=product_url,
            title=title,
            price_brl=price_brl,
            img_url=img_url,
            specifications=specs
        )