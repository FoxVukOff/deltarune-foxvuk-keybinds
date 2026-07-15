# -*- coding: utf-8 -*-
"""
================================================================
 Deltarune Key Remapper v1.0.3
================================================================

Target keys (what the game receives):
    Up / Left / Down / Right  —  movement
    Z                         —  confirm / interact
    X                         —  cancel / run
    C                         —  phone / call menu

Source keys (what you press) — fully customizable:
    Default: W A S D Q E R

Hotkeys:
    Ctrl+Alt+V          — toggle remap on/off
    Ctrl+Alt+Backspace  — quit the program

----------------------------------------------------------------
SAFETY: hooks ONLY the keys in your config. Nothing else.
----------------------------------------------------------------
First run: language (EN/RU), mode (GUI/NonGUI), key binding setup.
All settings saved to preferences.json.
================================================================
"""

import ctypes
import json
import os
import sys
import time

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


# ================================================================
# Paths
# ================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PREFERENCES_FILE = os.path.join(SCRIPT_DIR, "preferences.json")


# ================================================================
# Migration: v1.0.0-v1.0.2 -> v1.0.3
# ================================================================

def migrate_preferences(data: dict) -> dict:
    """Migrate old preferences to v1.0.3 format.
    v1.0.3 uses source->target mapping where targets are fixed
    (up/down/left/right/z/x/c) and sources are customizable."""
    old_remap = data.get("remap", {})

    # Build new format: target -> source
    new_targets = {
        "up": "w",
        "down": "s",
        "left": "a",
        "right": "d",
        "z": "q",
        "x": "e",
        "c": "r",
    }

    # Try to preserve old mappings
    # old format was: source -> target (e.g. "w": "up")
    for source, target in old_remap.items():
        if target in new_targets and source not in new_targets.values():
            new_targets[target] = source

    data["targets"] = new_targets
    data.pop("remap", None)
    data.pop("layout_preset", None)
    data["version"] = "1.0.3"
    return data


# ================================================================
# Localizations
# ================================================================

