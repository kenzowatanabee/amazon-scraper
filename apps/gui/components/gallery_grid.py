import os
import customtkinter as ctk
from PIL import Image
from typing import List, Dict, Any
from .specs_modal import SpecsModalView

class GalleryGridView(ctk.CTkScrollableFrame):
    """Responsive item listing layout manager dashboard grid sheet component."""
    def __init__(self, master, **kwargs):
        super().__init__(master, label_text="Scraped Data Record Sheets", **kwargs)

    def populate_results(self, data: List[Dict[str, Any]]):
        for widget in self.winfo_children():
            widget.destroy()

        if not data:
            no_data_lbl = ctk.CTkLabel(self, text="No items successfully extracted during this engine run.")
            no_data_lbl.pack(pady=20)
            return

        for item in data:
            card = ctk.CTkFrame(self, fg_color=("#f1f3f5", "#1c1c1e"), corner_radius=6)
            card.pack(fill="x", padx=10, pady=5)
            card.grid_columnconfigure(1, weight=1)

            # 🖼️ Thumbnail Loader Pipeline
            ean = item.get("ean", "unknown")
            image_path = f"data/assets/images/AMZ_{ean}.jpg"
            
            try:
                pil_img = Image.open(image_path) if os.path.exists(image_path) else Image.new("RGB", (80, 80), color="#343a40")
                img_thumb = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(80, 80))
                img_lbl = ctk.CTkLabel(card, image=img_thumb, text="")
                img_lbl.grid(row=0, column=0, padx=10, pady=10)
                
                # ✅ FIXED: Bypasses strict dot-notation type checks cleanly
                setattr(img_lbl, "image_reference", img_thumb)
                
            except Exception:
                img_lbl = ctk.CTkLabel(card, text="[No Image]", width=80, height=80)
                img_lbl.grid(row=0, column=0, padx=10, pady=10)

            # 📝 Meta Fields
            title_text = item.get("title", "Unknown Title")
            if len(title_text) > 65: title_text = title_text[:62] + "..."
                
            title_lbl = ctk.CTkLabel(card, text=title_text, font=ctk.CTkFont(size=14, weight="bold"), anchor="w", justify="left")
            title_lbl.grid(row=0, column=1, sticky="w", padx=10, pady=5)

            price_lbl = ctk.CTkLabel(card, text=f"Price: {item.get('price_brl', 'N/A')}", font=ctk.CTkFont(size=13), text_color="#2b8a3e")
            price_lbl.grid(row=0, column=2, padx=20, pady=5)

            spec_btn = ctk.CTkButton(card, text="🔎 Specs", width=70, command=lambda specs=item.get("specifications", {}): self._inspect_specs(specs))
            spec_btn.grid(row=0, column=3, padx=10, pady=5)

    def _inspect_specs(self, specs: Dict[str, str]):
        SpecsModalView(self, specs)