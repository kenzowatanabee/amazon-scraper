import os, csv, json
from typing import List, Dict, Any

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
    
    @classmethod
    def load_results_from_json(cls, file_path: str) -> List[Dict[str, Any]]:
        """
        Reads a structured JSON data array file from the local file system.
        Used for dashboard data hydration on application startup.
        """
        if not os.path.exists(file_path):
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                return []
                
            return data
            
        except json.JSONDecodeError as e:
            return []
        except Exception as e:
            return []
    
    @staticmethod
    def save_results_to_json(filepath: str, data: List[Dict[str, Any]]) -> None:
        """
        Centralized pipeline static method to save scraped datasets.
        """
        
        if not data:
            print("No data received to save. Skipping file generation.")
            return
        try:
            import os
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, mode="w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            print(f"Successfully saved {len(data)} items to {filepath}")
        except Exception as e:
            print(f"Failed to save JSON results: {e}")
            
    @staticmethod
    def save_image_to_disk(folder_path:str, filename: str, image_bytes: bytes) -> None:
        os.makedirs(folder_path, exist_ok=True)
        
        with open(os.path.join(folder_path, filename), "wb") as f:
            f.write(image_bytes)