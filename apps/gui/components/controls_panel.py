import customtkinter as ctk
from typing import Callable

class ControlsPanelView(ctk.CTkFrame):
    """Left sidebar engine setting management controls console layout component."""
    def __init__(self, master, on_run_callback: Callable[[str], None], **kwargs):
        super().__init__(master, width=320, corner_radius=0, **kwargs)
        self.on_run_callback = on_run_callback
        self._build_ui()

    def _build_ui(self):
        title_label = ctk.CTkLabel(self, text="Controls", font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(padx=20, pady=20)

        target_label = ctk.CTkLabel(self, text="Select Target Platform:")
        target_label.pack(anchor="w", padx=20, pady=5)
        self.target_combo = ctk.CTkComboBox(self, values=["amazon"])
        self.target_combo.pack(fill="x", padx=20, pady=5)

        ean_label = ctk.CTkLabel(self, text="Target EAN (Single Inspection):")
        ean_label.pack(anchor="w", padx=20, pady=5)
        self.ean_entry = ctk.CTkEntry(self, placeholder_text="e.g., 7891172523915")
        self.ean_entry.pack(fill="x", padx=20, pady=5)

        self.start_btn = ctk.CTkButton(
            self, text="▶️ Run Scraping Engine", 
            command=self._handle_run_click, 
            fg_color="#2b8a3e", hover_color="#237032"
        )
        self.start_btn.pack(fill="x", padx=20, pady=30)

    def _handle_run_click(self):
        target_ean = self.ean_entry.get().strip()
        self.on_run_callback(target_ean)

    def set_running_state(self, is_running: bool):
        if is_running:
            self.start_btn.configure(state="disabled", text="⚡ Processing Loop running...")
        else:
            self.start_btn.configure(state="normal", text="▶️ Run Scraping Engine")