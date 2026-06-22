import logging
import customtkinter as ctk

class GUIQueueLogHandler(logging.Handler):
    """Intercepts standard logging streams and feeds them into a target Tkinter widget safely."""
    def __init__(self, text_widget: ctk.CTkTextbox):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.after(0, self.append_message, msg + "\n")

    def append_message(self, msg: str):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", msg)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")


class LogConsoleView(ctk.CTkTextbox):
    """Self-contained logging text panel component wrapper."""
    def __init__(self, master, **kwargs):
        super().__init__(master, state="disabled", font=ctk.CTkFont(family="Courier", size=12), **kwargs)
        self._setup_global_bridge()

    def _setup_global_bridge(self):
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        handler = GUIQueueLogHandler(self)
        handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s]: %(message)s", "%H:%M:%S"))
        
        if root_logger.hasHandlers():
            root_logger.handlers.clear()
            
        root_logger.addHandler(handler)
        logging.getLogger("scrapling").setLevel(logging.WARNING)