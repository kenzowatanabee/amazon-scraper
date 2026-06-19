from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class AmazonProduct:
    ean: str
    marketplace: str
    url: str
    title: str
    price_brl: Optional[float]
    img_url: Optional[str]
    specifications: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)