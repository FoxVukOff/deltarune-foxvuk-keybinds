# -*- coding: utf-8 -*-
"""
================================================================
 Deltarune Key Remapper v1.1.1
================================================================

GUI-only key remapper with multi-profile support and hotkeys.

Target keys (what the game receives):
    Up / Left / Down / Right  —  movement
    Z                         —  confirm / interact
    X                         —  cancel / run
    C                         —  phone / call menu

Source keys (what you press) — fully customizable per profile.
Set to null to disable remapping for that key.

Hotkeys (global):
    Ctrl+Alt+V          — toggle remap on/off
    Ctrl+Alt+Backspace  — quit the program
    Ctrl+Alt+P+0-9      — switch profile (0=Default, 1-9=custom)

================================================================
"""

import ctypes
import json
import os
import sys
import time
from datetime import datetime

try:
    import keyboard
except ImportError:
    print("Library 'keyboard' is not installed.")
    print("Install it with:  pip install keyboard")
    sys.exit(1)

try:
    import win32gui
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QLabel, QVBoxLayout,
        QHBoxLayout, QWidget, QPushButton, QFrame, QComboBox,
        QFileDialog, QMessageBox, QLineEdit, QScrollArea,
        QGroupBox, QSizePolicy
    )
    from PyQt6.QtCore import Qt, QTimer, QSize
    from PyQt6.QtGui import QPalette, QColor, QFont, QIcon, QPainter, QPen, QBrush, QPixmap
    HAS_PYQT = True
except ImportError:
    HAS_PYQT = False


# ================================================================
# Constants
# ================================================================

# Fix paths for both EXE and script modes
if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

PROFILES_FILE = os.path.join(SCRIPT_DIR, "profiles.json")
PREFERENCES_FILE = os.path.join(SCRIPT_DIR, "preferences.json")

CURRENT_VERSION = "1.1.1"
UPDATE_URL = "https://raw.githubusercontent.com/FoxVukOff/deltarune-foxvuk-keybinds/refs/heads/main/version.txt"
REPO_URL = "https://github.com/FoxVukOff/deltarune-foxvuk-keybinds"

TARGET_ORDER = ["up", "down", "left", "right", "z", "x", "c"]

DEFAULT_PROFILE_TARGETS = {
    "up": "w",
    "down": "s",
    "left": "a",
    "right": "d",
    "z": "q",
    "x": "e",
    "c": "r",
}

DEFAULT_CONFIG = {
    "language": None,
    "active_profile": "Default",
    "hotkeys": {
        "toggle": "ctrl+alt+v",
        "quit": "ctrl+alt+backspace",
    },
    "profile_hotkeys": {
        "0": "ctrl+alt+p+0",
        "1": "ctrl+alt+p+1",
        "2": "ctrl+alt+p+2",
        "3": "ctrl+alt+p+3",
        "4": "ctrl+alt+p+4",
        "5": "ctrl+alt+p+5",
        "6": "ctrl+alt+p+6",
        "7": "ctrl+alt+p+7",
        "8": "ctrl+alt+p+8",
        "9": "ctrl+alt+p+9",
    },
    "window_check": True,
    "logs_enabled": True,
    "log_level": "info",
    "version": "1.1.1",
}

VALID_KEYS = {
    "a","b","c","d","e","f","g","h","i","j","k","l","m",
    "n","o","p","q","r","s","t","u","v","w","x","y","z",
    "0","1","2","3","4","5","6","7","8","9",
    "up","down","left","right",
    "f1","f2","f3","f4","f5","f6","f7","f8","f9","f10","f11","f12",
    "space","enter","tab","esc","backspace","delete","insert",
    "home","end","pageup","pagedown",
    "capslock","numlock","scrolllock",
    "`","-","=","[","]","\\",";","'",",",".","/",
}

MAX_QUICK_PROFILES = 9  # digits 1-9, Default on 0


# ================================================================
# OSD Window (borderless overlay, auto-hides)
# ================================================================

