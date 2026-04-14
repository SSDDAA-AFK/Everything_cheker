import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
import requests
import os
import tempfile
import hashlib
import subprocess
import re

# Налаштування папок
FOLDER = os.path.join(os.path.expanduser("~"), "Documents", "EverythingChecker")
os.makedirs(FOLDER, exist_ok=True)
THEME_FILE = os.path.join(FOLDER, "theme.txt")

ICON_URL = "https://raw.githubusercontent.com/SSDDAA-AFK/Everything_cheker/main/icon.ico"
ICON_PATH = os.path.join(tempfile.gettempdir(), "everything_icon.ico")

FOUND_FILES = []
AI_SUSPECTS = []

THEMES = {
    "RustMe Orange": {"BG": "#1A110C", "CARD": "#261912", "ACCENT": "#FF8C00", "BAR": "#E67E22", "TEXT": "#F5F5F5", "SUB": "#BDC3C7"},
    "Dark Purple": {"BG": "#0F0C1D", "CARD": "#1B172E", "ACCENT": "#9B59B6", "BAR": "#8E44AD", "TEXT": "#ECF0F1", "SUB": "#95A5A6"},
    "Midnight Blue": {"BG": "#0B1117", "CARD": "#161B22", "ACCENT": "#58A6FF", "BAR": "#1F6FEB", "TEXT": "#C9D1D9", "SUB": "#8B949E"},
    "Forest Green": {"BG": "#0D1111", "CARD": "#161C1C", "ACCENT": "#2ECC71", "BAR": "#27AE60", "TEXT": "#ECF0F1", "SUB": "#95A5A6"}
}

