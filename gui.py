import tkinter as tk
from tkinter import scrolledtext
import threading
import webbrowser
from datetime import datetime

import wikipedia
from PIL import ImageTk

from wiki_service import search_wikipedia


THEMES = {
    "dark": {
        "bg": "#121212",
        "panel": "#1e1e1e",
        "panel2": "#252526",
        "text": "#f2f2f2",
        "muted": "#a0a0a0",
        "entry": "#2a2a2a",
        "border": "#333333"
    },

    "light": {
        "bg": "#f4f4f7",
        "panel": "#ffffff",
        "panel2": "#eef0f4",
        "text": "#1a1a1a",
        "muted": "#5a5a5a",
        "entry": "#ffffff",
        "border": "#dcdcdc"
    }
}


ACCENTS = [
    "#4fc3f7",
    "#66bb6a",
    "#ffa726",
    "#ef5350",
    "#ab47bc",
    "#ec407a"
]


class WikiSearchApp:

    def __init__(self, root):
        self.root = root

        self.theme = "dark"
        self.accent = ACCENTS[0]

        self.history = {}
        self.current_url = ""
        self.current_image = None

        self.create_window()
        self.apply_theme()

    def create_window(self):

        self.root.title("Wikipedia Search Engine")
        self.root.geometry("1200x760")
        self.root.minsize(900, 600)

        # Top bar
        self.topbar = tk.Frame(self.root)
        self.topbar.pack(fill="x")

        self.heading = tk.Label(
            self.topbar,
            text="🌐 Wikipedia Search Engine",
            font=("Segoe UI", 22, "bold")
        )
        self.heading.pack(side="left", padx=20, pady=15)

        self.theme_button = tk.Button(
            self.topbar,
            text="☀ Light Mode",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.change_theme
        )
        self.theme_button.pack(side="right", padx=20)

        # Accent colors
        self.color_frame = tk.Frame(self.topbar)
        self.color_frame.pack(side="right", padx=10)

        tk.Label(
            self.color_frame,
            text="Accent:",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=(0, 6))

        self.color_buttons = []

        for color in ACCENTS:
            button = tk.Button(
                self.color_frame,
                bg=color,
                activebackground=color,
                width=2,
                height=1,
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda c=color: self.change_accent(c)
            )

            button.pack(side="left", padx=3)
            self.color_buttons.append(button)

        # Search bar
        self.search_frame = tk.Frame(self.root)
        self.search_frame.pack(
            fill="x",
            padx=20,
            pady=(5, 10)
        )

        self.search_entry = tk.Entry(
            self.search_frame,
            font=("Segoe UI", 14),
            relief="flat"
        )
        self.search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=8,
            padx=(0, 10)
        )

        self.search_entry.bind(
            "<Return>",
            lambda event: self.search()
        )

        self.search_button = tk.Button(
            self.search_frame,
            text="Search",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=16,
            cursor="hand2",
            command=self.search
        )
        self.search_button.pack(
            side="left",
            padx=4,
            ipady=6
        )

        self.clear_button = tk.Button(
            self.search_frame,
            text="Clear",
            font=("Segoe UI", 11),
            relief="flat",
            bd=0,
            padx=14,
            cursor="hand2",
            command=self.clear
        )
        self.clear_button.pack(
            side="left",
            padx=4,
            ipady=6
        )

        self.open_button = tk.Button(
            self.search_frame,
            text="Open in Wikipedia",
            font=("Segoe UI", 11),
            relief="flat",
            bd=0,
            padx=14,
            cursor="hand2",
            command=self.open_page
        )
        self.open_button.pack(
            side="left",
            padx=4,
            ipady=6
        )

        # Main area
        self.body = tk.Frame(self.root)
        self.body.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15)
        )

        # History
        self.sidebar = tk.Frame(
            self.body,
            width=240
        )
        self.sidebar.pack(
            side="left",
            fill="y",
            padx=(0, 15)
        )
        self.sidebar.pack_propagate(False)

        self.history_title = tk.Label(
            self.sidebar,
            text="🕒 Search History",
            font=("Segoe UI", 12, "bold"),
            anchor="w"
        )
        self.history_title.pack(
            fill="x",
            pady=(0, 8)
        )

        self.history_list = tk.Listbox(
            self.sidebar,
            font=("Segoe UI", 11),
            relief="flat",
            bd=0,
            activestyle="none",
            highlightthickness=0
        )
        self.history_list.pack(
            fill="both",
            expand=True
        )

        self.history_list.bind(
            "<<ListboxSelect>>",
            self.load_history
        )

        self.clear_history_button = tk.Button(
            self.sidebar,
            text="Clear History",
            font=("Segoe UI", 9),
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.clear_history
        )
        self.clear_history_button.pack(
            fill="x",
            pady=(8, 0),
            ipady=4
        )

        # Results
        self.results = tk.Frame(self.body)
        self.results.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.title_label = tk.Label(
            self.results,
            text="",
            font=("Segoe UI", 16, "bold"),
            anchor="w",
            justify="left"
        )
        self.title_label.pack(
            fill="x",
            pady=(0, 8)
        )

        self.content = tk.Frame(self.results)
        self.content.pack(
            fill="both",
            expand=True
        )

        self.image_label = tk.Label(
            self.content,
            text=""
        )
        self.image_label.pack(
            side="left",
            anchor="n",
            padx=(0, 15)
        )

        self.result_box = scrolledtext.ScrolledText(
            self.content,
            font=("Calibri", 12),
            relief="flat",
            bd=0,
            wrap="word"
        )
        self.result_box.pack(
            side="left",
            fill="both",
            expand=True
        )

        # Status
        self.status = tk.Label(
            self.root,
            text="Ready. Type something and press Search.",
            font=("Segoe UI", 9),
            anchor="w"
        )
        self.status.pack(
            fill="x",
            side="bottom",
            padx=20,
            pady=(0, 8)
        )

    def change_theme(self):
        if self.theme == "dark":
            self.theme = "light"
        else:
            self.theme = "dark"

        self.apply_theme()

    def change_accent(self, color):
        self.accent = color
        self.apply_theme()

    def apply_theme(self):

        t = THEMES[self.theme]

        self.root.configure(bg=t["bg"])

        self.topbar.configure(bg=t["bg"])
        self.heading.configure(
            bg=t["bg"],
            fg=self.accent
        )

        self.color_frame.configure(bg=t["bg"])

        for widget in self.color_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(
                    bg=t["bg"],
                    fg=t["muted"]
                )

        if self.theme == "dark":
            theme_text = "☀ Light Mode"
        else:
            theme_text = "🌙 Dark Mode"

        self.theme_button.configure(
            text=theme_text,
            bg=self.accent,
            fg="#111111",
            activebackground=self.accent
        )

        self.search_frame.configure(bg=t["bg"])

        self.search_entry.configure(
            bg=t["entry"],
            fg=t["text"],
            insertbackground=t["text"],
            highlightthickness=1,
            highlightbackground=t["border"],
            highlightcolor=self.accent
        )

        for button in (
            self.search_button,
            self.clear_button,
            self.open_button
        ):
            button.configure(
                bg=self.accent,
                fg="#111111",
                activebackground=self.accent
            )

        self.body.configure(bg=t["bg"])

        self.sidebar.configure(bg=t["panel"])

        self.history_title.configure(
            bg=t["panel"],
            fg=t["text"]
        )

        self.history_list.configure(
            bg=t["panel"],
            fg=t["text"],
            selectbackground=self.accent,
            selectforeground="#111111",
            highlightthickness=0
        )

        self.clear_history_button.configure(
            bg=t["panel2"],
            fg=t["muted"],
            activebackground=t["panel2"]
        )

        self.results.configure(bg=t["bg"])

        self.title_label.configure(
            bg=t["bg"],
            fg=self.accent
        )

        self.content.configure(bg=t["bg"])

        self.image_label.configure(
            bg=t["bg"],
            fg=t["muted"]
        )

        self.result_box.configure(
            bg=t["panel"],
            fg=t["text"],
            insertbackground=t["text"],
            highlightthickness=1,
            highlightbackground=t["border"]
        )

        self.status.configure(
            bg=t["bg"],
            fg=t["muted"]
        )

        for button, color in zip(
            self.color_buttons,
            ACCENTS
        ):
            if color == self.accent:
                button.configure(
                    highlightthickness=2,
                    highlightbackground=t["text"]
                )
            else:
                button.configure(
                    highlightthickness=0
                )

    def search(self):

        query = self.search_entry.get().strip()

        if query == "":
            return

        self.set_status(
            f"Searching for '{query}'..."
        )

        thread = threading.Thread(
            target=self.search_worker,
            args=(query,),
            daemon=True
        )

        thread.start()

    def search_worker(self, query):

        self.set_result("Searching...\n")

        try:
            result = search_wikipedia(query)

            self.show_result(result)
            self.add_history(result)

            self.set_status(
                f"Done. Showing results for '{result.title}'."
            )

        except wikipedia.exceptions.DisambiguationError as error:

            self.set_result(
                "Multiple results found:\n\n"
            )

            for item in error.options[:20]:
                self.result_box.insert(
                    tk.END,
                    "• " + item + "\n"
                )

            self.set_status(
                "Multiple matches found. Try a more specific term."
            )

        except Exception as error:

            self.set_result(
                "Error:\n" + str(error)
            )

            self.set_status(
                "Something went wrong."
            )

    def show_result(self, result):

        self.current_url = result.url

        self.title_label.configure(
            text=result.title
        )

        self.set_result(result.summary)

        if result.image is not None:

            self.current_image = ImageTk.PhotoImage(
                result.image
            )

            self.image_label.configure(
                image=self.current_image,
                text=""
            )

        else:

            self.current_image = None

            self.image_label.configure(
                image="",
                text="No Image\nAvailable"
            )

    def add_history(self, result):

        title = result.title

        if title in self.history:

            old_index = list(
                self.history.keys()
            ).index(title)

            self.history_list.delete(old_index)

        self.history[title] = {
            "result": result,
            "time": datetime.now().strftime("%H:%M:%S")
        }

        time = datetime.now().strftime("%H:%M:%S")

        self.history_list.insert(
            0,
            f"{title} · {time}"
        )

    def load_history(self, event):

        selected = self.history_list.curselection()

        if not selected:
            return

        item = self.history_list.get(
            selected[0]
        )

        title = item.split(" ·")[0]

        if title in self.history:

            result = self.history[title]["result"]

            self.show_result(result)

            self.set_status(
                f"Loaded '{title}' from history."
            )

    def clear_history(self):

        self.history.clear()

        self.history_list.delete(
            0,
            tk.END
        )

        self.set_status(
            "History cleared."
        )

    def clear(self):

        self.search_entry.delete(
            0,
            tk.END
        )

        self.result_box.delete(
            "1.0",
            tk.END
        )

        self.title_label.configure(
            text=""
        )

        self.image_label.configure(
            image="",
            text=""
        )

        self.current_image = None
        self.current_url = ""

        self.set_status(
            "Cleared. Ready for a new search."
        )

    def open_page(self):

        if self.current_url:
            webbrowser.open(
                self.current_url
            )
        else:
            self.set_status(
                "Nothing to open yet. Search for something first."
            )

    def set_result(self, text):

        self.result_box.delete(
            "1.0",
            tk.END
        )

        self.result_box.insert(
            tk.END,
            text
        )

    def set_status(self, text):

        self.status.configure(
            text=text
        )


if __name__ == "__main__":

    root = tk.Tk()

    app = WikiSearchApp(root)

    root.mainloop()