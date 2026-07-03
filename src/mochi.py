#!/usr/bin/env python3
"""
Mochi — Wagashi Linux package manager GUI
Wraps dango (pacman + yay)
"""

import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QLineEdit, QSizePolicy, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import json

CONFIG_PATH = os.path.expanduser("~/.config/mochi/config.json")

def load_config():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f)

# ─── Categories ───────────────────────────────────────────────────────────────

CATEGORIES = [
    {
        "id": "internet", "label": "Internet", "icon": "🌐",
        "desc": "Browsers, email, messaging and downloads",
        "packages": [
            {"name": "firefox",          "desc": "Fast, private and open-source web browser"},
            {"name": "chromium",         "desc": "Open-source base of Google Chrome"},
            {"name": "brave-bin",        "desc": "Privacy-focused browser with ad blocking"},
            {"name": "thunderbird",      "desc": "Email client with calendar support"},
            {"name": "evolution",        "desc": "Email, calendar and contacts suite"},
            {"name": "telegram-desktop", "desc": "Fast, cloud-based messaging app"},
            {"name": "signal-desktop",   "desc": "Private, end-to-end encrypted messaging"},
            {"name": "discord",          "desc": "Voice, video and text chat for communities"},
            {"name": "transmission-gtk", "desc": "Simple and lightweight BitTorrent client"},
            {"name": "qbittorrent",      "desc": "Feature-rich BitTorrent client"},
            {"name": "filezilla",        "desc": "FTP, SFTP and FTPS client"},
            {"name": "nextcloud-client", "desc": "Sync files with your Nextcloud server"},
            {"name": "element-desktop",  "desc": "Matrix chat client — decentralized messaging"},
        ]
    },
    {
        "id": "music_video", "label": "Music & Video", "icon": "🎵",
        "desc": "Media players, music and streaming",
        "packages": [
            {"name": "vlc",              "desc": "Plays almost any media file you throw at it"},
            {"name": "mpv",              "desc": "Minimal and powerful command-line media player"},
            {"name": "celluloid",        "desc": "Clean GTK4 frontend for mpv"},
            {"name": "rhythmbox",        "desc": "Music player and library manager"},
            {"name": "strawberry",       "desc": "Music player built for audiophiles"},
            {"name": "lollypop",         "desc": "Modern music player with a beautiful UI"},
            {"name": "amberol",          "desc": "Simple, opinionated music player"},
            {"name": "spotify-launcher", "desc": "Official Spotify client"},
            {"name": "nuclear",          "desc": "Stream music from free sources"},
            {"name": "audacious",        "desc": "Lightweight audio player — Winamp-style"},
            {"name": "elisa",            "desc": "KDE music player with a clean interface"},
            {"name": "haruna",           "desc": "Video player built on mpv and KDE"},
            {"name": "subtitlecomposer", "desc": "Subtitle editor for video files"},
        ]
    },
    {
        "id": "video_editing", "label": "Video Editing", "icon": "🎬",
        "desc": "Edit, encode, record and produce video",
        "packages": [
            {"name": "kdenlive",             "desc": "Professional non-linear video editor"},
            {"name": "shotcut",              "desc": "Free, cross-platform video editor"},
            {"name": "openshot",             "desc": "Easy-to-use video editor for beginners"},
            {"name": "obs-studio",           "desc": "Screen recording and live streaming"},
            {"name": "handbrake",            "desc": "Video transcoder — convert any format"},
            {"name": "ffmpeg",               "desc": "The Swiss Army knife of video/audio conversion"},
            {"name": "avisynth-plus",        "desc": "Video frameserver for advanced editing"},
            {"name": "mkvtoolnix-gui",       "desc": "Create and edit Matroska (MKV) files"},
            {"name": "mediainfo",            "desc": "Detailed technical info about video files"},
            {"name": "peek",                 "desc": "Record your screen as GIF or video"},
            {"name": "simplescreenrecorder", "desc": "Simple and fast screen recorder"},
        ]
    },
    {
        "id": "graphics", "label": "Photos & Graphics", "icon": "🖼️",
        "desc": "Image editing, illustration and photography",
        "packages": [
            {"name": "gimp",         "desc": "Powerful image editor — the Linux classic"},
            {"name": "krita",        "desc": "Professional digital painting and illustration"},
            {"name": "inkscape",     "desc": "Vector graphics editor — SVG native"},
            {"name": "darktable",    "desc": "Photography workflow and RAW processor"},
            {"name": "rawtherapee",  "desc": "Open-source RAW photo editor"},
            {"name": "digikam",      "desc": "Professional photo management"},
            {"name": "gwenview",     "desc": "Fast image viewer for KDE"},
            {"name": "gthumb",       "desc": "Image viewer and browser for GNOME"},
            {"name": "shotwell",     "desc": "Photo organizer for GNOME"},
            {"name": "pinta",        "desc": "Simple image editor inspired by Paint.NET"},
            {"name": "scribus",      "desc": "Desktop publishing and page layout"},
            {"name": "blender",      "desc": "3D modeling, animation and rendering"},
            {"name": "imagemagick",  "desc": "Command-line image processing toolkit"},
        ]
    },
    {
        "id": "office", "label": "Office", "icon": "📝",
        "desc": "Documents, spreadsheets, notes and PDFs",
        "packages": [
            {"name": "libreoffice-fresh",         "desc": "Full office suite — Writer, Calc, Impress"},
            {"name": "onlyoffice-desktopeditors",  "desc": "Office suite with excellent MS format support"},
            {"name": "okular",       "desc": "Universal document viewer for KDE"},
            {"name": "evince",       "desc": "Simple PDF and document viewer"},
            {"name": "zathura",      "desc": "Minimal, keyboard-driven PDF viewer"},
            {"name": "obsidian",     "desc": "Markdown knowledge base and note-taking"},
            {"name": "joplin-desktop","desc": "Note-taking with end-to-end encryption"},
            {"name": "typora",       "desc": "Minimal Markdown editor with live preview"},
            {"name": "calibre",      "desc": "E-book manager, reader and converter"},
            {"name": "foliate",      "desc": "Modern e-book reader for GNOME"},
        ]
    },
    {
        "id": "games", "label": "Games", "icon": "🎮",
        "desc": "Games, gaming tools and emulators",
        "packages": [
            {"name": "steam",                 "desc": "Valve's gaming platform — thousands of games"},
            {"name": "lutris",                "desc": "Game manager — runs Windows games via Wine"},
            {"name": "heroic-games-launcher",  "desc": "Epic Games and GOG launcher for Linux"},
            {"name": "gamemode",              "desc": "Automatically optimize system for gaming"},
            {"name": "mangohud",              "desc": "In-game performance overlay"},
            {"name": "bottles",               "desc": "Run Windows apps and games easily"},
            {"name": "retroarch",             "desc": "All-in-one emulator frontend"},
            {"name": "dolphin-emu",           "desc": "GameCube and Wii emulator"},
            {"name": "pcsx2",                 "desc": "PlayStation 2 emulator"},
            {"name": "ppsspp",                "desc": "PSP emulator"},
            {"name": "0ad",                   "desc": "Free and open-source real-time strategy"},
            {"name": "supertuxkart",          "desc": "Fun kart racing game"},
            {"name": "minetest",              "desc": "Open-source Minecraft-like game"},
        ]
    },
    {
        "id": "development", "label": "Development", "icon": "💻",
        "desc": "Code editors, tools, languages and runtimes",
        "packages": [
            {"name": "code",          "desc": "Visual Studio Code — popular code editor"},
            {"name": "neovim",        "desc": "Modern, extensible Vim-based text editor"},
            {"name": "kate",          "desc": "KDE's powerful text editor"},
            {"name": "git",           "desc": "Version control — you'll need this"},
            {"name": "github-cli",    "desc": "GitHub from the command line"},
            {"name": "python",        "desc": "Python programming language"},
            {"name": "nodejs",        "desc": "JavaScript runtime for the server"},
            {"name": "rustup",        "desc": "Rust language toolchain installer"},
            {"name": "go",            "desc": "Go programming language"},
            {"name": "docker",        "desc": "Container platform"},
            {"name": "docker-compose","desc": "Define multi-container Docker apps"},
            {"name": "postman-bin",   "desc": "API development and testing"},
            {"name": "dbeaver",       "desc": "Universal database manager"},
            {"name": "meld",          "desc": "Visual diff and merge tool"},
        ]
    },
    {
        "id": "system", "label": "System Tools", "icon": "🔧",
        "desc": "Utilities, backup and system management",
        "packages": [
            {"name": "htop",               "desc": "Interactive process viewer"},
            {"name": "btop",               "desc": "Beautiful resource monitor"},
            {"name": "gparted",            "desc": "Graphical disk partition editor"},
            {"name": "gnome-disk-utility", "desc": "Manage disks and disk images"},
            {"name": "timeshift",          "desc": "System backup and restore"},
            {"name": "baobab",             "desc": "Disk usage analyzer"},
            {"name": "bleachbit",          "desc": "System cleaner — free up disk space"},
            {"name": "cpu-x",              "desc": "CPU and system hardware information"},
            {"name": "ventoy",             "desc": "Create bootable USB drives"},
            {"name": "veracrypt",          "desc": "Strong disk encryption"},
            {"name": "keepassxc",          "desc": "Offline password manager"},
            {"name": "bitwarden",          "desc": "Password manager with cloud sync"},
            {"name": "syncthing",          "desc": "Sync files between devices — no cloud needed"},
        ]
    },
]

