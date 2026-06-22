import sys
import os

# Align monorepo paths so internal absolute imports work cleanly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the controller frame from app.py
from apps.gui.app import AppDashboard

if __name__ == "__main__":
    # Launch the application interface loop
    app = AppDashboard()
    app.mainloop()