import sys
import os
import threading
import asyncio
import logging
from typing import List, Dict, Any

import customtkinter as ctk

# Shared Core Modules
from core.targets.amazon.worker import AmazonScraper
from utils.file_handler import FileHandler

# Modular Component Imports 🧩
from apps.gui.components.controls_panel import ControlsPanelView
from apps.gui.components.log_console import LogConsoleView
from apps.gui.components.gallery_grid import GalleryGridView

class AppDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Enterprise Multi-Store Scraper Dashboard")
        self.geometry("1150x700")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Base configuration paths
        self.output_path = "data/output/amazon_gui_results.json"

        self.async_loop = None
        self.worker_thread = None

        self._assemble_views()
        
        # 🔄 HOOK: Hydrate existing cache data straight into the visualizer on startup
        self._hydrate_cached_results()

    def _assemble_views(self):
        """Builds the main layout frame by instantiating modular components."""
        self.grid_columnconfigure(0, weight=0, minsize=320)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.controls_panel = ControlsPanelView(self, on_run_callback=self.start_scraping_workflow)
        self.controls_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.display_tabview = ctk.CTkTabview(self, corner_radius=8)
        self.display_tabview.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        tab_gallery = self.display_tabview.add("📊 Scraped Results Gallery")
        tab_logs = self.display_tabview.add("📋 System Monitor Logs")
        
        tab_logs.grid_columnconfigure(0, weight=1)
        tab_logs.grid_rowconfigure(0, weight=1)
        tab_gallery.grid_columnconfigure(0, weight=1)
        tab_gallery.grid_rowconfigure(0, weight=1)

        self.log_console = LogConsoleView(tab_logs)
        self.log_console.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.gallery_grid = GalleryGridView(tab_gallery)
        self.gallery_grid.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    def _hydrate_cached_results(self):
        """Checks disk storage for pre-existing json datasets to display immediately."""
        if os.path.exists(self.output_path):
            try:
                logging.info(f"💾 Found existing cache file. Hydrating dashboard gallery...")
                
                # Use your shared file handler utility to load the json data array safely
                cached_data = FileHandler.load_results_from_json(self.output_path)
                
                if cached_data:
                    self.gallery_grid.populate_results(cached_data)
                    self.display_tabview.set("📊 Scraped Results Gallery")
                    logging.info(f"✅ Successfully loaded {len(cached_data)} items from disk.")
            except Exception as e:
                logging.warning(f"Could not load initialization cache data file: {e}")

    def start_scraping_workflow(self, target_ean: str):
        if not target_ean:
            logging.error("Operation canceled: No target EAN provided in fields.")
            return

        self.controls_panel.set_running_state(True)
        self.display_tabview.set("📋 System Monitor Logs")
        
        self.worker_thread = threading.Thread(target=self._run_async_worker_loop, args=([target_ean],), daemon=True)
        self.worker_thread.start()

    def _run_async_worker_loop(self, ean_list: List[str]):
        self.async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.async_loop)
        try:
            self.async_loop.run_until_complete(self._execute_engine_logic(ean_list))
        finally:
            self.async_loop.close()
            self.after(0, lambda: self.controls_panel.set_running_state(False))

    async def _execute_engine_logic(self, ean_list: List[str]):
        try:
            engine = AmazonScraper(ean_list=ean_list, max_concurrent=1)
            scraped_data = await engine.main()
            
            FileHandler.save_results_to_json(self.output_path, scraped_data)
            logging.info(f"Amazon Data saved successfully to: {self.output_path}")
            
            self.after(0, self._render_ui_updates, scraped_data)
        except Exception as e:
            logging.error(f"Critical fault inside engine loop pipeline: {e}")

    def _render_ui_updates(self, data: List[Dict[str, Any]]):
        self.gallery_grid.populate_results(data)
        self.display_tabview.set("📊 Scraped Results Gallery")

    def on_closing(self):
        if self.async_loop and self.async_loop.is_running():
            self.async_loop.call_soon_threadsafe(self.async_loop.stop)
        self.destroy()