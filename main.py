"""
main.py
-------
Entry point for the Wikipedia Search Engine desktop app.
Run with:  python main.py
"""

import tkinter as tk

from gui import WikiSearchApp


def main():
    root = tk.Tk()
    WikiSearchApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