WAGASHI_PACKAGES = [
    {"name": "windowmaker", "version": "0.96.0-1", "desc": "X11 window manager with a NeXTSTEP look and feel"},
]

NAV_ITEMS = [
    ("wagashi",    "🍡", "Wagashi Repo"),
    ("categories", "📦", "Categories"),
    ("installed",  "✓",  "Installed"),
    ("updates",    "↑",  "Updates"),
]

# ─── Themes ───────────────────────────────────────────────────────────────────

THEMES = {
    # Light — Clannad · Sunfield (toned down, warm paper instead of gold) — used by Ayu, Mishio, Nayuki
    "light": {
        "bg": "#fffaf0", "card": "#fffaf0", "card2": "#f5ead5", "accent": "#484860", "accent2": "#304860",
        "text": "#180000", "text_muted": "#6a5848", "hover": "#f0e2c8", "highlight": "#f0d8d8",
        "app_bg": "#f0e6d2",
    },
    # Dark — Clannad · Firefly (deep night, soft purple) — used by Ayu, Mishio, Nayuki
    "dark": {
        "bg": "#000018", "card": "#10102c", "card2": "#181840", "accent": "#906090", "accent2": "#c0c0d8",
        "text": "#d8f0f0", "text_muted": "#9090b8", "hover": "#1c1c44", "highlight": "#d8a890",
        "app_bg": "#000010",
    },
    # Sayuri — fixed monochrome + coral, regardless of light/dark preference
    "sayuri": {
        "bg": "#000000", "card": "#0d0d0d", "card2": "#161616", "accent": "#e8a0a0", "accent2": "#e8a0a0",
        "text": "#e8e8e8", "text_muted": "#787878", "hover": "#1a1a1a", "highlight": "#e8a0a0",
        "app_bg": "#000000",
    },
}

