import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import requests
import os
import tempfile
import json
import queue
import locale

# ---------------- PATHS ----------------

BASE = os.path.join(os.path.expanduser("~"), "Documents", "Checker")
os.makedirs(BASE, exist_ok=True)

TEMP = tempfile.gettempdir()

SETTINGS_FILE = os.path.join(BASE, "settings.json")
DOWNLOADED_EXE = os.path.join(BASE, "EvrCheck.exe")


# ---------------- URLS ----------------

DOWNLOAD_URL = "https://example.com/file.exe"


# ---------------- DANGEROUS FILES ----------------

DANGEROUS = [
    "cheatengine.exe",
    "aimbot.exe",
    "hack.dll",
    "injector.exe"
]


# ---------------- LANG ----------------

LANG = {

    "en": {
        "title": "Hidden Files Scan",
        "loading": "Loading...",
        "ready": "Ready to scan",
        "start": "Start scan",
        "scan": "Scanning files...",
        "clean": "No threats found!",
        "exit": "Press any key to exit",
        "theme": "Theme",
        "lang": "Language"
    },

    "ru": {
        "title": "Проверка файлов",
        "loading": "Загрузка...",
        "ready": "Готово к проверке",
        "start": "Начать проверку",
        "scan": "Сканирование...",
        "clean": "Угроз не найдено!",
        "exit": "Нажмите любую кнопку",
        "theme": "Тема",
        "lang": "Язык"
    },

    "ua": {
        "title": "Перевірка файлів",
        "loading": "Завантаження...",
        "ready": "Готово до перевірки",
        "start": "Почати перевірку",
        "scan": "Сканування...",
        "clean": "Загроз не знайдено!",
        "exit": "Натисніть будь-яку кнопку",
        "theme": "Тема",
        "lang": "Мова"
    }
}


# ---------------- THEMES ----------------

THEMES = {

    "Orange": {
        "BG": "#2B1A12",
        "CARD": "#3A2318",
        "ACCENT": "#FD9B23",
        "BAR": "#E28250",
        "TEXT": "#FDF8EB",
        "SUB": "#FCD19D"
    },

    "Blue": {
        "BG": "#0f172a",
        "CARD": "#020617",
        "ACCENT": "#38bdf8",
        "BAR": "#0ea5e9",
        "TEXT": "#e5e7eb",
        "SUB": "#94a3b8"
    },

    "Dark": {
        "BG": "#0a0a0a",
        "CARD": "#1a1a1a",
        "ACCENT": "#22c55e",
        "BAR": "#16a34a",
        "TEXT": "#ffffff",
        "SUB": "#9ca3af"
    }
}


# ---------------- SETTINGS ----------------

def detect_lang():
    try:
        loc = locale.getdefaultlocale()[0]

        if loc.startswith("ru"):
            return "ru"
        if loc.startswith("uk"):
            return "ua"
    except:
        pass

    return "en"


def load_settings():

    if not os.path.exists(SETTINGS_FILE):

        data = {
            "theme": "Orange",
            "lang": detect_lang(),
        }

        save_settings(data)
        return data

    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(data):

    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------------- APP ----------------

