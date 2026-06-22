import os, sys, asyncio, logging, threading
from typing import List, Any

import customtkinter as ctk

# Ensure root directory is in path for monorepo imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Shared Core Imports
from core.targets.amazon.worker import AmazonScraper
from utils.file_handler import FileHandler

# Set UI Theme Styles
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class GUIQueueLogHandler(logging.Handler):
    """Custom logging handler to redirect streams safely into the UI Textbox."""
    def __init__(self, text_widget: ctk.CTkTextbox):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        # Thread-safe insertion using Tkinter's after method
        self.text_widget.after(0, self.append_message, msg + "\n")

    def append_message(self, msg: str):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", msg)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")


class AppDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Enterprise Multi-Store Scraper Dashboard")
        self.geometry("1100x650")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Background loop handles async tracking execution
        self.async_loop = None
        self.worker_thread = None

        self._build_layout()
        self._setup_logging_bridge()

    def _build_layout(self):
        """Initializes the split dashboard layout grid system."""
        self.grid_columnconfigure(0, weight=1)  # Left Controls Panel
        self.grid_columnconfigure(1, weight=2)  # Right Visualizer/Logs Panel
        self.grid_rowconfigure(0, weight=1)

        # ----------------- LEFT CONTROL PANEL -----------------
        self.controls_frame = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.controls_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.title_label = ctk.CTkLabel(self.controls_frame, text="🎛️ Engine Controls", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.pack(padx=20, pady=20)

        # Target Selector
        self.target_label = ctk.CTkLabel(self.controls_frame, text="Select Target Platform:")
        self.target_label.pack(anchor="w", padx=20, pady=5)
        self.target_combo = ctk.CTkComboBox(self.controls_frame, values=["amazon"])
        self.target_combo.pack(fill="x", padx=20, pady=5)

        # Input EAN Inline Configuration
        self.ean_label = ctk.CTkLabel(self.controls_frame, text="Target EAN (Single Inspection):")
        self.ean_label.pack(anchor="w", padx=20, pady=5)
        self.ean_entry = ctk.CTkEntry(self.controls_frame, placeholder_text="e.g., 7891172523915")
        self.ean_entry.pack(fill="x", padx=20, pady=5)

        # Action Execution Controls
        self.start_btn = ctk.CTkButton(self.controls_frame, text="▶️ Run Scraping Engine", command=self.start_scraping_workflow, fg_color="#2b8a3e", hover_color="#237032")
        self.start_btn.pack(fill="x", padx=20, pady=30)

        # ----------------- RIGHT DISPLAY PANEL -----------------
        self.display_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.display_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.display_frame.grid_columnconfigure(0, weight=1)
        self.display_frame.grid_rowconfigure(0, weight=1)

        # Terminal Real-time Logging Monitor console
        self.log_textbox = ctk.CTkTextbox(self.display_frame, state="disabled", font=ctk.CTkFont(family="Courier", size=12))
        self.log_textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def _setup_logging_bridge(self):
        """Bridges ALL application loggers directly into the GUI Textbox console frame."""
        # 1. Access the universal Root Logger instead of a specific string namespace
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        # 2. Build the UI redirect handler
        self.gui_handler = GUIQueueLogHandler(self.log_textbox)
        self.gui_handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s]: %(message)s", "%H:%M:%S")
        )
        
        # 3. Clear out existing handlers to prevent duplicate print loops
        if root_logger.hasHandlers():
            root_logger.handlers.clear()
            
        # 4. Bind the interface display pipeline globally
        root_logger.addHandler(self.gui_handler)
        
        # 5. Optional: Mute Scrapling framework browser spam so it doesn't flood your UI text box
        logging.getLogger("scrapling").setLevel(logging.WARNING)

    def start_scraping_workflow(self):
        """Prepares safety limits and hands execution off to background thread loop."""
        target_ean = self.ean_entry.get().strip()
        if not target_ean:
            # 🔄 CHANGE THIS: Swap self.gui_logger for global logging
            logging.error("Operation canceled: No target EAN provided in fields.")
            return

        self.start_btn.configure(state="disabled", text="⚡ Processing Loop running...")
        
        self.worker_thread = threading.Thread(target=self._run_async_worker_loop, args=([target_ean],), daemon=True)
        self.worker_thread.start()

    def _run_async_worker_loop(self, ean_list: List[str]):
        """Runs inside background worker thread; creates and spins its own async engine context event loop."""
        self.async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.async_loop)
        
        try:
            self.async_loop.run_until_complete(self._execute_engine_logic(ean_list))
        finally:
            self.async_loop.close()
            # UI safe button reset
            self.start_btn.after(0, lambda: self.start_btn.configure(state="normal", text="▶️ Run Scraping Engine"))

    async def _execute_engine_logic(self, ean_list: List[str]):
        """Actual core execution context running inside the background thread."""
        try:
            engine = AmazonScraper(ean_list=ean_list, max_concurrent=1)
            scraped_data = await engine.main()
            
            output_path = "data/output/amazon_gui_results.json"
            FileHandler.save_results_to_json(output_path, scraped_data)
            
            # 🔄 CHANGE THIS: Swap self.gui_logger for global logging
            logging.info(f"Amazon Data saved successfully to: {output_path}")
            
        except Exception as e:
            # 🔄 CHANGE THIS: Swap self.gui_logger for global logging
            logging.error(f"Critical execution fault triggered inside engine loop pipeline: {e}")

    def on_closing(self):
        """Gracefully handle window termination controls."""
        if self.async_loop and self.async_loop.is_running():
            self.async_loop.call_soon_threadsafe(self.async_loop.stop)
        self.destroy()


if __name__ == "__main__":
    app = AppDashboard()
    app.mainloop()