class OSDWindow(QWidget):
    """Borderless overlay window that shows a message and auto-hides."""
    _instance = None

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                background: rgba(0, 0, 0, 180);
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.hide)
        self.timer.setSingleShot(True)

        self.resize(300, 60)
        self._center()

    def _center(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() - 120
        self.move(x, y)

    def show_message(self, text: str, duration_ms: int = 2000):
        self.label.setText(text)
        self.show()
        self.raise_()
        self.timer.start(duration_ms)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = OSDWindow()
        return cls._instance

    @classmethod
    def show(cls, text: str, duration_ms: int = 2000):
        cls.get_instance().show_message(text, duration_ms)


# ================================================================
# Logging
# ================================================================

LOG_LEVELS = {"debug": 0, "info": 1, "warn": 2, "error": 3}
_log_config = {"enabled": True, "level": "info"}


def log(msg: str, level: str = "info"):
    if not _log_config["enabled"]:
        return
    if LOG_LEVELS.get(level, 1) < LOG_LEVELS.get(_log_config["level"], 1):
        return
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  [{ts}] [{level.upper()}] {msg}")


def set_logging(enabled: bool, level: str = "info"):
    _log_config["enabled"] = enabled
    _log_config["level"] = level


# ================================================================
# Migration
# ================================================================

def migrate_preferences(data: dict) -> dict:
    """Migrate old preferences to current format."""
    old_ver = data.get("version", "1.0.0")

    # Handle very old formats (v1.0.0-v1.0.4)
    if old_ver in ("1.0.0", "1.0.1", "1.0.2", "1.0.3", "1.0.4", None):
        targets = data.get("targets", data.get("remap", {}))
        if targets:
            # Check if it's old format (source -> target like "w": "up")
            if "w" in targets and targets["w"] == "up":
                new_targets = {}
                for src, tgt in targets.items():
                    if tgt in TARGET_ORDER:
                        new_targets[tgt] = src
                targets = new_targets
            for t in TARGET_ORDER:
                if t not in targets:
                    targets[t] = DEFAULT_PROFILE_TARGETS.get(t, "unknown")
        data["targets"] = targets
        data.pop("remap", None)
        data.pop("layout_preset", None)

    # Ensure profile_hotkeys exists
    if "profile_hotkeys" not in data:
        data["profile_hotkeys"] = dict(DEFAULT_CONFIG["profile_hotkeys"])

    # Ensure hotkeys exists
    if "hotkeys" not in data:
        data["hotkeys"] = dict(DEFAULT_CONFIG["hotkeys"])

    data["version"] = CURRENT_VERSION
    return data


def migrate_to_profiles(config: dict) -> dict:
    """Convert old single-config to multi-profile format."""
    profiles_file_exists = os.path.exists(PROFILES_FILE)
    profiles = load_profiles()

    # If profiles file already exists with real data, don't overwrite
    if profiles_file_exists and len(profiles.get("profiles", {})) > 1:
        return profiles

    # Create Default profile from old config (or use defaults)
    targets = config.get("targets", None)
    if targets and isinstance(targets, dict) and "w" in targets:
        # Old format had source->target, need to invert
        new_targets = {}
        for src, tgt in targets.items():
            if tgt in TARGET_ORDER:
                new_targets[tgt] = src
        if new_targets:
            targets = new_targets

    if not targets or not isinstance(targets, dict):
        targets = dict(DEFAULT_PROFILE_TARGETS)

    # Ensure all targets exist
    for t in TARGET_ORDER:
        if t not in targets:
            targets[t] = DEFAULT_PROFILE_TARGETS.get(t, "unknown")

    profiles["profiles"]["Default"] = {
        "targets": targets,
        "created": datetime.now().isoformat(),
        "modified": datetime.now().isoformat(),
    }
    profiles["active"] = config.get("active_profile", "Default")

    save_profiles(profiles)
    return profiles


# ================================================================
# Profiles management
# ================================================================

def load_profiles() -> dict:
    """Load profiles from JSON. Returns structured data."""
    default = {
        "active": "Default",
        "profiles": {
            "Default": {
                "targets": dict(DEFAULT_PROFILE_TARGETS),
                "created": "2026-01-01T00:00:00",
                "modified": "2026-01-01T00:00:00",
            }
        },
    }

    if os.path.exists(PROFILES_FILE):
        try:
            with open(PROFILES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate structure
            if "profiles" not in data or not isinstance(data["profiles"], dict):
                log("Profiles file corrupted, using defaults", "warn")
                return default

            # Ensure Default exists and is correct
            if "Default" not in data["profiles"]:
                data["profiles"]["Default"] = default["profiles"]["Default"]
            else:
                # Default always reverts to hardcoded values
                data["profiles"]["Default"]["targets"] = dict(DEFAULT_PROFILE_TARGETS)

            # Validate each profile
            for name, profile in list(data["profiles"].items()):
                if "targets" not in profile or not isinstance(profile["targets"], dict):
                    log(f"Profile '{name}' corrupted, removing", "warn")
                    del data["profiles"][name]
                    continue
                # Ensure all targets exist (null is allowed = disabled)
                for t in TARGET_ORDER:
                    if t not in profile["targets"]:
                        profile["targets"][t] = DEFAULT_PROFILE_TARGETS.get(t, "unknown")

            if "active" not in data or data["active"] not in data["profiles"]:
                data["active"] = "Default"

            return data

        except (json.JSONDecodeError, IOError) as e:
            log(f"Failed to load profiles: {e}, using defaults", "warn")
            return default

    return default


def save_profiles(profiles: dict):
    """Save profiles to JSON."""
    with open(PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)
    log(f"Profiles saved ({len(profiles['profiles'])} profiles)")


def create_profile(profiles: dict, name: str) -> tuple[bool, str]:
    """Create a new profile. Returns (created, message)."""
    if name in profiles["profiles"]:
        return False, "exists"
    if not name.strip():
        return False, "empty"

    # Count custom profiles (excluding Default)
    custom_count = len([p for p in profiles["profiles"] if p != "Default"])

    # Assign hotkey digit if available
    hotkey_digit = None
    if custom_count < MAX_QUICK_PROFILES:
        # Find next available digit
        used_digits = set()
        for pname, pdata in profiles["profiles"].items():
            if pname != "Default" and "hotkey_digit" in pdata:
                used_digits.add(pdata["hotkey_digit"])
        for d in range(1, 10):
            if str(d) not in used_digits:
                hotkey_digit = str(d)
                break

    profiles["profiles"][name] = {
        "targets": dict(DEFAULT_PROFILE_TARGETS),
        "created": datetime.now().isoformat(),
        "modified": datetime.now().isoformat(),
    }
    if hotkey_digit:
        profiles["profiles"][name]["hotkey_digit"] = hotkey_digit

    save_profiles(profiles)
    log(f"Profile created: {name}" + (f" (hotkey: Ctrl+Alt+P+{hotkey_digit})" if hotkey_digit else " (no quick hotkey)"))

    msg = ""
    if custom_count >= MAX_QUICK_PROFILES:
        msg = f"Quick profiles exhausted ({MAX_QUICK_PROFILES} max). This profile has no hotkey."
    elif hotkey_digit:
        msg = f"Profile created with hotkey: Ctrl+Alt+P+{hotkey_digit}"

    return True, msg


def delete_profile(profiles: dict, name: str) -> bool:
    """Delete a profile. Cannot delete Default. Returns True if deleted."""
    if name == "Default":
        return False
    if name not in profiles["profiles"]:
        return False

    del profiles["profiles"][name]
    if profiles["active"] == name:
        profiles["active"] = "Default"
    save_profiles(profiles)
    log(f"Profile deleted: {name}")
    return True


def rename_profile(profiles: dict, old_name: str, new_name: str) -> bool:
    """Rename a profile. Cannot rename Default. Returns True if renamed."""
    if old_name == "Default":
        return False
    if new_name == "Default":
        return False
    if old_name not in profiles["profiles"]:
        return False
    if new_name in profiles["profiles"]:
        return False
    if not new_name.strip():
        return False

    profiles["profiles"][new_name] = profiles["profiles"].pop(old_name)
    profiles["profiles"][new_name]["modified"] = datetime.now().isoformat()
    if profiles["active"] == old_name:
        profiles["active"] = new_name
    save_profiles(profiles)
    log(f"Profile renamed: {old_name} -> {new_name}")
    return True


def update_profile_targets(profiles: dict, name: str, targets: dict):
    """Update targets for a profile."""
    if name in profiles["profiles"]:
        profiles["profiles"][name]["targets"] = dict(targets)
        profiles["profiles"][name]["modified"] = datetime.now().isoformat()
        save_profiles(profiles)
        log(f"Profile updated: {name}")


def export_profile(profiles: dict, name: str, filepath: str) -> bool:
    """Export a profile to a JSON file."""
    if name not in profiles["profiles"]:
        return False
    try:
        data = {
            "profile_name": name,
            "targets": profiles["profiles"][name]["targets"],
            "exported": datetime.now().isoformat(),
            "version": CURRENT_VERSION,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log(f"Profile exported: {name} -> {filepath}")
        return True
    except Exception as e:
        log(f"Export failed: {e}", "error")
        return False


def import_profile(profiles: dict, filepath: str) -> str | None:
    """Import a profile from a JSON file. Returns profile name or None."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        name = data.get("profile_name", "Imported")
        targets = data.get("targets", {})

        if not targets:
            log("Import failed: no targets in file", "error")
            return None

        # Ensure all targets
        for t in TARGET_ORDER:
            if t not in targets:
                targets[t] = DEFAULT_PROFILE_TARGETS.get(t, "unknown")

        # Handle name collision
        original_name = name
        counter = 1
        while name in profiles["profiles"]:
            name = f"{original_name} ({counter})"
            counter += 1

        profiles["profiles"][name] = {
            "targets": targets,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
        }
        save_profiles(profiles)
        log(f"Profile imported: {name}")
        return name

    except Exception as e:
        log(f"Import failed: {e}", "error")
        return None


# ================================================================
# Preferences
# ================================================================

def load_preferences() -> dict:
    if os.path.exists(PREFERENCES_FILE):
        try:
            with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Migrate old format (any version before current)
            old_ver = data.get("version", "1.0.0")
            if old_ver != CURRENT_VERSION:
                data = migrate_preferences(data)

            config = dict(DEFAULT_CONFIG)
            config.update(data)
            if "hotkeys" in data:
                hotkeys = dict(DEFAULT_CONFIG["hotkeys"])
                hotkeys.update(data["hotkeys"])
                config["hotkeys"] = hotkeys
            if "profile_hotkeys" in data:
                phk = dict(DEFAULT_CONFIG["profile_hotkeys"])
                phk.update(data["profile_hotkeys"])
                config["profile_hotkeys"] = phk
            return config

        except (json.JSONDecodeError, IOError):
            pass
    return dict(DEFAULT_CONFIG)


def save_preferences(config: dict):
    config["version"] = CURRENT_VERSION
    with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# ================================================================
# Language selection (console, first run only)
# ================================================================

def select_language_gui(config: dict) -> str:
    """GUI-based language selection for first run."""
    if config.get("language") in ("en", "ru"):
        return config["language"]

    # Create a simple dialog
    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

    dialog = QDialog()
    dialog.setWindowTitle("Select Language / Выберите язык")
    dialog.setFixedSize(350, 150)
    dialog.setStyleSheet("""
        QDialog { background: #1a1a2e; }
        QLabel { color: #ddd; font-size: 14px; }
        QPushButton {
            background: #252540; color: #ccc; border: 1px solid #444466;
            border-radius: 4px; padding: 10px 20px; font-size: 13px;
        }
        QPushButton:hover { background: #333355; border-color: #6666aa; }
    """)

    layout = QVBoxLayout(dialog)

    title = QLabel("Select language / Выберите язык:")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)

    btn_row = QHBoxLayout()

    btn_en = QPushButton("English")
    btn_en.setMinimumHeight(40)
    btn_en.clicked.connect(lambda: dialog.done(1))
    btn_row.addWidget(btn_en)

    btn_ru = QPushButton("Русский")
    btn_ru.setMinimumHeight(40)
    btn_ru.clicked.connect(lambda: dialog.done(2))
    btn_row.addWidget(btn_ru)

    layout.addLayout(btn_row)

    result = dialog.exec()

    if result == 1:
        lang = "en"
    elif result == 2:
        lang = "ru"
    else:
        lang = "en"  # Default fallback

    config["language"] = lang
    save_preferences(config)
    return lang


# ================================================================
# Update check
# ================================================================

def parse_version(v: str) -> tuple[int, int, int]:
    v = v.strip().lstrip("v")
    parts = v.split(".")
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except (IndexError, ValueError):
        return (0, 0, 0)


def check_for_updates() -> tuple[str, str]:
    """Check version status from GitHub.

    Returns (status, message) where status is:
        "ok"           — version is supported, continue normally
        "notsup"       — version not supported, block until updated
        "alnotsup"     — version will stop being supported soon, show warning
        "notreleased"  — new version coming, show info banner
        "unknown"      — version not in list at all, treat as ok
    """
    try:
        import urllib.request
        bust_url = f"{UPDATE_URL}?_t={int(time.time() * 1000)}"
        req = urllib.request.Request(bust_url, headers={"Cache-Control": "no-cache", "Pragma": "no-cache"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read().decode("utf-8").strip()

        # Parse multi-line format: v1.0.0:status\nv1.0.1:status\n...
        version_map = {}
        for line in raw.splitlines():
            line = line.strip()
            if ":" in line:
                ver_str, status = line.split(":", 1)
                ver_str = ver_str.strip()
                status = status.strip().lower()
                version_map[ver_str] = status

        current_ver_str = f"v{CURRENT_VERSION}"
        status = version_map.get(current_ver_str)

        if status is None:
            # Version not in list at all
            return "unknown", ""

        if status == "sup":
            return "ok", ""

        elif status == "notsup":
            return "notsup", (
                f"Version v{CURRENT_VERSION} is no longer supported.\n"
                f"Please update to the latest version.\n"
                f"Download: {REPO_URL}"
            )

        elif status == "alnotsup":
            return "alnotsup", (
                f"Version v{CURRENT_VERSION} will stop being supported soon.\n"
                f"Please update when you can.\n"
                f"Download: {REPO_URL}"
            )

        elif status == "notreleased":
            return "notreleased", (
                f"A new version of Deltarune Key Remapper is coming soon.\n"
                f"Current: v{CURRENT_VERSION}"
            )

        else:
            return "ok", ""

    except Exception:
        return "ok", ""


# ================================================================
# Window detection
# ================================================================

def find_deltarune_hwnd() -> int | None:
    if not HAS_WIN32:
        return None
    result = [None]
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            if "deltarune" in win32gui.GetWindowText(hwnd).lower():
                result[0] = hwnd
        return True
    win32gui.EnumWindows(callback, None)
    return result[0]


def is_deltarune_focused() -> bool:
    if not HAS_WIN32:
        return True
    hwnd = find_deltarune_hwnd()
    return hwnd is not None and win32gui.GetForegroundWindow() == hwnd


# ================================================================
# State & hooks
# ================================================================

class RemapState:
    def __init__(self, hotkeys: dict):
        self.enabled = True
        self.running = True
        self.pressed = set()
        self.hotkeys = hotkeys

    def release_all(self):
        for k in list(self.pressed):
            try: keyboard.release(k)
            except: pass
        self.pressed.clear()

    def toggle(self):
        self.enabled = not self.enabled
        state_text = "ON" if self.enabled else "OFF"
        log(f"Remap {state_text}")
        OSDWindow.show(f"Remap: {state_text}")
        if not self.enabled:
            self.release_all()

    def request_quit(self):
        log("Kill switch pressed")
        OSDWindow.show("Kill switch pressed")
        # Small delay so OSD is visible before quit
        QApplication.processEvents()
        time.sleep(0.5)
        self.running = False
        self.release_all()


def make_handler(state, target_key):
    def handler(event):
        try:
            if not state.enabled:
                return True
            if event.event_type == keyboard.KEY_DOWN:
                if target_key not in state.pressed:
                    state.pressed.add(target_key)
                    keyboard.press(target_key)
            elif event.event_type == keyboard.KEY_UP:
                if target_key in state.pressed:
                    state.pressed.discard(target_key)
                    keyboard.release(target_key)
            return False
        except Exception as exc:
            log(f"Error handling {target_key}: {exc}", "error")
            return True
    return handler


def install_hooks(state, targets: dict):
    try:
        for target, source in targets.items():
            if source is not None:
                keyboard.hook_key(source, make_handler(state, target), suppress=True)
        keyboard.add_hotkey(state.hotkeys["toggle"], state.toggle, suppress=True)
        keyboard.add_hotkey(state.hotkeys["quit"], state.request_quit, suppress=True)
        log(f"Hooks installed: {len([v for v in targets.values() if v])} keys")
    except Exception as exc:
        log(f"Failed to install hooks: {exc}", "error")
        sys.exit(1)


def reinstall_hooks(state, targets: dict):
    try: keyboard.unhook_all()
    except: pass
    state.pressed.clear()
    install_hooks(state, targets)


# ================================================================
# Utilities
# ================================================================

def is_admin():
    try: return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except: return False

def set_console_title(title):
    try: ctypes.windll.kernel32.SetConsoleTitleW(title)
    except: pass


# ================================================================
# Shield icon (drawn, not emoji)
# ================================================================

def create_shield_icon(color: QColor = QColor(66, 133, 244)) -> QIcon:
    """Create a small shield icon programmatically."""
    size = 16
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Shield path
    painter.setPen(QPen(color, 1.5))
    painter.setBrush(QBrush(color))

    from PyQt6.QtGui import QPolygonF
    from PyQt6.QtCore import QPointF

    shield = QPolygonF([
        QPointF(8, 1),
        QPointF(14, 3),
        QPointF(14, 8),
        QPointF(8, 14),
        QPointF(2, 8),
        QPointF(2, 3),
    ])
    painter.drawPolygon(shield)
    painter.end()

    return QIcon(pixmap)


# ================================================================
# GUI
# ================================================================

LANG_GUI = {
    "en": {
        "title": f"Deltarune Key Remapper v{CURRENT_VERSION}",
        "profile": "Profile:",
        "create": "Create",
        "delete": "Delete",
        "rename": "Rename",
        "export": "Export",
        "import": "Import",
        "bindings": "Key Bindings",
        "target": "Action",
        "source": "Key",
        "rebind": "Rebind",
        "toggle": "Toggle",
        "save": "Save",
        "quit": "Quit",
        "active": "ACTIVE",
        "paused": "PAUSED",
        "settings": "Settings",
        "logs": "Logs:",
        "enabled": "Enabled",
        "level": "Level:",
        "create_title": "New Profile",
        "create_prompt": "Profile name:",
        "delete_title": "Delete Profile",
        "delete_confirm": "Delete profile '{name}'?",
        "rename_title": "Rename Profile",
        "rename_prompt": "New name:",
        "cannot_delete_default": "Cannot delete Default profile.",
        "cannot_rename_default": "Cannot rename Default profile.",
        "profile_exists": "Profile '{name}' already exists.",
        "profile_created": "Profile '{name}' created.",
        "profile_deleted": "Profile '{name}' deleted.",
        "profile_renamed": "Profile renamed to '{name}'.",
        "profile_imported": "Profile '{name}' imported.",
        "export_saved": "Profile exported to:\n{path}",
        "import_file": "Select profile JSON file",
        "invalid_import": "Invalid profile file.",
        "save_done": "Settings saved.",
        "update_title": "Update Available",
        "update_required": "This update is required to continue.",
        "update_optional": "You can continue, but consider updating.",
        "update_download": "Download: {url}",
        "rebind_prompt": "Press a key for {target}\n(or ESC to keep '{current}')",
        "rebound": "{target} <- {key}",
        "kept": "{target} kept as {key}",
    },
    "ru": {
        "title": f"Ремап клавиш для Deltarune v{CURRENT_VERSION}",
        "profile": "Профиль:",
        "create": "Создать",
        "delete": "Удалить",
        "rename": "Переименовать",
        "export": "Экспорт",
        "import": "Импорт",
        "bindings": "Привязки клавиш",
        "target": "Действие",
        "source": "Клавиша",
        "rebind": "Изменить",
        "toggle": "Переключить",
        "save": "Сохранить",
        "quit": "Выход",
        "active": "АКТИВЕН",
        "paused": "ПАУЗА",
        "settings": "Настройки",
        "logs": "Логи:",
        "enabled": "Включены",
        "level": "Уровень:",
        "create_title": "Новый профиль",
        "create_prompt": "Имя профиля:",
        "delete_title": "Удалить профиль",
        "delete_confirm": "Удалить профиль '{name}'?",
        "rename_title": "Переименовать профиль",
        "rename_prompt": "Новое имя:",
        "cannot_delete_default": "Нельзя удалить профиль Default.",
        "cannot_rename_default": "Нельзя переименовать профиль Default.",
        "profile_exists": "Профиль '{name}' уже существует.",
        "profile_created": "Профиль '{name}' создан.",
        "profile_deleted": "Профиль '{name}' удалён.",
        "profile_renamed": "Профиль переименован в '{name}'.",
        "profile_imported": "Профиль '{name}' импортирован.",
        "export_saved": "Профиль экспортирован в:\n{path}",
        "import_file": "Выберите JSON-файл профиля",
        "invalid_import": "Неверный файл профиля.",
        "save_done": "Настройки сохранены.",
        "update_title": "Доступно обновление",
        "update_required": "Это обновление обязательно для работы.",
        "update_optional": "Можно продолжить, но рекомендуется обновиться.",
        "update_download": "Скачать: {url}",
        "rebind_prompt": "Нажмите клавишу для {target}\n(ESC чтобы оставить '{current}')",
        "rebound": "{target} <- {key}",
        "kept": "{target} осталась {key}",
    },
}


class MainWindow(QMainWindow):
    def __init__(self, config: dict, profiles: dict, lang: str, update_status: str = "ok", update_msg: str = ""):
        super().__init__()
        self.config = config
        self.profiles = profiles
        self.lang = lang
        self.t = LANG_GUI[lang]
        self.state = RemapState(config["hotkeys"])
        self.rebinding = False
        self.update_status = update_status
        self.update_msg = update_msg

        # Set window icon
        icon_path = os.path.join(SCRIPT_DIR, "icons", "deltamap_raw.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setWindowTitle(self.t["title"])
        self.setFixedSize(480, 620 if update_status in ("alnotsup", "notreleased", "notsup") else 560)
        self._apply_style()
        self._build_ui()
        self._refresh_profile_list()
        self._show_update_banner()
        self._load_profile()
        self._install_hooks()
        self._start_timer()

    def _apply_style(self):
        self.setStyleSheet("""
            QMainWindow { background: #1a1a2e; }
            QGroupBox {
                font-size: 12px; font-weight: bold; color: #8888aa;
                border: 1px solid #333355; border-radius: 6px;
                margin-top: 10px; padding-top: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 10px; padding: 0 5px;
            }
            QLabel { color: #ddd; }
            QPushButton {
                background: #252540; color: #ccc; border: 1px solid #444466;
                border-radius: 4px; padding: 6px 12px; font-size: 12px;
            }
            QPushButton:hover { background: #333355; border-color: #6666aa; }
            QPushButton:pressed { background: #444466; }
            QPushButton#danger {
                background: #552222; color: #ff8888; border-color: #884444;
            }
            QPushButton#danger:hover { background: #663333; }
            QPushButton#primary {
                background: #2255aa; color: #aaddff; border: none;
            }
            QPushButton#primary:hover { background: #3366cc; }
            QComboBox {
                background: #252540; color: #ddd; border: 1px solid #444466;
                border-radius: 4px; padding: 4px 8px; font-size: 12px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: #252540; color: #ddd; selection-background-color: #333366;
            }
            QLineEdit {
                background: #252540; color: #ddd; border: 1px solid #444466;
                border-radius: 4px; padding: 4px 8px; font-size: 12px;
            }
            QScrollArea { border: none; background: transparent; }
        """)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 10, 10, 10)

        # Status
        self.status_label = QLabel(self.t["active"])
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4caf50; padding: 4px;")
        layout.addWidget(self.status_label)

        # Profile selector row
        profile_row = QHBoxLayout()
        lbl = QLabel(self.t["profile"])
        lbl.setStyleSheet("font-size: 12px; color: #888;")
        profile_row.addWidget(lbl)

        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(150)
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        profile_row.addWidget(self.profile_combo, 1)

        self.btn_create = QPushButton(self.t["create"])
        self.btn_create.clicked.connect(self._create_profile)
        profile_row.addWidget(self.btn_create)

        self.btn_delete = QPushButton(self.t["delete"])
        self.btn_delete.setObjectName("danger")
        self.btn_delete.clicked.connect(self._delete_profile)
        profile_row.addWidget(self.btn_delete)

        self.btn_rename = QPushButton(self.t["rename"])
        self.btn_rename.clicked.connect(self._rename_profile)
        profile_row.addWidget(self.btn_rename)

        layout.addLayout(profile_row)

        # Import/Export row
        ie_row = QHBoxLayout()
        self.btn_export = QPushButton(self.t["export"])
        self.btn_export.clicked.connect(self._export_profile)
        ie_row.addWidget(self.btn_export)

        self.btn_import = QPushButton(self.t["import"])
        self.btn_import.clicked.connect(self._import_profile)
        ie_row.addWidget(self.btn_import)
        layout.addLayout(ie_row)

        # Bindings group
        bindings_group = QGroupBox(f"  {self.t['bindings']}  ")
        bindings_layout = QVBoxLayout()
        bindings_layout.setSpacing(2)

        # Header
        header = QHBoxLayout()
        h_target = QLabel(f"  {self.t['target']}")
        h_target.setStyleSheet("font-size: 11px; color: #666; font-weight: bold; min-width: 80px;")
        h_source = QLabel(self.t["source"])
        h_source.setStyleSheet("font-size: 11px; color: #666; font-weight: bold; min-width: 80px;")
        header.addWidget(h_target)
        header.addWidget(h_source)
        header.addStretch()
        bindings_layout.addLayout(header)

        self.binding_rows = []
        for target in TARGET_ORDER:
            row = QHBoxLayout()
            row.setSpacing(4)

            lbl_target = QLabel(f"  {target.upper()}")
            lbl_target.setStyleSheet("font-size: 14px; font-weight: bold; color: #64b5f6; min-width: 80px;")
            row.addWidget(lbl_target)

            lbl_source = QLabel("w")
            lbl_source.setStyleSheet("font-size: 14px; font-weight: bold; color: #81c784; min-width: 80px;")
            row.addWidget(lbl_source)

            row.addStretch()

            btn = QPushButton(self.t["rebind"])
            btn.setFixedWidth(70)
            btn.setStyleSheet("""
                QPushButton { background: #1a3a5a; color: #88ccff; border: none; border-radius: 3px; font-size: 11px; padding: 3px; }
                QPushButton:hover { background: #2a5a8a; }
            """)
            btn.clicked.connect(lambda _, t=target, l=lbl_source: self._start_rebind(t, l))
            row.addWidget(btn)

            bindings_layout.addLayout(row)
            self.binding_rows.append((target, lbl_source, btn))

        bindings_group.setLayout(bindings_layout)

        scroll = QScrollArea()
        scroll.setWidget(bindings_group)
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(280)
        layout.addWidget(scroll)

        # Settings group
        settings_group = QGroupBox(f"  {self.t['settings']}  ")
        settings_layout = QHBoxLayout()

        logs_lbl = QLabel(self.t["logs"])
        logs_lbl.setStyleSheet("font-size: 11px; color: #888;")
        settings_layout.addWidget(logs_lbl)

        self.logs_check = QPushButton(self.t["enabled"] if self.config.get("logs_enabled", True) else "OFF")
        self.logs_check.setCheckable(True)
        self.logs_check.setChecked(self.config.get("logs_enabled", True))
        self.logs_check.clicked.connect(self._toggle_logs)
        settings_layout.addWidget(self.logs_check)

        level_lbl = QLabel(self.t["level"])
        level_lbl.setStyleSheet("font-size: 11px; color: #888;")
        settings_layout.addWidget(level_lbl)

        self.level_combo = QComboBox()
        self.level_combo.addItems(["debug", "info", "warn", "error"])
        self.level_combo.setCurrentText(self.config.get("log_level", "info"))
        self.level_combo.currentTextChanged.connect(self._change_log_level)
        self.level_combo.setFixedWidth(70)
        settings_layout.addWidget(self.level_combo)

        settings_layout.addStretch()
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Bottom buttons
        btn_row = QHBoxLayout()

        self.toggle_btn = QPushButton(f"{self.t['toggle']} ({self.config['hotkeys']['toggle'].upper()})")
        self.toggle_btn.setMinimumHeight(36)
        self.toggle_btn.setObjectName("primary")
        self.toggle_btn.clicked.connect(self.state.toggle)
        btn_row.addWidget(self.toggle_btn)

        self.save_btn = QPushButton(self.t["save"])
        self.save_btn.setMinimumHeight(36)
        self.save_btn.clicked.connect(self._save)
        btn_row.addWidget(self.save_btn)

        self.quit_btn = QPushButton(f"{self.t['quit']} ({self.config['hotkeys']['quit'].upper()})")
        self.quit_btn.setMinimumHeight(36)
        self.quit_btn.setObjectName("danger")
        self.quit_btn.clicked.connect(self.state.request_quit)
        btn_row.addWidget(self.quit_btn)

        layout.addLayout(btn_row)

        # Credits
        credits = QLabel('Developed by <a href="https://github.com/FoxVukOff" style="color:#666;">FoxVuk</a>')
        credits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits.setOpenExternalLinks(True)
        credits.setStyleSheet("font-size: 10px; color: #666; padding: 4px;")
        layout.addWidget(credits)

    def _show_update_banner(self):
        """Show update banner based on status."""
        if self.update_status == "ok" or not self.update_msg:
            return

        banner = QFrame()
        banner.setFixedHeight(60)

        if self.update_status == "notsup":
            # Red banner, non-dismissable (blocks use)
            banner.setStyleSheet("""
                QFrame { background: #552222; border: 1px solid #aa4444; border-radius: 6px; }
                QLabel { color: #ff8888; }
            """)
            layout = QVBoxLayout(banner)
            layout.setContentsMargins(10, 6, 10, 6)
            lbl = QLabel(self.update_msg.replace("\n", " | "))
            lbl.setStyleSheet("font-size: 11px; color: #ff8888; font-weight: bold;")
            lbl.setWordWrap(True)
            layout.addWidget(lbl)

        elif self.update_status == "alnotsup":
            # Orange banner, non-dismissable (warning)
            banner.setStyleSheet("""
                QFrame { background: #554422; border: 1px solid #aa8844; border-radius: 6px; }
                QLabel { color: #ffcc66; }
            """)
            layout = QVBoxLayout(banner)
            layout.setContentsMargins(10, 6, 10, 6)
            lbl = QLabel(self.update_msg.replace("\n", " | "))
            lbl.setStyleSheet("font-size: 11px; color: #ffcc66; font-weight: bold;")
            lbl.setWordWrap(True)
            layout.addWidget(lbl)

        elif self.update_status == "notreleased":
            # Blue banner, dismissable
            banner.setStyleSheet("""
                QFrame { background: #223355; border: 1px solid #4466aa; border-radius: 6px; }
                QLabel { color: #88bbff; }
            """)
            h_layout = QHBoxLayout(banner)
            h_layout.setContentsMargins(10, 6, 10, 6)

            lbl = QLabel(self.update_msg.replace("\n", " | "))
            lbl.setStyleSheet("font-size: 11px; color: #88bbff;")
            lbl.setWordWrap(True)
            h_layout.addWidget(lbl, 1)

            close_btn = QPushButton("x")
            close_btn.setFixedSize(20, 20)
            close_btn.setStyleSheet("""
                QPushButton { background: transparent; color: #88bbff; border: none; font-size: 14px; font-weight: bold; }
                QPushButton:hover { color: #ffffff; }
            """)
            close_btn.clicked.connect(banner.deleteLater)
            h_layout.addWidget(close_btn)

        # Insert banner at the top of the main layout
        main_widget = self.centralWidget()
        main_layout = main_widget.layout()
        main_layout.insertWidget(0, banner)

    def _refresh_profile_list(self):
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        for name in sorted(self.profiles["profiles"].keys()):
            self.profile_combo.addItem(name)
        idx = self.profile_combo.findText(self.profiles["active"])
        if idx >= 0:
            self.profile_combo.setCurrentIndex(idx)
        self.profile_combo.blockSignals(False)

    def _on_profile_changed(self, name):
        if name and name in self.profiles["profiles"]:
            self.profiles["active"] = name
            self.config["active_profile"] = name
            self._load_profile()
            self._reinstall_hooks()
            # Save active profile immediately
            save_preferences(self.config)
            save_profiles(self.profiles)
            log(f"Switched to profile: {name}")

    def _load_profile(self):
        name = self.profiles["active"]
        targets = self.profiles["profiles"][name]["targets"]

        for target, lbl_source, btn in self.binding_rows:
            src = targets.get(target)
            if src is None:
                lbl_source.setText("(disabled)")
                lbl_source.setStyleSheet("font-size: 13px; font-weight: bold; color: #888; min-width: 80px;")
            else:
                lbl_source.setText(src)
                if name == "Default":
                    lbl_source.setStyleSheet("font-size: 14px; font-weight: bold; color: #4285f4; min-width: 80px;")
                else:
                    lbl_source.setStyleSheet("font-size: 14px; font-weight: bold; color: #81c784; min-width: 80px;")

            if name == "Default":
                btn.setEnabled(False)
            else:
                btn.setEnabled(True)

        # Update profile name styling
        self.profile_combo.blockSignals(True)
        idx = self.profile_combo.findText(name)
        if idx >= 0:
            self.profile_combo.setCurrentIndex(idx)
        self.profile_combo.blockSignals(False)

    def _install_hooks(self):
        targets = self.profiles["profiles"][self.profiles["active"]]["targets"]
        install_hooks(self.state, targets)
        self._install_profile_hotkeys()

    def _reinstall_hooks(self):
        targets = self.profiles["profiles"][self.profiles["active"]]["targets"]
        reinstall_hooks(self.state, targets)
        self._install_profile_hotkeys()

    def _install_profile_hotkeys(self):
        """Register Ctrl+Alt+P+0-9 hotkeys for profile switching."""
        profile_hotkeys = self.config.get("profile_hotkeys", {})
        for digit, hotkey in profile_hotkeys.items():
            try:
                def make_handler(d=digit):
                    def handler():
                        self._switch_profile_by_hotkey(d)
                    return handler
                keyboard.add_hotkey(hotkey, make_handler(digit), suppress=True)
            except Exception as e:
                log(f"Failed to register hotkey {hotkey}: {e}", "warn")

    def _switch_profile_by_hotkey(self, digit: str):
        """Switch profile by hotkey digit. Shows OSD."""
        # Find profile with this hotkey digit
        target_name = None
        if digit == "0":
            target_name = "Default"
        else:
            for name, pdata in self.profiles["profiles"].items():
                if pdata.get("hotkey_digit") == digit:
                    target_name = name
                    break

        if target_name and target_name in self.profiles["profiles"]:
            self.profiles["active"] = target_name
            self.config["active_profile"] = target_name
            self._load_profile()
            self._reinstall_hooks()
            save_preferences(self.config)
            save_profiles(self.profiles)
            OSDWindow.show(f"Profile: {target_name}")
            log(f"Switched to profile: {target_name} (hotkey Ctrl+Alt+P+{digit})")

    def _start_rebind(self, target: str, lbl: QLabel):
        if self.rebinding:
            return
        self.rebinding = True

        name = self.profiles["active"]
        current = self.profiles["profiles"][name]["targets"].get(target)

        lbl.setText("...")
        lbl.repaint()

        # Temporarily unhook to catch keypress
        try: keyboard.unhook_all()
        except: pass

        event = keyboard.read_event(suppress=True)

        # Reinstall hooks
        self._install_hooks()

        if event.event_type == keyboard.KEY_DOWN and event.name != "esc":
            key = event.name
            if key in VALID_KEYS:
                self.profiles["profiles"][name]["targets"][target] = key
                lbl.setText(key)
                lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #81c784; min-width: 80px;")
                log(f"{target} <- {key}")
            else:
                if current is None:
                    lbl.setText("(disabled)")
                    lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #888; min-width: 80px;")
                else:
                    lbl.setText(current)
                log(f"Invalid key: {key}", "warn")
        else:
            # ESC pressed — disable this key
            self.profiles["profiles"][name]["targets"][target] = None
            lbl.setText("(disabled)")
            lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #888; min-width: 80px;")
            log(f"{target} disabled")

        self.rebinding = False

    def _create_profile(self):
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, self.t["create_title"], self.t["create_prompt"])
        if ok and name:
            created, msg = create_profile(self.profiles, name)
            if created:
                self._refresh_profile_list()
                self.profile_combo.setCurrentText(name)
                full_msg = self.t["profile_created"].format(name=name)
                if msg:
                    full_msg += f"\n\n{msg}"
                QMessageBox.information(self, self.t["create_title"], full_msg)
            elif msg == "exists":
                QMessageBox.warning(self, self.t["create_title"], self.t["profile_exists"].format(name=name))

    def _delete_profile(self):
        name = self.profiles["active"]
        if name == "Default":
            QMessageBox.warning(self, self.t["delete_title"], self.t["cannot_delete_default"])
            return
        reply = QMessageBox.question(self, self.t["delete_title"], self.t["delete_confirm"].format(name=name))
        if reply == QMessageBox.StandardButton.Yes:
            delete_profile(self.profiles, name)
            self._refresh_profile_list()
            self._load_profile()

    def _rename_profile(self):
        from PyQt6.QtWidgets import QInputDialog
        old_name = self.profiles["active"]
        if old_name == "Default":
            QMessageBox.warning(self, self.t["rename_title"], self.t["cannot_rename_default"])
            return
        new_name, ok = QInputDialog.getText(self, self.t["rename_title"], self.t["rename_prompt"], text=old_name)
        if ok and new_name:
            if rename_profile(self.profiles, old_name, new_name):
                self._refresh_profile_list()
                self.profile_combo.setCurrentText(new_name)
            else:
                QMessageBox.warning(self, self.t["rename_title"], self.t["profile_exists"].format(name=new_name))

    def _export_profile(self):
        name = self.profiles["active"]
        filepath, _ = QFileDialog.getSaveFileName(self, self.t["export"], f"{name}.json", "JSON (*.json)")
        if filepath:
            if export_profile(self.profiles, name, filepath):
                QMessageBox.information(self, self.t["export"], self.t["export_saved"].format(path=filepath))

    def _import_profile(self):
        filepath, _ = QFileDialog.getOpenFileName(self, self.t["import"], "", "JSON (*.json)")
        if filepath:
            name = import_profile(self.profiles, filepath)
            if name:
                self._refresh_profile_list()
                self.profile_combo.setCurrentText(name)
                QMessageBox.information(self, self.t["import"], self.t["profile_imported"].format(name=name))
            else:
                QMessageBox.warning(self, self.t["import"], self.t["invalid_import"])

    def _toggle_logs(self):
        enabled = self.logs_check.isChecked()
        self.config["logs_enabled"] = enabled
        set_logging(enabled, self.config.get("log_level", "info"))
        self.logs_check.setText(self.t["enabled"] if enabled else "OFF")

    def _change_log_level(self, level):
        self.config["log_level"] = level
        set_logging(self.config.get("logs_enabled", True), level)

    def _save(self):
        self.config["active_profile"] = self.profiles["active"]
        save_preferences(self.config)
        save_profiles(self.profiles)
        log(self.t["save_done"])

    def _start_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.start(100)

    def _update(self):
        if self.state.enabled:
            self.status_label.setText(self.t["active"])
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4caf50; padding: 4px;")
        else:
            self.status_label.setText(self.t["paused"])
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f44336; padding: 4px;")
        if not self.state.running:
            QApplication.quit()

    def closeEvent(self, event):
        self.state.release_all()
        try: keyboard.unhook_all()
        except: pass
        event.accept()


# ================================================================
# Main
# ================================================================

def main():
    # Check for PyQt6
    if not HAS_PYQT:
        print(f"PyQt6 is required for v{CURRENT_VERSION}.")
        print("Install with: pip install PyQt6")
        sys.exit(1)

    set_console_title("Deltarune Remap")

    # Load config
    config = load_preferences()

    # Start app early for GUI language selection
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark palette
    p = QPalette()
    p.setColor(QPalette.ColorRole.Window, QColor(26, 26, 46))
    p.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
    p.setColor(QPalette.ColorRole.Base, QColor(37, 37, 64))
    p.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
    p.setColor(QPalette.ColorRole.Button, QColor(37, 37, 64))
    p.setColor(QPalette.ColorRole.ButtonText, QColor(200, 200, 200))
    p.setColor(QPalette.ColorRole.Highlight, QColor(34, 85, 170))
    app.setPalette(p)

    # Language selection (GUI, first run)
    lang = select_language_gui(config)

    # Set logging
    set_logging(config.get("logs_enabled", True), config.get("log_level", "info"))
    log(f"Deltarune Key Remapper v{CURRENT_VERSION}")

    # Check for updates
    update_status, update_msg = check_for_updates()
    if update_msg:
        log(update_msg, "warn" if update_status in ("notsup", "alnotsup") else "info")

    # Migrate to profiles format
    profiles = migrate_to_profiles(config)

    # Block if version not supported
    if update_status == "notsup":
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Version Not Supported")
        msg_box.setText(update_msg)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        sys.exit(0)

    window = MainWindow(config, profiles, lang, update_status, update_msg)
    window.show()

    app.exec()

    # Cleanup
    try: keyboard.unhook_all()
    except: pass
    sys.exit(0)


if __name__ == "__main__":
    main()