LANG = {
    "en": {
        "banner_title": "Deltarune Key Remapper v1.0.3",
        "banner_target": "Target (game receives):",
        "banner_toggle": "{hotkey}  —  toggle remap on/off",
        "banner_quit": "{hotkey}  —  quit the program",
        "banner_console_quit": "Ctrl+C in this window — fallback quit",
        "banner_safety": "If something goes wrong — Ctrl+Alt+Backspace kills the process.",
        "banner_rebind": "Press the number key (1-7) to rebind that action.",
        "banner_custom": "Fully customizable: change any source key to your preference.",
        "admin_warning": "WARNING: NOT running as Administrator. Keyboard hook may not work.",
        "ready": "Ready. Remap active, switch to the game.",
        "remap_on": "Remap: ON",
        "remap_off": "Remap: OFF",
        "quit_msg": "Ctrl+Alt+Backspace — exiting...",
        "ctrl_c_msg": "Ctrl+C received, shutting down...",
        "hook_error": "Failed to install keyboard hook: {err}",
        "hook_hint": "Make sure the script is running as Administrator.",
        "key_error": "Error handling '{key}': {err}",
        "migrated": "Settings migrated to v1.0.3 format.",
        "rebind_prompt": "Press a key to bind to {target} (or ESC to keep '{current}'): ",
        "rebound": "{target} <- {key}",
        "kept": "{target} kept as {key}",
        "window_not_found": "WARNING: Deltarune window not found!",
        "window_not_focused": "WARNING: Deltarune is not the active window.",
        "lang_prompt": "Select language / Выберите язык:",
        "lang_saved": "Language saved.",
        "mode_prompt": "Select interface mode:",
        "mode_nogui": "1) NonGUI (console)",
        "mode_gui": "2) GUI (PyQt6 window)",
        "mode_saved": "Mode saved.",
        "mode_gui_missing": "PyQt6 not installed. Install with: pip install PyQt6",
        "config_saved": "Configuration saved.",
        "bindings_title": "Current bindings:",
        "press_num": "Press 1-7 to rebind, S to save & start, Q to quit:",
    },
    "ru": {
        "banner_title": "Ремап клавиш для Deltarune v1.0.3",
        "banner_target": "Цель (игра получает):",
        "banner_toggle": "{hotkey}  —  включить/выключить ремап",
        "banner_quit": "{hotkey}  —  выйти из программы",
        "banner_console_quit": "Ctrl+C в этом окне — запасной способ выйти",
        "banner_safety": "Если что-то не так — Ctrl+Alt+Backspace убивает процесс.",
        "banner_rebind": "Нажмите цифру (1-7) чтобы переназначить клавишу.",
        "banner_custom": "Полная кастомизация: меняйте любую клавишу под себя.",
        "admin_warning": "ВНИМАНИЕ: не от администратора. Хук может не работать.",
        "ready": "Готово. Ремап активен, можно переключаться в игру.",
        "remap_on": "[Ремап] ВКЛЮЧЁН",
        "remap_off": "[Ремап] ВЫКЛЮЧЕН",
        "quit_msg": "Ctrl+Alt+Backspace — выхожу...",
        "ctrl_c_msg": "\nПолучен Ctrl+C, завершаюсь...",
        "hook_error": "Не удалось установить хук: {err}",
        "hook_hint": "Запустите от имени администратора.",
        "key_error": "Ошибка '{key}': {err}",
        "migrated": "Настройки мигрированы на v1.0.3.",
        "rebind_prompt": "Нажмите клавишу для {target} (ESC чтобы оставить '{current}'): ",
        "rebound": "{target} <- {key}",
        "kept": "{target} осталась {key}",
        "window_not_found": "ВНИМАНИЕ: Окно Deltarune не найдено!",
        "window_not_focused": "ВНИМАНИЕ: Deltarune не активно.",
        "lang_prompt": "Select language / Выберите язык:",
        "lang_saved": "Язык сохранён.",
        "mode_prompt": "Выберите режим:",
        "mode_nogui": "1) NonGUI (консоль)",
        "mode_gui": "2) GUI (окно PyQt6)",
        "mode_saved": "Режим сохранён.",
        "mode_gui_missing": "PyQt6 не установлен. Установите: pip install PyQt6",
        "config_saved": "Настройки сохранены.",
        "bindings_title": "Текущие привязки:",
        "press_num": "Нажмите 1-7 для переназначения, S — сохранить и старт, Q — выход:",
    },
}


# ================================================================
# Default targets -> source keys
# ================================================================

DEFAULT_TARGETS = {
    "up": "w",
    "down": "s",
    "left": "a",
    "right": "d",
    "z": "q",
    "x": "e",
    "c": "r",
}

TARGET_ORDER = ["up", "down", "left", "right", "z", "x", "c"]

