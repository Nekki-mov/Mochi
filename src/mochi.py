#!/usr/bin/env python3
"""
Mochi — Wagashi Linux package manager GUI
Wraps dango (pacman + yay)
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio
import subprocess
import os
import threading

# ─── Theme detection ──────────────────────────────────────────────────────────

def detect_edition():
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("VARIANT_ID="):
                    return line.strip().split("=")[1].strip('"').lower()
    except Exception:
        pass
    return "ayu"

def detect_dark_mode(edition):
    if edition == "sayuri":
        return True
    # KDE
    if edition in ("ayu", "sayuri"):
        try:
            result = subprocess.run(
                ["kreadconfig6", "--group", "General", "--key", "ColorScheme"],
                capture_output=True, text=True
            )
            return "dark" in result.stdout.lower()
        except Exception:
            pass
    # LXQt
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

def get_theme_css_path(edition, dark):
    base = os.path.join(os.path.dirname(__file__), "themes")
    if edition == "sayuri":
        return os.path.join(base, "sayuri.css")
    if edition == "mishio":
        return os.path.join(base, "mishio-dark.css" if dark else "mishio-light.css")
    if edition == "nayuki":
        return os.path.join(base, "nayuki-light.css" if not dark else "ayu-dark.css")
    # ayu default
    return os.path.join(base, "ayu-dark.css" if dark else "ayu-light.css")

def apply_theme(edition, dark):
    css_path = get_theme_css_path(edition, dark)
    if not os.path.exists(css_path):
        return
    provider = Gtk.CssProvider()
    provider.load_from_path(css_path)
    Gtk.StyleContext.add_provider_for_display(
        Gtk.Widget.get_default().get_display() if hasattr(Gtk.Widget, 'get_default') else None,
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

# ─── Package data ─────────────────────────────────────────────────────────────

WAGASHI_PACKAGES = [
    {"name": "windowmaker", "desc": "X11 window manager with a NeXTSTEP look and feel", "installed": False},
]

CATEGORIES = [
    {"id": "wagashi",         "label": "Wagashi Repo",            "icon": "🍡"},
    {"id": "search",          "label": "Search",                  "icon": "🔍"},
    {"id": "installed",       "label": "Installed",               "icon": "✓"},
    {"id": "updates",         "label": "Updates",                 "icon": "↑"},
]

# ─── Package operations ───────────────────────────────────────────────────────

def run_dango(args, callback):
    def _run():
        try:
            result = subprocess.run(
                ["dango"] + args,
                capture_output=True, text=True
            )
            GLib.idle_add(callback, result.returncode, result.stdout, result.stderr)
        except FileNotFoundError:
            GLib.idle_add(callback, -1, "", "dango not found")
    threading.Thread(target=_run, daemon=True).start()

def search_packages(query, callback):
    def _run():
        try:
            result = subprocess.run(
                ["pacman", "-Ss", query],
                capture_output=True, text=True
            )
            packages = parse_pacman_search(result.stdout)
            GLib.idle_add(callback, packages)
        except Exception as e:
            GLib.idle_add(callback, [])
    threading.Thread(target=_run, daemon=True).start()

def parse_pacman_search(output):
    packages = []
    lines = output.strip().split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if line and not line.startswith(" "):
            parts = line.split(" ")
            if len(parts) >= 2:
                repo_name = parts[0]
                version = parts[1] if len(parts) > 1 else ""
                installed = "[installed]" in line
                desc = lines[i+1].strip() if i+1 < len(lines) else ""
                name_parts = repo_name.split("/")
                name = name_parts[1] if len(name_parts) > 1 else repo_name
                packages.append({
                    "name": name,
                    "version": version,
                    "desc": desc,
                    "installed": installed,
                    "repo": name_parts[0] if len(name_parts) > 1 else "extra",
                })
                i += 2
                continue
        i += 1
    return packages[:50]

def get_installed_packages(callback):
    def _run():
        try:
            result = subprocess.run(
                ["pacman", "-Q"],
                capture_output=True, text=True
            )
            packages = []
            for line in result.stdout.strip().split("\n"):
                parts = line.split(" ")
                if len(parts) >= 2:
                    packages.append({"name": parts[0], "version": parts[1], "desc": "", "installed": True})
            GLib.idle_add(callback, packages)
        except Exception:
            GLib.idle_add(callback, [])
    threading.Thread(target=_run, daemon=True).start()

# ─── UI ───────────────────────────────────────────────────────────────────────

class PackageRow(Gtk.ListBoxRow):
    def __init__(self, pkg):
        super().__init__()
        self.pkg = pkg
        self.add_css_class("package-row")

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.set_margin_start(16)
        box.set_margin_end(16)
        box.set_margin_top(10)
        box.set_margin_bottom(10)

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        info.set_hexpand(True)

        name_lbl = Gtk.Label(label=pkg["name"])
        name_lbl.add_css_class("package-name")
        name_lbl.set_halign(Gtk.Align.START)

        desc_lbl = Gtk.Label(label=pkg.get("desc", ""))
        desc_lbl.add_css_class("package-desc")
        desc_lbl.set_halign(Gtk.Align.START)
        desc_lbl.set_ellipsize(3)  # PANGO_ELLIPSIZE_END

        info.append(name_lbl)
        info.append(desc_lbl)

        if pkg.get("installed"):
            action_btn = Gtk.Button(label="Remove")
            action_btn.add_css_class("remove-btn")
        else:
            action_btn = Gtk.Button(label="Install")
            action_btn.add_css_class("install-btn")

        action_btn.connect("clicked", self._on_action)
        action_btn.set_valign(Gtk.Align.CENTER)

        box.append(info)
        box.append(action_btn)
        self.set_child(box)

    def _on_action(self, btn):
        if self.pkg.get("installed"):
            run_dango(["-R", self.pkg["name"]], self._on_done)
            btn.set_label("Removing...")
        else:
            run_dango(["-S", self.pkg["name"]], self._on_done)
            btn.set_label("Installing...")
        btn.set_sensitive(False)

    def _on_done(self, code, stdout, stderr):
        if code == 0:
            self.pkg["installed"] = not self.pkg["installed"]
        # Refresh handled by parent


class MochiWindow(Gtk.ApplicationWindow):
    def __init__(self, app, edition, dark):
        super().__init__(application=app)
        self.edition = edition
        self.dark = dark
        self.set_title("Mochi")
        self.set_default_size(960, 620)

        self._build()
        self._show_wagashi()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.set_child(root)

        # Sidebar
        sidebar = self._build_sidebar()
        root.append(sidebar)

        # Main area
        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main.set_hexpand(True)

        # Search bar
        self.search = Gtk.SearchEntry()
        self.search.set_placeholder_text("Search packages...")
        self.search.add_css_class("search-bar")
        self.search.set_margin_top(8)
        self.search.set_margin_bottom(4)
        self.search.set_margin_start(8)
        self.search.set_margin_end(8)
        self.search.connect("search-changed", self._on_search)
        main.append(self.search)

        # Package list
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.pkg_list = Gtk.ListBox()
        self.pkg_list.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll.set_child(self.pkg_list)
        main.append(scroll)

        # Status bar
        self.statusbar = Gtk.Label(label="Ready.")
        self.statusbar.add_css_class("statusbar")
        self.statusbar.set_halign(Gtk.Align.START)
        self.statusbar.set_margin_start(16)
        self.statusbar.set_margin_top(4)
        self.statusbar.set_margin_bottom(4)
        main.append(self.statusbar)

        root.append(main)

    def _build_sidebar(self):
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar.add_css_class("sidebar")
        sidebar.set_size_request(220, -1)

        header = Gtk.Label(label="Mochi")
        header.add_css_class("sidebar-header")
        header.set_halign(Gtk.Align.START)
        header.set_margin_start(16)
        header.set_margin_top(12)
        header.set_margin_bottom(12)
        sidebar.append(header)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        sidebar.append(sep)

        for cat in CATEGORIES:
            btn = Gtk.Button(label=f"{cat['icon']}  {cat['label']}")
            btn.add_css_class("book-row")
            btn.set_has_frame(False)
            btn.set_halign(Gtk.Align.FILL)
            btn.connect("clicked", self._on_category, cat["id"])
            sidebar.append(btn)

        return sidebar

    def _show_wagashi(self):
        self._clear_list()
        wagashi_header = Gtk.Label(label="🍡  WAGASHI REPO")
        wagashi_header.add_css_class("wagashi-repo-header")
        wagashi_header.set_halign(Gtk.Align.FILL)
        self.pkg_list.append(wagashi_header)

        for pkg in WAGASHI_PACKAGES:
            self.pkg_list.append(PackageRow(pkg))

        self.statusbar.set_text(f"{len(WAGASHI_PACKAGES)} package(s) in Wagashi repo")

    def _on_category(self, btn, cat_id):
        if cat_id == "wagashi":
            self._show_wagashi()
        elif cat_id == "search":
            self.search.grab_focus()
        elif cat_id == "installed":
            self._clear_list()
            self.statusbar.set_text("Loading installed packages...")
            get_installed_packages(self._show_packages)
        elif cat_id == "updates":
            self._clear_list()
            self.statusbar.set_text("Checking for updates...")
            run_dango(["-Qu"], self._on_updates_done)

    def _on_search(self, entry):
        query = entry.get_text().strip()
        if len(query) < 2:
            return
        self._clear_list()
        self.statusbar.set_text(f"Searching for '{query}'...")
        search_packages(query, self._show_packages)

    def _show_packages(self, packages):
        self._clear_list()
        for pkg in packages:
            self.pkg_list.append(PackageRow(pkg))
        self.statusbar.set_text(f"{len(packages)} package(s) found")

    def _on_updates_done(self, code, stdout, stderr):
        packages = []
        for line in stdout.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 2:
                packages.append({"name": parts[0], "version": parts[1], "desc": "Update available", "installed": True})
        self._show_packages(packages)

    def _clear_list(self):
        while True:
            row = self.pkg_list.get_first_child()
            if row is None:
                break
            self.pkg_list.remove(row)


# ─── App ──────────────────────────────────────────────────────────────────────

def main():
    edition = detect_edition()
    dark = detect_dark_mode(edition)

    app = Gtk.Application(application_id="es.neklair.mochi")

    def on_activate(app):
        # Apply CSS theme
        css_path = get_theme_css_path(edition, dark)
        if os.path.exists(css_path):
            provider = Gtk.CssProvider()
            provider.load_from_path(css_path)
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

        win = MochiWindow(app, edition, dark)
        win.present()

    app.connect("activate", on_activate)
    app.run(None)

if __name__ == "__main__":
    from gi.repository import Gdk
    main()
