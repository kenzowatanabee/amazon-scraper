import os
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageOps
from typing import Dict

class SpecsModalView(ctk.CTkToplevel):
    """Widescreen popup modal configured with an expansive left panel to show images at full size."""
    def __init__(self, master, specs: Dict[str, str], ean: str, **kwargs):
        super().__init__(master, **kwargs)
        self.title(f"Product Detailed Inspection — EAN: {ean}")
        
        # 📏 Expanded size to provide a cinema-scale image frame panel
        self.geometry("1000x650") 
        self.minsize(900, 550)
        self.attributes("-topmost", True)
        
        self._build_layout(specs, ean)

    def _build_layout(self, specs: Dict[str, str], ean: str):
        # 👑 THE MASTER PROPORTION SWAP: Give column 0 (Left Image) the majority weight and size
        self.grid_columnconfigure(0, weight=3, minsize=550) 
        self.grid_columnconfigure(1, weight=1, minsize=300) 
        self.grid_rowconfigure(0, weight=1)

        # ----------------- LEFT PANEL: THE DOMINANT IMAGE FRAME (BIGGER ONE) -----------------
        img_panel = ctk.CTkFrame(self, fg_color=("#e9ecef", "#141416"), corner_radius=16)
        img_panel.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        # Massive 500x500 dimension bounds so details are fully clear and visible
        target_size = (500, 500)
        radius = 28 # Smooth, premium curvature to scale with the giant canvas size
        image_path = f"data/assets/images/AMZ_{ean}.jpg"
        
        try:
            if os.path.exists(image_path):
                source_img = Image.open(image_path).convert("RGBA")
            else:
                source_img = Image.new("RGBA", target_size, color=(44, 44, 46, 255))
                draw = ImageDraw.Draw(source_img)
                draw.rectangle([0, 0, target_size[0]-1, target_size[1]-1], outline="#3a3a3c", width=3)

            # 🛠️ Letterbox Contain Scaling Loop: Fits the ENTIRE image without cutting a single pixel
            source_img.thumbnail(target_size, Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", target_size, (0, 0, 0, 0))
            
            # Center the un-cropped item onto the giant square transparent backing sheet
            paste_x = (target_size[0] - source_img.size[0]) // 2
            paste_y = (target_size[1] - source_img.size[1]) // 2
            canvas.paste(source_img, (paste_x, paste_y), source_img)

            # Apply clean curved border bounds to the canvas layer edge points
            mask = Image.new("L", target_size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([0, 0, target_size[0], target_size[1]], radius=radius, fill=255)
            canvas.putalpha(mask)

            modal_hero = ctk.CTkImage(light_image=canvas, dark_image=canvas, size=target_size)
            
            img_lbl = ctk.CTkLabel(img_panel, image=modal_hero, text="")
            img_lbl.pack(expand=True, padx=20, pady=20)
            setattr(img_lbl, "image_reference", modal_hero)
            
            ean_lbl = ctk.CTkLabel(img_panel, text=f"SKU/EAN IDENTIFIER LINK: {ean}", font=ctk.CTkFont(family="Courier", size=14, weight="bold"), text_color="#868e96")
            ean_lbl.pack(pady=(0, 20))
            
        except Exception:
            fallback_lbl = ctk.CTkLabel(img_panel, text="⚠️\nImage Asset Missing", font=ctk.CTkFont(size=16), width=target_size[0], height=target_size[1])
            fallback_lbl.pack(expand=True)

        # ----------------- RIGHT PANEL: COMPRESSED TECHNICAL ATTRIBUTES -----------------
        scroll_box = ctk.CTkScrollableFrame(self, label_text="Product Attributes")
        scroll_box.grid(row=0, column=1, sticky="nsew", padx=(0, 15), pady=15)

        if not specs or not isinstance(specs, dict):
            ctk.CTkLabel(scroll_box, text="No metadata attributes detected.").pack(pady=40)
            return

        for idx, (key, val) in enumerate(specs.items()):
            row_bg = ("#f8f9fa", "#1a1a1c") if idx % 2 == 0 else "transparent"
            row_frame = ctk.CTkFrame(scroll_box, fg_color=row_bg, corner_radius=4)
            row_frame.pack(fill="x", pady=2, padx=2)
            
            lbl_key = ctk.CTkLabel(row_frame, text=str(key), font=ctk.CTkFont(size=12, weight="bold"), width=110, anchor="w")
            lbl_key.pack(side="left", padx=8, pady=6)
            
            lbl_val = ctk.CTkLabel(row_frame, text=str(val), font=ctk.CTkFont(size=12), anchor="w", justify="left", wraplength=140)
            lbl_val.pack(side="left", fill="x", expand=True, padx=8, pady=6)