DEFAULT_CONFIG = {
    "language": None,
    "mode": None,
    "targets": dict(DEFAULT_TARGETS),
    "hotkeys": {
        "toggle": "ctrl+alt+v",
        "quit": "ctrl+alt+backspace",
    },
    "window_check": True,
    "version": "1.0.3",
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


# ================================================================
# Preferences
# ================================================================

def load_preferences() -> tuple[dict, bool]:
    was_migrated = False
    if os.path.exists(PREFERENCES_FILE):
        try:
            with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            old_ver = data.get("version", "1.0.0")
            if old_ver in ("1.0.0", "1.0.1", "1.0.2", None):
                data = migrate_preferences(data)
                was_migrated = True
            config = dict(DEFAULT_CONFIG)
            config.update(data)
            if "targets" in data:
                targets = dict(DEFAULT_TARGETS)
                targets.update(data["targets"])
                config["targets"] = targets
            if "hotkeys" in data:
                hotkeys = dict(DEFAULT_CONFIG["hotkeys"])
                hotkeys.update(data["hotkeys"])
                config["hotkeys"] = hotkeys
            return config, was_migrated
        except (json.JSONDecodeError, IOError):
            pass
    return dict(DEFAULT_CONFIG), was_migrated


def save_preferences(config: dict):
    config["version"] = "1.0.3"
    with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# ================================================================
# Language selection
# ================================================================

def select_language(config: dict) -> str:
    if config.get("language") in ("en", "ru"):
        return config["language"]
    print("=" * 55)
    print("  Select language / Выберите язык:")
    print("=" * 55)
    print("  1) English")
    print("  2) Русский")
    print("=" * 55)
    while True:
        choice = input("  Your choice (1 or 2): ").strip()
        if choice == "1":
            lang = "en"; break
        elif choice == "2":
            lang = "ru"; break
    config["language"] = lang
    save_preferences(config)
    print(f"  {LANG[lang]['lang_saved']}\n")
    return lang


# ================================================================
# Mode selection
# ================================================================

def select_mode(config: dict, lang: str) -> str:
    if config.get("mode") in ("gui", "nogui"):
        return config["mode"]
    t = LANG[lang]
    print("=" * 55)
    print(f"  {t['mode_prompt']}")
    print("=" * 55)
    print(f"  {t['mode_nogui']}")
    print(f"  {t['mode_gui']}")
    print("=" * 55)
    while True:
        choice = input("  > ").strip()
        if choice == "1":
            mode = "nogui"; break
        elif choice == "2":
            try:
                import PyQt6  # noqa: F401
                mode = "gui"; break
            except ImportError:
                print(f"  {t['mode_gui_missing']}")
    config["mode"] = mode
    save_preferences(config)
    print(f"  {t['mode_saved']}\n")
    return mode


# ================================================================
# NonGUI rebinding
# ================================================================

def listen_for_key() -> str | None:
    """Block until a key is pressed, return its name. ESC returns None."""
    event = keyboard.read_event(suppress=True)
    if event.event_type == keyboard.KEY_DOWN:
        if event.name == "esc":
            return None
        return event.name
    return None


def rebind_interactive(config: dict, lang: str) -> dict:
    """NonGUI interactive key rebinding."""
    t = LANG[lang]
    targets = config["targets"]

    while True:
        print()
        print(f"  {t['bindings_title']}")
        print("  " + "-" * 40)
        for i, target in enumerate(TARGET_ORDER, 1):
            src = targets.get(target, "?")
            print(f"    {i}) {target.upper():>6}  <-  {src}")
        print("  " + "-" * 40)
        print(f"  {t['press_num']}")

        choice = input("  > ").strip().lower()

        if choice == "s":
            save_preferences(config)
            print(f"  {t['config_saved']}")
            return config
        elif choice == "q":
            sys.exit(0)
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(TARGET_ORDER):
                target = TARGET_ORDER[idx]
                current = targets.get(target, "?")
                print(f"  {t['rebind_prompt'].format(target=target.upper(), current=current)}", end="", flush=True)
                key = listen_for_key()
                if key is None:
                    print(f"  {t['kept'].format(target=target.upper(), key=current)}")
                elif key in VALID_KEYS:
                    targets[target] = key
                    print(f"  {t['rebound'].format(target=target.upper(), key=key)}")
                else:
                    print(f"  Invalid key: {key}")
            else:
                print("  Invalid number")


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
    def __init__(self, config, lang):
        self.enabled = True
        self.running = True
        self.pressed = set()
        self.t = LANG[lang]

    def release_all(self):
        for k in list(self.pressed):
            try: keyboard.release(k)
            except: pass
        self.pressed.clear()

    def toggle(self):
        self.enabled = not self.enabled
        print(self.t["remap_on"] if self.enabled else self.t["remap_off"])
        if not self.enabled:
            self.release_all()

    def request_quit(self):
        print(self.t["quit_msg"])
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
            print(state.t["key_error"].format(key=target_key, err=repr(exc)))
            return True
    return handler


def install_hooks(state, config):
    targets = config["targets"]
    try:
        for target, source in targets.items():
            if source is not None:
                keyboard.hook_key(source, make_handler(state, target), suppress=True)
        keyboard.add_hotkey(config["hotkeys"]["toggle"], state.toggle, suppress=True)
        keyboard.add_hotkey(config["hotkeys"]["quit"], state.request_quit, suppress=True)
    except Exception as exc:
        print(state.t["hook_error"].format(err=repr(exc)))
        print(state.t["hook_hint"])
        sys.exit(1)


def reinstall_hooks(state, config):
    try: keyboard.unhook_all()
    except: pass
    state.pressed.clear()
    install_hooks(state, config)


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
# GUI (PyQt6)
# ================================================================

def run_gui(config, lang):
    try:
        from PyQt6.QtWidgets import (
            QApplication, QMainWindow, QLabel, QVBoxLayout,
            QHBoxLayout, QWidget, QPushButton, QFrame
        )
        from PyQt6.QtCore import Qt, QTimer
        from PyQt6.QtGui import QPalette, QColor
    except ImportError:
        print(LANG[lang]["mode_gui_missing"])
        sys.exit(1)

    state = RemapState(config, lang)
    install_hooks(state, config)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark palette
    p = QPalette()
    p.setColor(QPalette.ColorRole.Window, QColor(25, 25, 25))
    p.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
    p.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    p.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
    p.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
    p.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
    p.setColor(QPalette.ColorRole.Highlight, QColor(70, 110, 170))
    app.setPalette(p)

    win = QMainWindow()
    win.setWindowTitle("Deltarune Key Remapper v1.0.3")
    win.setFixedSize(440, 480)
    win.setStyleSheet("""
        QMainWindow { background: #191919; }
        QFrame#card {
            background: #252525;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 8px;
        }
        QLabel { color: #ddd; }
        QPushButton {
            background: #333; color: #ddd;
            border: 1px solid #555; border-radius: 5px;
            padding: 8px; font-size: 13px;
        }
        QPushButton:hover { background: #444; }
    """)

    central = QWidget()
    win.setCentralWidget(central)
    layout = QVBoxLayout(central)
    layout.setSpacing(6)

    # Status
    status = QLabel("ACTIVE")
    status.setAlignment(Qt.AlignmentFlag.AlignCenter)
    status.setStyleSheet("font-size: 18px; font-weight: bold; color: #4caf50; padding: 4px;")
    layout.addWidget(status)

    # Binding rows
    targets = config["targets"]
    rows = []

    for target in TARGET_ORDER:
        card = QFrame()
        card.setObjectName("card")
        card.setFixedHeight(42)
        row = QHBoxLayout(card)
        row.setContentsMargins(12, 4, 12, 4)

        lbl_target = QLabel(target.upper())
        lbl_target.setStyleSheet("font-size: 16px; font-weight: bold; color: #64b5f6; min-width: 50px;")
        row.addWidget(lbl_target)

        arrow = QLabel("  <-  ")
        arrow.setStyleSheet("font-size: 13px; color: #666;")
        row.addWidget(arrow)

        lbl_source = QLabel(targets.get(target, "?"))
        lbl_source.setStyleSheet("font-size: 16px; font-weight: bold; color: #81c784; min-width: 50px;")
        row.addWidget(lbl_source)

        row.addStretch()

        btn_rebind = QPushButton("Rebind")
        btn_rebind.setFixedWidth(70)
        btn_rebind.setStyleSheet("""
            QPushButton { background: #1a5276; color: #aed6f1; border: none; border-radius: 4px; font-size: 11px; padding: 4px; }
            QPushButton:hover { background: #2471a3; }
        """)

        def make_rebind(tgt, lbl, btn):
            def on_click():
                btn.setText("...")
                btn.repaint()
                # Listen for key
                event = keyboard.read_event(suppress=True)
                if event.event_type == keyboard.KEY_DOWN and event.name != "esc":
                    targets[tgt] = event.name
                    lbl.setText(event.name)
                    config["targets"] = targets
                    reinstall_hooks(state, config)
                btn.setText("Rebind")
            return on_click

        btn_rebind.clicked.connect(make_rebind(target, lbl_source, btn_rebind))
        row.addWidget(btn_rebind)

        layout.addWidget(card)
        rows.append((lbl_source, btn_rebind))

    # Buttons
    btn_row = QHBoxLayout()

    toggle_btn = QPushButton(f"Toggle ({config['hotkeys']['toggle'].upper()})")
    toggle_btn.setMinimumHeight(36)
    toggle_btn.setStyleSheet("""
        QPushButton { background: #2e7d32; color: white; border: none; border-radius: 5px; font-size: 12px; }
        QPushButton:hover { background: #388e3c; }
    """)
    toggle_btn.clicked.connect(state.toggle)
    btn_row.addWidget(toggle_btn)

    save_btn = QPushButton("Save")
    save_btn.setMinimumHeight(36)
    save_btn.setStyleSheet("""
        QPushButton { background: #1565c0; color: white; border: none; border-radius: 5px; font-size: 12px; }
        QPushButton:hover { background: #1976d2; }
    """)
    def on_save():
        config["targets"] = targets
        save_preferences(config)
    save_btn.clicked.connect(on_save)
    btn_row.addWidget(save_btn)

    quit_btn = QPushButton(f"Quit ({config['hotkeys']['quit'].upper()})")
    quit_btn.setMinimumHeight(36)
    quit_btn.setStyleSheet("""
        QPushButton { background: #c62828; color: white; border: none; border-radius: 5px; font-size: 12px; }
        QPushButton:hover { background: #d32f2f; }
    """)
    quit_btn.clicked.connect(state.request_quit)
    btn_row.addWidget(quit_btn)

    layout.addLayout(btn_row)

    # Timer
    def update():
        if state.enabled:
            status.setText("ACTIVE")
            status.setStyleSheet("font-size: 18px; font-weight: bold; color: #4caf50; padding: 4px;")
        else:
            status.setText("PAUSED")
            status.setStyleSheet("font-size: 18px; font-weight: bold; color: #f44336; padding: 4px;")
        if not state.running:
            app.quit()

    timer = QTimer()
    timer.timeout.connect(update)
    timer.start(100)

    win.show()
    app.exec()
    state.release_all()
    try: keyboard.unhook_all()
    except: pass


# ================================================================
# Banner
# ================================================================

def print_banner(config, lang):
    t = LANG[lang]
    targets = config["targets"]
    toggle = config["hotkeys"]["toggle"]
    quit_hk = config["hotkeys"]["quit"]

    print("=" * 55)
    print(f"  {t['banner_title']}")
    print("=" * 55)
    print(f"  {t['banner_target']}")
    for i, target in enumerate(TARGET_ORDER, 1):
        src = targets.get(target, "?")
        print(f"    {i}) {target.upper():>6}  <-  {src}")
    print("-" * 55)
    print(f"  {t['banner_toggle'].format(hotkey=toggle.upper())}")
    print(f"  {t['banner_quit'].format(hotkey=quit_hk.upper())}")
    print(f"  {t['banner_console_quit']}")
    print("-" * 55)
    print(f"  {t['banner_rebind']}")
    print(f"  {t['banner_custom']}")
    print("-" * 55)
    print(f"  {t['banner_safety']}")
    print("=" * 55)
    if not is_admin():
        print(f"\n  {t['admin_warning']}")
    print()


# ================================================================
# Main
# ================================================================

def main():
    config, was_migrated = load_preferences()
    first_run = not os.path.exists(PREFERENCES_FILE)

    lang = select_language(config)
    t = LANG[lang]

    if was_migrated:
        print(f"  {t['migrated']}\n")

    if first_run:
        mode = select_mode(config, lang)
    else:
        mode = config.get("mode", "nogui")

    set_console_title("Deltarune Remap")

    # GUI mode
    if mode == "gui":
        if first_run:
            print(f"  Set up your key bindings:\n")
            rebind_interactive(config, lang)
        run_gui(config, lang)
        return

    # NonGUI mode
    print_banner(config, lang)

    if first_run:
        print(f"  Set up your key bindings:\n")
        rebind_interactive(config, lang)
        print_banner(config, lang)

    if config.get("window_check", True) and HAS_WIN32:
        print("  Window detection: ON\n")

    state = RemapState(config, lang)
    install_hooks(state, config)

    print(f"  {t['ready']}\n")

    window_warn_shown = False
    try:
        while state.running:
            time.sleep(0.1)
            if config.get("window_check", True) and HAS_WIN32:
                hwnd = find_deltarune_hwnd()
                if hwnd is None:
                    if not window_warn_shown:
                        print(f"  {t['window_not_found']}")
                        window_warn_shown = True
                else:
                    if not is_deltarune_focused():
                        if not window_warn_shown:
                            print(f"  {t['window_not_focused']}")
                            window_warn_shown = True
                    else:
                        window_warn_shown = False
    except KeyboardInterrupt:
        print(t["ctrl_c_msg"])
    finally:
        state.release_all()
        try: keyboard.unhook_all()
        except: pass
        sys.exit(0)


if __name__ == "__main__":
    main()
