from tkinter import Tk
from linq_app import LinqApp
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="app.log", format="%(asctime)s - %(levelname)s - %(message)s")
    root = Tk()
    app = LinqApp(root)
    root.mainloop()
