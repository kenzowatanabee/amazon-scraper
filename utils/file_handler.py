import os, csv, json
from typing import List

class FileHandler:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def load_eans_from_csv(filepath: str) -> List[str]:
        eans: List[str] = []
        
        try:
            with open(filepath, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    ean = row.get("ean", "").strip()
                    if ean: eans.append(ean)
                    
            print(f"Loaded {len(eans)} EANS from {filepath}")
            
        except Exception as e:
            print(f"Error reading CSV: {e}")
            
        return eans