class LoaderApp:
    def __init__(self, root):
        self.current_theme = self.load_theme()
        self.is_scanning = False
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.title("Everything Checker v2.0 | RUSTME EDITION")
        self.root.geometry("500x380")
        
        if self.download_icon():
            try: self.root.iconbitmap(ICON_PATH)
            except: pass
            
        self.root.resizable(False, False)
        theme = THEMES[self.current_theme]
        self.root.configure(bg=theme["BG"])

        self.main_container = tk.Frame(root, bg=theme["BG"])
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.card = tk.Frame(self.main_container, bg=theme["CARD"], bd=0)
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=440, height=330)

        self.title = tk.Label(self.card, text="🛡️ RUSTME CHECKER", font=("Segoe UI", 18, "bold"), fg=theme["ACCENT"], bg=theme["CARD"])
        self.title.pack(pady=(20, 10))

        self.label = tk.Label(self.card, text="Ready to protect your game", bg=theme["CARD"], fg=theme["TEXT"], font=("Segoe UI", 11))
        self.label.pack(pady=5)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.update_progressbar_style(theme)

        self.progress = ttk.Progressbar(self.card, style="Main.Horizontal.TProgressbar", orient="horizontal", length=360, mode="determinate")
        self.progress.pack(pady=15)

        self.status = tk.Label(self.card, text="Waiting for start...", bg=theme["CARD"], fg=theme["SUB"], font=("Segoe UI", 9))
        self.status.pack()

        self.btn_frame = tk.Frame(self.card, bg=theme["CARD"])
        self.btn_frame.pack(pady=10)

        self.start_btn = tk.Button(self.btn_frame, text="🚀 START SCAN", command=self.start_scan_thread, bg=theme["ACCENT"], fg=theme["BG"], font=("Segoe UI", 10, "bold"), relief="flat", padx=15, cursor="hand2")
        self.start_btn.pack(side="left", padx=5)

        self.report_btn = tk.Button(self.btn_frame, text="📋 LAST REPORT", command=self.show_full_results, bg=theme["CARD"], fg=theme["SUB"], font=("Segoe UI", 10), relief="flat", bd=1, state="disabled", cursor="hand2")
        self.report_btn.pack(side="left", padx=5)

        self.theme_btn = tk.Button(self.card, text="🎨 SWITCH THEME", command=self.switch_theme, bg=theme["CARD"], fg=theme["SUB"], font=("Segoe UI", 9), relief="flat", cursor="hand2")
        self.theme_btn.pack(pady=5)

    def update_progressbar_style(self, theme):
        self.style.configure("Main.Horizontal.TProgressbar", background=theme["BAR"], troughcolor=theme["BG"], bordercolor=theme["CARD"], lightcolor=theme["BAR"], darkcolor=theme["BAR"])

    def start_scan_thread(self):
        if self.is_scanning: return
        self.is_scanning = True
        self.start_btn.config(state="disabled", text="SCANNING...")
        self.report_btn.config(state="disabled")
        threading.Thread(target=self.run_pro_check, daemon=True).start()

    def run_pro_check(self):
        self.check_processes()
        self.check_virtual_drives()
        self.scan_critical_dirs()
        self.check_obfuscated_configs()
        self.check_rustme_specifics()
        self.is_scanning = False
        self.root.after(0, self.finish_scan)

    def scan_critical_dirs(self):
        self.root.after(0, lambda: self.label.config(text="📂 Scanning critical locations..."))
        target_dirs = [
            os.path.join(os.environ["APPDATA"], ".minecraft"),
            os.path.join(os.environ["APPDATA"], "RustMe"),
            os.path.join(os.environ["LOCALAPPDATA"], "Temp"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Recent")
        ]
        keywords = ["akrien", "celestial", "deadcode", "expensive", "nurik", "zamora", "wild", "client", "hack", "cheat", "bypass", "loader", "inject", "hitbox", "reach", "killaura", "spoof", "spoofer"]
        ignore_list = ["site-packages", "pyqt5", "geometryloaders", "discord", "unity", "steam", "anydesk", "tesseract", "setup", "midnait"]
        
        found_files = []
        AI_SUSPECTS.clear()
        valid_dirs = [d for d in target_dirs if os.path.exists(d)]
        total_to_scan = sum(len(files) for d in valid_dirs for _, _, files in os.walk(d)) or 1
        
        scanned = 0
        for d in valid_dirs:
            for root_dir, _, files in os.walk(d):
                if any(ignore in root_dir.lower() for ignore in ignore_list): continue
                for file in files:
                    scanned += 1
                    if scanned % 100 == 0: self.root.after(0, lambda p=int(10+(scanned/total_to_scan)*80): self.progress.config(value=p))
                    name = file.lower()
                    path = os.path.join(root_dir, file)
                    if any(w in name for w in ["anydesk", "icu", "uniset", "setup"]): continue
                    
                    is_match = False
                    for k in keywords:
                        if k in name and name.endswith((".jar", ".dll", ".exe", ".zip", ".lnk")):
                            if "recent" in root_dir.lower(): self.add_suspect(path, 6, "Recent")
                            else: found_files.append(path)
                            is_match = True; break
                    if name.endswith((".jar", ".dll", ".exe")): self.deep_analyze_file(path)
        global FOUND_FILES
        FOUND_FILES = list(set(found_files))

    def deep_analyze_file(self, path):
        try:
            size = os.path.getsize(path) / 1024 / 1024
            if size > 150: return 
            name_low = os.path.basename(path).lower()
            with open(path, "rb") as f:
                data = f.read(10000000) 
                
                # Akcel Signatures (Strict)
                akcel_hard = [b"P}ng3wH", b"Q,9-EVV", b"S&ZOfzk-Z", b"Fi!NCbX?hT", b"[*V_M3{V"]
                akcel_base = [b"H&IU", b"HNIU", b"HVIU", b"H^IU"]
                if any(s in data for s in akcel_hard):
                    self.add_suspect(path, 10, "Spoof(A)")
                    return
                if sum(1 for s in akcel_base if s in data) >= 3:
                    self.add_suspect(path, 10, "loader(A)")
                    return

                # Nemezida Signatures (Strict)
                nem_hard = [b"DhEMCtP3", b"dd`KkbV+", b"\\DhEMCtP3", b"!bR2", b"!v=Or"]
                nem_base = [b"kQdeW", b"kALze_", b"kI)ae_", b"v*r7xj"]
                if any(s in data for s in nem_hard):
                    self.add_suspect(path, 10, "Spoof(N)")
                    return
                if sum(1 for s in nem_base if s in data) >= 3:
                    self.add_suspect(path, 10, "loader(N)")
                    return

                if any(s in data for s in [b"net/minecraft/client", b"EntityPlayerSP", b"killaura"]):
                    self.add_suspect(path, 5, "Minecraft")
        except: pass

    def add_suspect(self, path, score, t):
        if not any(s["path"] == path for s in AI_SUSPECTS): AI_SUSPECTS.append({"path": path, "score": score, "type": t})

    def check_obfuscated_configs(self):
        local = os.environ.get("LOCALAPPDATA")
        if not local: return
        chars = "䀻ぐ伧릫ꍯ跮⚅瓍₅づ┗斁敂攕"
        for file in os.listdir(local):
            if file.endswith(".cfg"):
                path = os.path.join(local, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(1024)
                        if any(c in content for c in chars): self.add_suspect(path, 10, "Cheat Config")
                except: pass

    def check_virtual_drives(self):
        try:
            out = subprocess.check_output("wmic logicaldisk get name,drivetype", shell=True).decode()
            for line in out.strip().split("\n")[1:]:
                p = line.split()
                if len(p) >= 2 and p[0] in ["Z:","X:","W:","B:"] and p[1] == "4": self.add_suspect(p[0], 7, "Virtual Drive")
        except: pass

    def check_processes(self):
        try:
            out = subprocess.check_output("tasklist /v", shell=True).decode("cp866", errors="ignore").lower()
            for k in ["akcel", "nemezida", "expensive", "deadcode"]:
                if k in out: self.add_suspect(k.upper(), 10, "Process")
        except: pass

    def check_rustme_specifics(self):
        rm = os.path.join(os.environ["APPDATA"], "RustMe")
        if os.path.exists(rm):
            for r, _, files in os.walk(rm):
                for f in files:
                    if f.lower().endswith(".dll") and f.lower() not in ["discord_game_sdk.dll", "unityplayer.dll"]: self.add_suspect(os.path.join(r, f), 5, "RustMe DLL")

    def finish_scan(self):
        self.progress.config(value=100); self.start_btn.config(state="normal", text="RESCAN"); self.report_btn.config(state="normal")
        if not FOUND_FILES and not AI_SUSPECTS: self.label.config(text="✅ System is Clean!", fg="#2ECC71")
        else: self.label.config(text="⚠️ Threats Detected!", fg="#E74C3C"); self.show_full_results()

    def show_full_results(self):
        if not FOUND_FILES and not AI_SUSPECTS: return
        theme = THEMES[self.current_theme]; win = tk.Toplevel(self.root); win.title("Security Report"); win.geometry("750x500"); win.configure(bg=theme["BG"])
        if os.path.exists(ICON_PATH):
            try: win.iconbitmap(ICON_PATH)
            except: pass
        tk.Label(win, text="DETECTION LOG", font=("Segoe UI", 14, "bold"), bg=theme["BG"], fg=theme["ACCENT"]).pack(pady=10)
        c = tk.Frame(win, bg=theme["BG"]); c.pack(fill="both", expand=True, padx=10, pady=5)
        tree = ttk.Treeview(c, columns=("Type", "Path", "Risk"), show="headings")
        for col, w in [("Type", 130), ("Path", 480), ("Risk", 80)]: tree.heading(col, text=col); tree.column(col, width=w)
        tree.pack(side="left", fill="both", expand=True); sb = tk.Scrollbar(c, command=tree.yview); sb.pack(side="right", fill="y"); tree.config(yscrollcommand=sb.set)
        res = []
        for f in FOUND_FILES: res.append({"type": "Name Match", "path": f, "risk": "HIGH", "prio": 3})
        for s in AI_SUSPECTS:
            t = s.get("type", "Heuristic"); p = 5
            if "loader" in t.lower(): p = 1
            elif "spoof" in t.lower(): p = 2
            elif "minecraft" in t.lower(): p = 4
            res.append({"type": t, "path": s["path"], "risk": "CRITICAL" if s["score"] >= 8 else "MEDIUM", "prio": p})
        res.sort(key=lambda x: (x["prio"], x["type"]))
        for r in res: tree.insert("", "end", values=(r["type"], r["path"], r["risk"]))
        tree.bind("<Double-1>", lambda e: os.startfile(os.path.dirname(tree.item(tree.selection()[0], "values")[1])) if "Recent" not in tree.item(tree.selection()[0], "values")[1] else None)
        tk.Label(win, text="Tip: Loaders and Spoofers are prioritized. Double-click to open folder.", font=("Segoe UI", 9), bg=theme["BG"], fg=theme["SUB"]).pack(pady=5)

    def load_theme(self):
        if os.path.exists(THEME_FILE):
            try:
                with open(THEME_FILE, "r") as f:
                    t = f.read().strip()
                    if t in THEMES: return t
            except: pass
        return "RustMe Orange"

    def save_theme(self):
        try:
            with open(THEME_FILE, "w") as f: f.write(self.current_theme)
        except: pass

    def switch_theme(self):
        keys = list(THEMES.keys()); self.current_theme = keys[(keys.index(self.current_theme) + 1) % len(keys)]; self.save_theme(); theme = THEMES[self.current_theme]
        self.root.configure(bg=theme["BG"]); self.main_container.configure(bg=theme["BG"]); self.card.configure(bg=theme["CARD"]); self.btn_frame.configure(bg=theme["CARD"])
        self.title.configure(bg=theme["CARD"], fg=theme["ACCENT"]); self.label.configure(bg=theme["CARD"], fg=theme["TEXT"]); self.status.configure(bg=theme["CARD"], fg=theme["SUB"])
        self.start_btn.configure(bg=theme["ACCENT"], fg=theme["BG"]); self.report_btn.configure(bg=theme["CARD"], fg=theme["SUB"]); self.theme_btn.configure(bg=theme["CARD"], fg=theme["SUB"]); self.update_progressbar_style(theme)

    def download_icon(self):
        if os.path.exists(ICON_PATH): return True
        try:
            r = requests.get(ICON_URL, timeout=5)
            with open(ICON_PATH, "wb") as f: f.write(r.content)
            return True
        except: return False

    def on_close(self): self.root.destroy(); os._exit(0)

if __name__ == "__main__":
    root = tk.Tk(); app = LoaderApp(root); root.mainloop()
