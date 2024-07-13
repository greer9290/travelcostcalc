# src/main.py

import sys
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).resolve().parent
sys.path.append(str(src_dir))

from gui import main_window

if __name__ == "__main__":
    app = main_window.TravelCostApp()
    app.notebook.bind("<<NotebookTabChanged>>", app.on_tab_change)
    app.mainloop()