class App:

    def __init__(self, root):

        self.root = root
        self.q = queue.Queue()

        self.settings = load_settings()

        self.theme = self.settings["theme"]
        self.lang = self.settings["lang"]

        self.setup_ui()

        threading.Thread(
            target=self.download_exe,
            daemon=True
        ).start()

        self.safe_loop()


    # ---------------- UI ----------------

    def setup_ui(self):

        self.root.title("Everything Checker")
        self.root.geometry("480x330")
        self.root.resizable(False, False)

        self.card = tk.Frame(self.root)
        self.card.place(relx=0.5, rely=0.5, anchor="center",
                        width=440, height=290)

        self.title = tk.Label(
            self.card,
            font=("Segoe UI", 20, "bold")
        )
        self.title.pack(pady=10)



        self.label = tk.Label(
            self.card,
            font=("Segoe UI", 12)
        )
        self.label.pack()


        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Main.Horizontal.TProgressbar",
            thickness=15
        )

        self.bar = ttk.Progressbar(
            self.card,
            style="Main.Horizontal.TProgressbar",
            length=350
        )
        self.bar.pack(pady=15)


        self.status = tk.Label(
            self.card,
            font=("Segoe UI", 10)
        )
        self.status.pack()


        self.start_btn = tk.Button(
            self.card,
            command=self.start_scan,
            font=("Segoe UI", 10, "bold")
        )
        self.start_btn.pack_forget()

        self.theme_btn = tk.Button(
            self.card,
            command=self.switch_theme,
            font=("Segoe UI", 9)
        )
        self.theme_btn.pack(pady=3)


        self.apply_all()


    # ---------------- APPLY ----------------

    def apply_all(self):

        t = THEMES[self.theme]
        l = LANG[self.lang]

        self.root.configure(bg=t["BG"])
        self.card.configure(bg=t["CARD"])

        self.theme_btn.configure(
            bg=t["ACCENT"],
            fg=t["BG"],
            activebackground=t["BAR"],
            activeforeground=t["TEXT"]
        )

        self.title.configure(
            text=l["title"],
            fg=t["ACCENT"],
            bg=t["CARD"]
        )

        self.label.configure(
            text=l["loading"],
            fg=t["TEXT"],
            bg=t["CARD"]
        )

        self.status.configure(
            fg=t["SUB"],
            bg=t["CARD"]
        )

        self.start_btn.configure(
            text=l["start"],
            bg=t["ACCENT"],
            fg=t["BG"]
        )

        self.theme_btn.configure(
            text=l["theme"]
        )

        style = ttk.Style()

        style.configure(
            "Main.Horizontal.TProgressbar",
            background=t["BAR"],
            troughcolor=t["BG"]
        )

    # ---------------- THREAD SAFE ----------------

    def safe_loop(self):

        try:
            while True:

                fn = self.q.get_nowait()
                fn()

        except queue.Empty:
            pass

        self.root.after(50, self.safe_loop)


    def ui(self, fn):
        self.q.put(fn)


    # ---------------- SWITCH ----------------

    def switch_theme(self):

        keys = list(THEMES.keys())
        i = keys.index(self.theme)

        self.theme = keys[(i+1) % len(keys)]

        self.settings["theme"] = self.theme
        save_settings(self.settings)

        self.apply_all()

    # ---------------- DOWNLOAD ----------------

    def download_exe(self):

        try:

            r = requests.get(DOWNLOAD_URL, stream=True)

            with open(DOWNLOADED_EXE, "wb") as f:

                for c in r.iter_content(1024):
                    if c:
                        f.write(c)

        except:
            pass

        self.root.after(0, self.show_start_button)

    def show_start_button(self):

        self.label.config(
            text=LANG[self.lang]["ready"]
        )

        self.start_btn.pack(pady=8)

    # ---------------- SCAN ----------------

    def start_scan(self):

        self.ui(lambda: self.label.config(
            text=LANG[self.lang]["scan"]
        ))

        threading.Thread(
            target=self.scan_worker,
            daemon=True
        ).start()


    def scan_worker(self):

        found = []

        paths = [
            os.getenv("APPDATA"),
            os.getenv("LOCALAPPDATA"),
            os.getenv("TEMP")
        ]

        for i in range(101):

            time.sleep(0.03)

            self.ui(lambda v=i: self.bar.config(value=v))


        for p in paths:

            if not p:
                continue

            for root, dirs, files in os.walk(p):

                for f in files:

                    if f.lower() in DANGEROUS:
                        found.append(os.path.join(root, f))


        if found:
            msg = "Found:\n" + "\n".join(found[:5])
        else:
            msg = LANG[self.lang]["clean"]

        self.ui(lambda: self.finish(msg))


    # ---------------- FINISH ----------------

    def finish(self, text):

        self.label.config(text=text)

        self.status.config(
            text=LANG[self.lang]["exit"]
        )

        self.root.bind("<Key>", lambda e: self.root.destroy())
        self.root.bind("<Button>", lambda e: self.root.destroy())



# ---------------- START ----------------

root = tk.Tk()
App(root)
root.mainloop()