def detect_edition():
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("VARIANT_ID="):
                    return line.strip().split("=", 1)[1].strip('"').lower()
    except Exception:
        pass
    return "ayu"

def detect_dark(edition):
    if edition == "sayuri":
        return True
    if edition == "ayu":
        try:
            r = subprocess.run(["kreadconfig6", "--group", "General", "--key", "ColorScheme"],
                                capture_output=True, text=True, timeout=2)
            return "dark" in r.stdout.lower()
        except Exception:
            pass
    if edition == "nayuki":
        try:
            cfg = os.path.expanduser("~/.config/lxqt/lxqt.conf")
            with open(cfg) as f:
                for line in f:
                    if "theme" in line.lower() and "dark" in line.lower():
                        return True
        except Exception:
            pass
    return False

def get_theme_key(edition, dark):
    if edition == "sayuri":
        return "sayuri"
    return "dark" if dark else "light"

# ─── Backend ──────────────────────────────────────────────────────────────────

def has_dango():
    try:
        subprocess.run(["dango", "--version"], capture_output=True, timeout=2)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return True

def check_installed(name):
    try:
        r = subprocess.run(["pacman", "-Q", name], capture_output=True, text=True, timeout=3)
        return r.returncode == 0
    except Exception:
        return False

def parse_pacman_ss(output):
    pkgs = []
    lines = output.strip().split("\n")
    i = 0
    while i < len(lines) - 1:
        line = lines[i]
        if line and not line.startswith(" ") and "/" in line:
            parts = line.split()
            repo_name = parts[0].split("/")
            name = repo_name[1] if len(repo_name) > 1 else repo_name[0]
            version = parts[1] if len(parts) > 1 else ""
            installed = "[instalado]" in line or "[installed]" in line
            desc = lines[i+1].strip() if i+1 < len(lines) else ""
            pkgs.append({"name": name, "version": version, "desc": desc, "installed": installed})
            i += 2
        else:
            i += 1
    return pkgs[:60]


class SearchThread(QThread):
    done = pyqtSignal(list)
    def __init__(self, query):
        super().__init__()
        self.query = query
    def run(self):
        try:
            r = subprocess.run(["pacman", "-Ss", self.query], capture_output=True, text=True, timeout=15)
            self.done.emit(parse_pacman_ss(r.stdout))
        except Exception:
            self.done.emit([])


