# src/main.py

import sys
from pathlib import Path
from src.gui import main_window

# Add the src directory to the Python path
src_dir = Path(__file__).resolve().parent
sys.path.append(str(src_dir))

if __name__ == "__main__":
    app = main_window.TravelCostApp()
    app.notebook.bind("<<NotebookTabChanged>>", app.on_tab_change)
    app.mainloop()