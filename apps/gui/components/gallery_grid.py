import os
import threading
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageOps
from typing import List, Dict, Any
from .specs_modal import SpecsModalView


class GalleryGridView(ctk.CTkScrollableFrame):
    """Responsive item listing layout manager dashboard grid sheet component."""
    def __init__(self, master, **kwargs):
        super().__init__(master, label_text="Scraped Data Record Sheets", **kwargs)

    def populate_results(self, data: List[Dict[str, Any]]):
        """Clears old widgets and draws the skeleton infrastructure for incoming records."""
        for widget in self.winfo_children():
            widget.destroy()

        if not data:
            no_data_lbl = ctk.CTkLabel(self, text="No items successfully extracted during this engine run.")
            no_data_lbl.pack(pady=20)
            return

        for item in data:
            card = ctk.CTkFrame(self, fg_color=("#f1f3f5", "#1c1c1e"), corner_radius=8)
            card.pack(fill="x", padx=10, pady=5)
            card.grid_columnconfigure(1, weight=1)

            # 🛡️ THE FIX: Bind 'ean' immediately at the start of the item scope loop!
            ean = item.get("ean", "unknown")

            # 🛠️ Placeholder Step: Draw a clean temporary UI block while loading
            img_lbl = ctk.CTkLabel(card, text="⌛ Loading...", width=80, height=80, fg_color=("#e9ecef", "#2c2c2e"), corner_radius=6)
            img_lbl.grid(row=0, column=0, padx=10, pady=10)

            # 📝 Metadata Fields Mapping
            title_text = item.get("title", "Unknown Title")
            if len(title_text) > 65: 
                title_text = title_text[:62] + "..."
                
            title_lbl = ctk.CTkLabel(card, text=title_text, font=ctk.CTkFont(size=14, weight="bold"), anchor="w", justify="left")
            title_lbl.grid(row=0, column=1, sticky="w", padx=10, pady=5)

            price_lbl = ctk.CTkLabel(card, text=f"Price: {item.get('price_brl', 'N/A')}", font=ctk.CTkFont(size=13), text_color="#2b8a3e")
            price_lbl.grid(row=0, column=2, padx=20, pady=5)

            # ✅ Safely references the 'ean' defined above
            spec_btn = ctk.CTkButton(
                card, text="🔎 Specs", width=70, 
                command=lambda specs=item.get("specifications", {}), current_ean=ean: self._inspect_specs(specs, current_ean)
            )
            spec_btn.grid(row=0, column=3, padx=10, pady=5)

            # 🚀 Async Dispatch for image rendering
            image_path = f"data/assets/images/AMZ_{ean}.jpg"
            
            threading.Thread(
                target=self._async_load_and_process_thumbnail, 
                args=(img_lbl, image_path), 
                daemon=True
            ).start()

    def _async_load_and_process_thumbnail(self, label_widget: ctk.CTkLabel, path: str):
        """Processes and rounds image borders in a background thread, then pipes it to the UI."""
        target_size = (80, 80)
        radius = 12  # Control the smoothness of the rounding curvature radius
        
        try:
            if os.path.exists(path):
                source_img = Image.open(path)
            else:
                # High-fidelity visual fallback asset: Neutral box with subtle border accents
                source_img = Image.new("RGB", target_size, color="#3a3a3c")
                draw = ImageDraw.Draw(source_img)
                draw.rectangle([0, 0, 79, 79], outline="#48484a", width=2)
            
            # Crop image cleanly to fit our square dimensions symmetrically
            processed_img = ImageOps.fit(source_img, target_size, Image.Resampling.LANCZOS)
            
            # Create anti-aliased round mask overlay graphics
            mask = Image.new("L", target_size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([0, 0, target_size[0], target_size[1]], radius=radius, fill=250)
            
            # Inject alpha channel transparency mask onto our thumbnail asset
            processed_img.putalpha(mask)
            
            # Build native CustomTkinter graphic wrapper
            ctk_thumb = ctk.CTkImage(light_image=processed_img, dark_image=processed_img, size=target_size)
            
            # Safely schedule the update back on the main UI rendering thread
            label_widget.after(0, self._apply_processed_image_to_widget, label_widget, ctk_thumb)
            
        except Exception:
            # Silent fallback handler to guarantee safety guards
            fallback_img = Image.new("RGBA", target_size, color="#2c2c2e")
            ctk_fallback = ctk.CTkImage(light_image=fallback_img, dark_image=fallback_img, size=target_size)
            label_widget.after(0, self._apply_processed_image_to_widget, label_widget, ctk_fallback)

    def _apply_processed_image_to_widget(self, label_widget: ctk.CTkLabel, ctk_image: ctk.CTkImage):
        """Updates the target label with the processed image and keeps a memory reference active."""
        if label_widget.winfo_exists():
            label_widget.configure(image=ctk_image, text="", fg_color="transparent")
            setattr(label_widget, "image_reference", ctk_image)

    def _inspect_specs(self, specs: Dict[str, str], ean: str):
        # Pass the EAN code directly to the modal creator
        SpecsModalView(self, specs, ean)