class InstalledThread(QThread):
    done = pyqtSignal(list)
    def run(self):
        try:
            r = subprocess.run(["pacman", "-Q"], capture_output=True, text=True, timeout=10)
            pkgs = []
            for line in r.stdout.strip().split("\n"):
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    pkgs.append({"name": parts[0], "version": parts[1], "desc": "", "installed": True, "mode": "remove"})
            self.done.emit(pkgs)
        except Exception:
            self.done.emit([])


class UpdatesThread(QThread):
    done = pyqtSignal(list)
    def run(self):
        try:
            cmd = ["dango", "-Qu"] if has_dango() else ["pacman", "-Qu"]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            pkgs = []
            for line in r.stdout.strip().split("\n"):
                parts = line.split()
                if len(parts) >= 2:
                    pkgs.append({"name": parts[0], "version": parts[1], "desc": "Update available", "mode": "update"})
            self.done.emit(pkgs)
        except Exception:
            self.done.emit([])


class CategoryThread(QThread):
    done = pyqtSignal(list)
    def __init__(self, category):
        super().__init__()
        self.category = category
    def run(self):
        pkgs = []
        for pkg in self.category["packages"]:
            installed = check_installed(pkg["name"])
            pkgs.append({**pkg, "installed": installed, "mode": "remove" if installed else "install"})
        self.done.emit(pkgs)


class ActionThread(QThread):
    done = pyqtSignal(int, str, str)
    def __init__(self, name, mode):
        super().__init__()
        self.name = name
        self.mode = mode  # "install", "remove", "update"
    def run(self):
        flag = "-R" if self.mode == "remove" else "-S"
        if has_dango():
            cmd = ["dango", flag, self.name]
        else:
            cmd = ["pkexec", "pacman", flag, self.name, "--noconfirm"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            self.done.emit(r.returncode, r.stdout, r.stderr)
        except Exception as e:
            self.done.emit(-1, "", str(e))


class UpdateAllThread(QThread):
    line_received = pyqtSignal(str)
    done = pyqtSignal(int, str, str)
    def run(self):
        if has_dango():
            cmd = ["dango", "-Syu"]
        else:
            cmd = ["pkexec", "pacman", "-Syu", "--noconfirm"]
        full_output = []
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, universal_newlines=True
            )
            for line in proc.stdout:
                line = line.rstrip()
                if line:
                    full_output.append(line)
                    self.line_received.emit(line)
            proc.wait(timeout=900)
            self.done.emit(proc.returncode, chr(10).join(full_output), "")
        except Exception as e:
            self.done.emit(-1, chr(10).join(full_output), str(e))


# ─── UI helpers ───────────────────────────────────────────────────────────────

def mk_font(size=13, bold=False, family="Literata"):
    f = QFont(family, size)
    if bold:
        f.setWeight(QFont.Weight.DemiBold)
    return f


# ─── Widgets — floating card language ──────────────────────────────────────────

CARD_RADIUS = 18
INNER_RADIUS = 12

