import customtkinter as ctk
from typing import Dict

class SpecsModalView(ctk.CTkToplevel):
    """Dynamic key-value overlay inspector popup modal window."""
    def __init__(self, master, specs: Dict[str, str], **kwargs):
        super().__init__(master, **kwargs)
        self.title("Specifications Map Inspector")
        self.geometry("500x400")
        self.attributes("-topmost", True)
        
        self._build_table(specs)

    def _build_table(self, specs: Dict[str, str]):
        scroll_box = ctk.CTkScrollableFrame(self, label_text="Product Property Attributes Key-Value Array")
        scroll_box.pack(fill="both", expand=True, padx=15, pady=15)

        if not specs or not isinstance(specs, dict):
            ctk.CTkLabel(scroll_box, text="No specifications available for this entry.").pack(pady=20)
            return

        for key, val in specs.items():
            row_frame = ctk.CTkFrame(scroll_box, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            lbl_key = ctk.CTkLabel(row_frame, text=f"{key}:", font=ctk.CTkFont(weight="bold"), width=150, anchor="w")
            lbl_key.pack(side="left", padx=5)
            
            lbl_val = ctk.CTkLabel(row_frame, text=str(val), anchor="w", justify="left", wraplength=280)
            lbl_val.pack(side="left", fill="x", expand=True, padx=5)