class PackageRow(QFrame):
    """A single package row inside a card — name, description, action button."""
    def __init__(self, pkg, theme, parent=None):
        super().__init__(parent)
        self.pkg = pkg
        self.theme = theme
        self._threads = []
        self._build()

    def _build(self):
        t = self.theme
        self.setStyleSheet("QFrame{background:transparent;border:none;}")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 10, 18, 10)
        lay.setSpacing(12)

        info = QVBoxLayout()
        info.setSpacing(3)
        info.setContentsMargins(0, 0, 0, 0)

        name_lbl = QLabel(self.pkg["name"])
        name_lbl.setFont(mk_font(13, bold=True))
        name_lbl.setStyleSheet("color:" + t["text"] + "; background:transparent; border:none;")

        desc_text = self.pkg.get("desc", "")
        version = self.pkg.get("version", "")
        if version:
            desc_text = (version + "  ·  " + desc_text) if desc_text else version

        desc_lbl = QLabel(desc_text)
        desc_lbl.setFont(mk_font(10))
        desc_lbl.setStyleSheet("color:" + t["text_muted"] + "; background:transparent; border:none;")

        info.addWidget(name_lbl)
        info.addWidget(desc_lbl)

        info_w = QWidget()
        info_w.setLayout(info)
        info_w.setStyleSheet("background:transparent; border:none;")
        info_w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        mode = self.pkg.get("mode", "install")
        label_map = {"install": "Install", "remove": "Remove", "update": "Update"}
        self.btn = QPushButton(label_map.get(mode, "Install"))
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.setFixedWidth(92)
        self.btn.setFixedHeight(34)
        self._style_btn(mode)
        self.btn.clicked.connect(self._on_click)

        lay.addWidget(info_w)
        lay.addWidget(self.btn)

    def _style_btn(self, mode):
        t = self.theme
        radius = INNER_RADIUS
        if mode in ("remove",):
            self.btn.setStyleSheet(
                f"QPushButton{{background:transparent;color:{t['accent']};border:1.5px solid {t['accent']};border-radius:{radius}px;font-size:11px;font-weight:600;}}"
                f"QPushButton:hover{{background:{t['accent']};color:{t['card']};}}"
            )
        else:
            self.btn.setStyleSheet(
                f"QPushButton{{background:{t['accent']};color:{t['card']};border:none;border-radius:{radius}px;font-size:11px;font-weight:bold;}}"
                f"QPushButton:hover{{background:{t['accent2']};}}"
            )

    def _on_click(self):
        mode = self.pkg.get("mode", "install")
        verbs = {"install": "Installing...", "remove": "Removing...", "update": "Updating..."}
        self.btn.setText(verbs.get(mode, "Working..."))
        self.btn.setEnabled(False)
        th = ActionThread(self.pkg["name"], mode)
        th.done.connect(self._on_done)
        self._threads.append(th)
        th.finished.connect(lambda t=th: self._threads.remove(t) if t in self._threads else None)
        th.start()

    def _on_done(self, code, stdout, stderr):
        self.btn.setEnabled(True)
        if code == 0:
            mode = self.pkg.get("mode", "install")
            if mode == "install":
                self.pkg["mode"] = "remove"
                self.btn.setText("Remove")
            elif mode == "remove":
                self.pkg["mode"] = "install"
                self.btn.setText("Install")
            elif mode == "update":
                self.btn.setText("Updated")
                self.btn.setEnabled(False)
                return
            self._style_btn(self.pkg["mode"])
        else:
            original = {"install": "Install", "remove": "Remove", "update": "Update"}
            self.btn.setText(original.get(self.pkg.get("mode", "install"), "Install"))
            self._style_btn(self.pkg.get("mode", "install"))


class RowDivider(QFrame):
    """Thin, soft divider between rows inside a card — no hard borders."""
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background:{theme['hover']}; border:none; margin: 0 18px;")


class SectionHeader(QFrame):
    """Floating pill-style header announcing the current section."""
    def __init__(self, text, theme, parent=None):
        super().__init__(parent)
        t = theme
        self.setStyleSheet(
            f"QFrame{{background:{t['accent']}; border:none; border-radius:{INNER_RADIUS}px;}}"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 9, 16, 9)
        lbl = QLabel(text)
        lbl.setFont(mk_font(10, bold=True))
        lbl.setStyleSheet(f"color:{t['card']}; background:transparent; border:none; letter-spacing: 1.5px;")
        lay.addWidget(lbl)


class CategoryCard(QFrame):
    def __init__(self, category, theme, on_click, parent=None):
        super().__init__(parent)
        self.category = category
        self.theme = theme
        self.on_click = on_click
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build()

    def _build(self):
        t = self.theme
        self.setStyleSheet("QFrame{background:transparent;border:none;}")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 13, 18, 13)
        lay.setSpacing(14)

        icon = QLabel(self.category["icon"])
        icon.setFont(mk_font(18))
        icon.setStyleSheet("background:transparent; border:none;")

        info = QVBoxLayout()
        info.setSpacing(2)
        info.setContentsMargins(0, 0, 0, 0)
        name = QLabel(self.category["label"])
        name.setFont(mk_font(13, bold=True))
        name.setStyleSheet(f"color:{t['text']}; background:transparent; border:none;")
        desc = QLabel(self.category["desc"])
        desc.setFont(mk_font(10))
        desc.setStyleSheet(f"color:{t['text_muted']}; background:transparent; border:none;")
        info.addWidget(name)
        info.addWidget(desc)
        info_w = QWidget()
        info_w.setLayout(info)
        info_w.setStyleSheet("background:transparent; border:none;")
        info_w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        count = QLabel(f"{len(self.category['packages'])} apps  ›")
        count.setFont(mk_font(10))
        count.setStyleSheet(f"color:{t['text_muted']}; background:transparent; border:none;")

        lay.addWidget(icon)
        lay.addWidget(info_w)
        lay.addWidget(count)

    def mousePressEvent(self, e):
        self.on_click(self.category)


class NavButton(QFrame):
    """Floating pill nav item — no hard left border, just a soft fill when active."""
    def __init__(self, icon, label, theme, on_click, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.on_click = on_click
        self._active = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(40)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 14, 0)
        self.lbl = QLabel(icon + "   " + label)
        self.lbl.setFont(mk_font(12))
        lay.addWidget(self.lbl)
        self._style()

    def set_active(self, v):
        self._active = v
        self._style()

    def _style(self):
        t = self.theme
        weight = "font-weight:bold;" if self._active else ""
        self.lbl.setStyleSheet(f"color:{t['text']}; background:transparent; border:none;{weight}")
        radius = INNER_RADIUS
        if self._active:
            self.setStyleSheet(f"QFrame{{background:{t['accent']}; border-radius:{radius}px;}}")
            self.lbl.setStyleSheet(f"color:{t['card']}; background:transparent; border:none; font-weight:bold;")
        else:
            self.setStyleSheet(
                f"QFrame{{background:transparent; border-radius:{radius}px;}}"
                f"QFrame:hover{{background:{t['hover']};}}"
            )

    def mousePressEvent(self, e):
        self.on_click()


class Card(QFrame):
    """A floating card — the base unit of the Material-ish language."""
    def __init__(self, theme, radius=CARD_RADIUS, parent=None):
        super().__init__(parent)
        t = theme
        self.setStyleSheet(
            f"QFrame{{background:{t['card']}; border:none; border-radius:{radius}px;}}"
        )


# ─── Main Window ──────────────────────────────────────────────────────────────

class MochiWindow(QMainWindow):
    def __init__(self, edition, dark):
        super().__init__()
        self.edition = edition
        self.dark = dark
        self.theme = THEMES[get_theme_key(edition, dark)]
        self._threads = []
        self._current_header = None
        self._pending_updates = []
        self._active_nav = "wagashi"
        self._build()
        self._show_wagashi()

    def _build(self):
        self.setWindowTitle("Mochi")
        self.setMinimumSize(980, 640)
        self.resize(1080, 700)
        central = QWidget()
        self.setCentralWidget(central)
        self._build_into(central)

    def _build_into(self, central):
        t = self.theme
        central.setStyleSheet(f"background:{t['app_bg']};")

        outer = QHBoxLayout(central)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(16)

        # ── Sidebar card ──
        sidebar = Card(t, radius=CARD_RADIUS)
        sidebar.setFixedWidth(240)
        slay = QVBoxLayout(sidebar)
        slay.setContentsMargins(0, 0, 0, 0)
        slay.setSpacing(0)

        header_row = QFrame()
        header_row.setStyleSheet("background:transparent; border:none;")
        hlay = QHBoxLayout(header_row)
        hlay.setContentsMargins(20, 18, 16, 12)

        title = QLabel("Mochi")
        title.setFont(mk_font(20, bold=True))
        title.setStyleSheet(f"color:{t['text']}; background:transparent; border:none;")

        sayuri_mode = (self.edition == "sayuri")
        self.theme_btn = QPushButton("◐" if not self.dark else "◑")
        self.theme_btn.setFixedSize(30, 30)
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.setStyleSheet(
            f"QPushButton{{background:transparent;border:1.5px solid {t['hover']};border-radius:15px;color:{t['text_muted']};font-size:13px;}}"
            f"QPushButton:hover{{background:{t['hover']};border-color:{t['accent']};color:{t['accent']};}}"
        )
        self.theme_btn.clicked.connect(self._toggle_theme)
        if sayuri_mode:
            self.theme_btn.setVisible(False)

        hlay.addWidget(title)
        hlay.addStretch()
        hlay.addWidget(self.theme_btn)
        slay.addWidget(header_row)

        nav_container = QFrame()
        nav_container.setStyleSheet("background:transparent; border:none;")
        nlay = QVBoxLayout(nav_container)
        nlay.setContentsMargins(10, 4, 10, 4)
        nlay.setSpacing(2)

        self.nav_buttons = {}
        for cat_id, icon, label in NAV_ITEMS:
            btn = NavButton(icon, label, t, lambda cid=cat_id: self._on_nav(cid))
            nlay.addWidget(btn)
            self.nav_buttons[cat_id] = btn

        slay.addWidget(nav_container)
        slay.addStretch()
        outer.addWidget(sidebar)

        # ── Main column ──
        main_col = QVBoxLayout()
        main_col.setSpacing(16)
        main_col.setContentsMargins(0, 0, 0, 0)

        # Top bar card (search + actions)
        topbar = Card(t, radius=CARD_RADIUS)
        topbar.setFixedHeight(60)
        tlay = QHBoxLayout(topbar)
        tlay.setContentsMargins(14, 10, 14, 10)
        tlay.setSpacing(10)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search packages...")
        self.search_box.setFixedHeight(38)
        self.search_box.setFont(mk_font(12))
        self.search_box.setStyleSheet(
            f"QLineEdit{{background:{t['app_bg']};border:none;border-radius:{INNER_RADIUS}px;padding:0 16px;color:{t['text']};font-size:12px;}}"
            f"QLineEdit:focus{{border:1.5px solid {t['accent']};}}"
        )
        self.search_box.textChanged.connect(self._on_search)

        self.update_all_btn = QPushButton("Update All")
        self.update_all_btn.setFixedHeight(38)
        self.update_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_all_btn.setFont(mk_font(11, bold=True))
        self.update_all_btn.setStyleSheet(
            f"QPushButton{{background:{t['accent']};color:{t['card']};border:none;border-radius:{INNER_RADIUS}px;padding:0 18px;}}"
            f"QPushButton:hover{{background:{t['accent2']};}}"
        )
        self.update_all_btn.clicked.connect(self._on_update_all)
        self.update_all_btn.hide()

        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setFixedSize(38, 38)
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.setToolTip("Check for updates")
        self.refresh_btn.setStyleSheet(
            f"QPushButton{{background:{t['app_bg']};border:none;border-radius:{INNER_RADIUS}px;color:{t['text']};font-size:16px;}}"
            f"QPushButton:hover{{background:{t['hover']};color:{t['accent']};}}"
        )
        self.refresh_btn.clicked.connect(lambda: self._on_nav("updates"))

        tlay.addWidget(self.search_box)
        tlay.addWidget(self.update_all_btn)
        tlay.addWidget(self.refresh_btn)
        main_col.addWidget(topbar)

        # Content card (scroll list or log view)
        content_card = Card(t, radius=CARD_RADIUS)
        clay = QVBoxLayout(content_card)
        clay.setContentsMargins(0, 0, 0, 0)
        clay.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet(
            "QScrollArea{background:transparent; border:none;}"
            "QScrollBar:vertical{background:transparent; width:8px; margin:4px 2px 4px 0;}"
            f"QScrollBar::handle:vertical{{background:{t['text_muted']}; border-radius:4px; min-height:24px;}}"
            f"QScrollBar::handle:vertical:hover{{background:{t['accent']};}}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical{height:0px; background:none;}"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical{background:none;}"
        )

        self.list_widget = QWidget()
        self.list_widget.setStyleSheet("background:transparent;")
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(8, 12, 8, 12)
        self.list_layout.setSpacing(2)
        self.scroll.setWidget(self.list_widget)
        clay.addWidget(self.scroll)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("monospace", 10))
        self.log_view.setStyleSheet(
            f"QTextEdit{{background:transparent;color:{t['text']};border:none;padding:18px 22px;}}"
        )
        self.log_view.hide()
        clay.addWidget(self.log_view)

        main_col.addWidget(content_card)

        # Status bar card (slim)
        status_card = Card(t, radius=INNER_RADIUS)
        status_card.setFixedHeight(34)
        stlay = QHBoxLayout(status_card)
        stlay.setContentsMargins(18, 0, 18, 0)
        self.status = QLabel()
        self.status.setFont(mk_font(9))
        self.status.setStyleSheet(f"color:{t['text_muted']}; background:transparent; border:none;")
        stlay.addWidget(self.status)
        main_col.addWidget(status_card)

        main_widget = QWidget()
        main_widget.setLayout(main_col)
        outer.addWidget(main_widget)

    # ── List management ──

    def _clear_list(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

    def _set_active(self, cat_id):
        for cid, btn in self.nav_buttons.items():
            btn.set_active(cid == cat_id)

    def _add_rows(self, packages):
        for i, pkg in enumerate(packages):
            if i > 0:
                self.list_layout.addWidget(RowDivider(self.theme))
            self.list_layout.addWidget(PackageRow(pkg, self.theme))

    def _render(self, header_text, packages):
        self._clear_list()
        if header_text:
            self.list_layout.addWidget(SectionHeader(header_text, self.theme))
            self.list_layout.addSpacing(4)
        self._add_rows(packages)
        self.list_layout.addStretch()
        self.status.setText(f"{len(packages)} package(s)")

    # ── Navigation ──

    def _on_nav(self, cat_id):
        self._active_nav = cat_id
        self._set_active(cat_id)
        if cat_id != "updates":
            self.update_all_btn.hide()
        if cat_id == "wagashi":
            self._show_wagashi()
        elif cat_id == "categories":
            self._show_categories()
        elif cat_id == "installed":
            self.status.setText("Loading installed packages...")
            self._clear_list()
            th = InstalledThread()
            th.done.connect(lambda pkgs: self._render(None, pkgs))
            self._threads.append(th)
            th.finished.connect(lambda t=th: self._threads.remove(t) if t in self._threads else None)
            th.start()
        elif cat_id == "updates":
            self.status.setText("Checking for updates...")
            self._clear_list()
            th = UpdatesThread()
            th.done.connect(self._on_updates_result)
            self._threads.append(th)
            th.finished.connect(lambda t=th: self._threads.remove(t) if t in self._threads else None)
            th.start()

    def _on_updates_result(self, packages):
        self._pending_updates = packages
        if not packages:
            self._clear_list()
            self.status.setText("Everything is up to date. 🍡")
            self.update_all_btn.hide()
        else:
            self._render(f"↑  {len(packages)} UPDATE(S) AVAILABLE", packages)
            self.update_all_btn.show()

    def _on_update_all(self):
        self.update_all_btn.setText("Updating...")
        self.update_all_btn.setEnabled(False)
        self.search_box.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        self.scroll.hide()
        self.log_view.clear()
        self.log_view.show()
        self.status.setText("Updating all packages — this may take a while...")
        th = UpdateAllThread()
        th.line_received.connect(self._on_update_line)
        th.done.connect(self._on_update_all_done)
        self._threads.append(th)
        th.finished.connect(lambda t=th: self._threads.remove(t) if t in self._threads else None)
        th.start()

    def _on_update_line(self, line):
        self.log_view.append(line)
        self.log_view.verticalScrollBar().setValue(self.log_view.verticalScrollBar().maximum())

    def _on_update_all_done(self, code, stdout, stderr):
        self.update_all_btn.setEnabled(True)
        self.update_all_btn.setText("Update All")
        self.search_box.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        self.log_view.hide()
        self.scroll.show()
        if code == 0:
            self.update_all_btn.hide()
            self._clear_list()
            self.status.setText("Everything is up to date. 🍡")
        else:
            self.status.setText("Update finished with errors — check above for details.")

    def _on_search(self, text):
        q = text.strip()
        if len(q) < 2:
            return
        self._set_active(None)
        self.update_all_btn.hide()
        self.status.setText(f"Searching for '{q}'...")
        self._clear_list()
        th = SearchThread(q)
        th.done.connect(lambda pkgs: self._render(None, [
            {**p, "mode": "remove" if p.get("installed") else "install"} for p in pkgs
        ]))
        self._threads.append(th)
        th.finished.connect(lambda t=th: self._threads.remove(t) if t in self._threads else None)
        th.start()

    def _show_wagashi(self):
        pkgs = []
        for pkg in WAGASHI_PACKAGES:
            installed = check_installed(pkg["name"])
            pkgs.append({**pkg, "installed": installed, "mode": "remove" if installed else "install"})
        self._render("🍡  WAGASHI REPO", pkgs)

    def _show_categories(self):
        self._clear_list()
        self.list_layout.addWidget(SectionHeader("📦  CATEGORIES", self.theme))
        self.list_layout.addSpacing(4)
        for i, cat in enumerate(CATEGORIES):
            if i > 0:
                self.list_layout.addWidget(RowDivider(self.theme))
            self.list_layout.addWidget(CategoryCard(cat, self.theme, self._show_category))
        self.list_layout.addStretch()
        self.status.setText(f"{len(CATEGORIES)} categories")

    def _show_category(self, category):
        self._current_header = f"{category['icon']}  {category['label'].upper()}"
        self._clear_list()
        self.list_layout.addWidget(SectionHeader(self._current_header, self.theme))
        self.list_layout.addSpacing(4)
        self.list_layout.addStretch()
        self.status.setText("Checking installed packages...")
        th = CategoryThread(category)
        th.done.connect(lambda pkgs: self._render(self._current_header, pkgs))
        self._threads.append(th)
        th.finished.connect(lambda t=th: self._threads.remove(t) if t in self._threads else None)
        th.start()

    def _toggle_theme(self):
        if self.edition == "sayuri":
            return
        self.dark = not self.dark
        cfg = load_config()
        cfg["dark"] = self.dark
        save_config(cfg)
        self.theme = THEMES[get_theme_key(self.edition, self.dark)]
        central = QWidget()
        self.setCentralWidget(central)
        self._build_into(central)
        self._on_nav(self._active_nav)


# ─── Entry ────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Mochi")
    app.setOrganizationName("Wagashi Linux")

    edition = detect_edition()
    cfg = load_config()
    if "dark" in cfg:
        dark = cfg["dark"]
    else:
        dark = detect_dark(edition)

    win = MochiWindow(edition, dark)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
