# -*- coding: utf-8 -*-
"""
================================================================
 Deltarune Key Remapper
================================================================

WASD  ->  arrows (Up / Left / Down / Right)
Q     ->  Z
E     ->  X
R     ->  C (phone/call menu)

Fully supports diagonals and any simultaneous key presses —
as if you were physically pressing the arrows: you don't need to
release one key for another to work.

Hotkeys:
    Ctrl+Alt+V          — toggle remap on/off
    Ctrl+Alt+Backspace  — quit the program
    Ctrl+C in console   — fallback quit

Layout switching:
    N                   — cycle through preset layouts

----------------------------------------------------------------
SAFETY: why this won't lock your keyboard
----------------------------------------------------------------
The script hooks EXACTLY the keys listed in your config — each
via its own keyboard.hook_key(). NOTHING else is hooked. Alt+Tab,
Win, Esc, F-keys, Ctrl+Shift+Esc etc. cannot be blocked by this
script.

----------------------------------------------------------------
First run: language selection (EN / RU), mode (GUI / NonGUI)
All settings are saved to preferences.json.
================================================================

Installation (once):
    pip install keyboard
    pip install PyQt6        (only if using GUI mode)

Launch (MUST be run as Administrator):
    python deltarune_remap.py
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
# Migration: v1.0.0/v1.0.1 -> v1.0.2
# ================================================================

def migrate_preferences(data: dict) -> dict:
    """
    Migrate old preferences to v1.0.2 format.

    v1.0.0: had "c": null (C disabled)
    v1.0.1: had "c": "r" (C -> R, wrong direction)
    v1.0.2: "r": "c" (R -> C, correct direction), no "c" key in remap
    """
    remap = data.get("remap", {})

    # v1.0.1 had "c": "r" — remove it
    if "c" in remap:
        del remap["c"]

    # v1.0.0 had "c": null — remove it
    if "c" in remap:
        del remap["c"]

    # Add R -> C if not present
    if "r" not in remap:
        remap["r"] = "c"

    data["remap"] = remap

    # Add version marker
    data["version"] = "1.0.2"

    return data


# ================================================================
# Localizations
# ================================================================

LANG = {
    "en": {
        # Banner
        "banner_title": "Deltarune Key Remapper",
        "banner_wasd": "W A S D  ->  arrows (diagonals work)",
        "banner_q": "Q        ->  Z",
        "banner_e": "E        ->  X",
        "banner_r": "R        ->  C (phone menu)",
        "banner_toggle": "{hotkey}  —  toggle remap on/off",
        "banner_quit": "{hotkey}  —  quit the program",
        "banner_switch": "N        —  switch layout preset",
        "banner_console_quit": "Ctrl+C in this window — fallback quit",
        "banner_safety": "If something goes wrong — use Ctrl + Alt + Backspace",
        "banner_safety2": "It will kill the process instantly, regardless",
        "banner_safety3": "of keyboard state. Ctrl+Alt+Delete also always",
        "banner_safety4": "works and cannot be blocked by any program.",
        "banner_layout_note": "Layout: R->C because R is right next to E on the keyboard.",
        "banner_layout_note2": "Not perfect, but it works. Change it in preferences.json.",
        # Admin warning
        "admin_warning_title": "WARNING: NOT running as Administrator.",
        "admin_warning_line1": "On Windows without admin rights, keyboard often",
        "admin_warning_line2": "cannot intercept/emulate keys. If remap doesn't",
        "admin_warning_line3": "work in-game — close this window and re-launch",
        "admin_warning_line4": "via 'Run as Administrator'.",
        # Status
        "ready": "Ready. Remap active, switch to the game.",
        "remap_on": "Remap: ON",
        "remap_off": "Remap: OFF",
        "quit_msg": "Ctrl+Alt+Backspace — exiting...",
        "ctrl_c_msg": "Ctrl+C received, shutting down...",
        "hook_error": "Failed to install keyboard hook: {err}",
        "hook_error_hint": "Make sure the script is running as Administrator.",
        "key_error": "Error handling '{key}': {err}",
        "layout_switched": "Layout switched to: {name}",
        "migrated": "Settings migrated from old version to v1.0.2.",
        # Window detection
        "window_check_enabled": "Window detection: ON (Deltarune window must be focused)",
        "window_check_disabled": "Window detection: OFF",
        "window_not_found": "WARNING: Deltarune window not found! Remap may not work.",
        "window_not_focused": "WARNING: Deltarune is not the active window. Remap may not work in-game.",
        # Language selection
        "lang_prompt": "Select language / Выберите язык:",
        "lang_en": "1) English",
        "lang_ru": "2) Русский",
        "lang_choice": "Your choice (1 or 2): ",
        "lang_saved": "Language saved.",
        # Mode selection
        "mode_prompt": "Select interface mode:",
        "mode_nogui": "1) NonGUI (console)",
        "mode_gui": "2) GUI (PyQt6 window)",
        "mode_choice": "Your choice (1 or 2): ",
        "mode_saved": "Mode saved.",
        "mode_gui_missing": "PyQt6 not installed. Install with: pip install PyQt6",
        # Preferences
        "prefs_created": "Created default preferences.json",
        "prefs_loaded": "Loaded preferences from preferences.json",
        "prefs_saving": "Saving preferences...",
        # Config display
        "config_title": "Current configuration:",
        "config_remap": "Remap bindings:",
        "config_disabled": "(disabled)",
        "config_hotkeys": "Hotkeys:",
        "config_toggle": "Toggle:",
        "config_quit": "Quit:",
        "config_window_check": "Window detection:",
        "config_mode": "Mode:",
        "config_yes": "ON",
        "config_no": "OFF",
        # Interactive config
        "config_ask": "Would you like to configure key bindings? (y/n): ",
        "config_source_prompt": "Remap '{src}' to (leave empty to disable, or enter key name): ",
        "config_toggle_prompt": "Toggle hotkey (e.g. ctrl+alt+v): ",
        "config_quit_prompt": "Quit hotkey (e.g. ctrl+alt+backspace): ",
        "config_window_prompt": "Enable Deltarune window detection? (y/n): ",
        "config_saved": "Configuration saved to preferences.json",
        "config_key_disabled": "'{src}' remapping disabled.",
        "config_key_set": "'{src}' -> '{target}'",
        "config_invalid_key": "Invalid key name '{key}'. Use a valid keyboard key name.",
    },
    "ru": {
        # Banner
        "banner_title": "Ремап клавиш для Deltarune",
        "banner_wasd": "W A S D  ->  стрелки (диагонали работают)",
        "banner_q": "Q        ->  Z",
        "banner_e": "E        ->  X",
        "banner_r": "R        ->  C (меню звонка)",
        "banner_toggle": "{hotkey}  —  включить/выключить ремап",
        "banner_quit": "{hotkey}  —  выйти из программы",
        "banner_switch": "N        —  сменить раскладку",
        "banner_console_quit": "Ctrl+C в этом окне — запасной способ выйти",
        "banner_safety": "Если что-то пошло не так — используйте Ctrl + Alt + Backspace",
        "banner_safety2": "Она убьёт процесс мгновенно, независимо",
        "banner_safety3": "от состояния клавиатуры. Ctrl+Alt+Delete тоже всегда",
        "banner_safety4": "работает и не может быть заблокирована ни одной программой.",
        "banner_layout_note": "Раскладка: R->C потому что R рядом с E на клавиатуре.",
        "banner_layout_note2": "Не идеально, но работает. Можно поменять в preferences.json.",
        # Admin warning
        "admin_warning_title": "ВНИМАНИЕ: окно запущено НЕ от имени администратора.",
        "admin_warning_line1": "На Windows без прав администратора keyboard часто не",
        "admin_warning_line2": "может подавлять/перехватывать клавиши. Если ремап не",
        "admin_warning_line3": "срабатывает в игре — закройте окно и запустите скрипт",
        "admin_warning_line4": "через 'Запуск от имени администратора'.",
        # Status
        "ready": "Готово. Ремап активен, можно переключаться в игру.",
        "remap_on": "[Ремап] ВКЛЮЧЁН",
        "remap_off": "[Ремап] ВЫКЛЮЧЕН",
        "quit_msg": "[Ремап] Ctrl+Alt+Backspace — выхожу из программы...",
        "ctrl_c_msg": "\n[Ремап] Получен Ctrl+C, завершаюсь...",
        "hook_error": "Не удалось установить перехват клавиатуры: {err}",
        "hook_error_hint": "Убедитесь, что скрипт запущен от имени администратора.",
        "key_error": "Ошибка обработки '{key}': {err}",
        "layout_switched": "Раскладка переключена: {name}",
        "migrated": "Настройки мигрированы со старой версии на v1.0.2.",
        # Window detection
        "window_check_enabled": "Проверка окна: ВКЛ (окно Deltarune должно быть активным)",
        "window_check_disabled": "Проверка окна: ВЫКЛ",
        "window_not_found": "ВНИМАНИЕ: Окно Deltarune не найдено! Ремап может не работать.",
        "window_not_focused": "ВНИМАНИЕ: Deltarune не является активным окном. Ремап может не работать в игре.",
        # Language selection
        "lang_prompt": "Select language / Выберите язык:",
        "lang_en": "1) English",
        "lang_ru": "2) Русский",
        "lang_choice": "Your choice (1 or 2): ",
        "lang_saved": "Язык сохранён.",
        # Mode selection
        "mode_prompt": "Выберите режим интерфейса:",
        "mode_nogui": "1) NonGUI (консоль)",
        "mode_gui": "2) GUI (окно PyQt6)",
        "mode_choice": "Ваш выбор (1 или 2): ",
        "mode_saved": "Режим сохранён.",
        "mode_gui_missing": "PyQt6 не установлен. Установите: pip install PyQt6",
        # Preferences
        "prefs_created": "Создан default preferences.json",
        "prefs_loaded": "Загружены настройки из preferences.json",
        "prefs_saving": "Сохраняю настройки...",
        # Config display
        "config_title": "Текущая конфигурация:",
        "config_remap": "Привязки клавиш:",
        "config_disabled": "(отключено)",
        "config_hotkeys": "Горячие клавиши:",
        "config_toggle": "Переключение:",
        "config_quit": "Выход:",
        "config_window_check": "Проверка окна:",
        "config_mode": "Режим:",
        "config_yes": "ВКЛ",
        "config_no": "ВЫКЛ",
        # Interactive config
        "config_ask": "Настроить привязки клавиш? (y/n): ",
        "config_source_prompt": "Перенаправить '{src}' на (оставьте пустым для отключения, или введите имя клавиши): ",
        "config_toggle_prompt": "Горячая клавиша переключения (напр. ctrl+alt+v): ",
        "config_quit_prompt": "Горячая клавиша выхода (напр. ctrl+alt+backspace): ",
        "config_window_prompt": "Включить проверку окна Deltarune? (y/n): ",
        "config_saved": "Конфигурация сохранена в preferences.json",
        "config_key_disabled": "Перенаправление '{src}' отключено.",
        "config_key_set": "'{src}' -> '{target}'",
        "config_invalid_key": "Неверное имя клавиши '{key}'. Используйте корректное имя клавиши.",
    },
}


# ================================================================
# Layout presets
# ================================================================

LAYOUT_PRESETS = {
    "default": {
        "name_en": "Default (R->C)",
        "name_ru": "Стандартная (R->C)",
        "remap": {
            "w": "up",
            "a": "left",
            "s": "down",
            "d": "right",
            "q": "z",
            "e": "x",
            "r": "c",
        },
    },
    "classic": {
        "name_en": "Classic (no R)",
        "name_ru": "Классическая (без R)",
        "remap": {
            "w": "up",
            "a": "left",
            "s": "down",
            "d": "right",
            "q": "z",
            "e": "x",
            "r": None,
        },
    },
    "full": {
        "name_en": "Full (R->C pass-through)",
        "name_ru": "Полная (R->C проходит)",
        "remap": {
            "w": "up",
            "a": "left",
            "s": "down",
            "d": "right",
            "q": "z",
            "e": "x",
            "r": "c",
        },
    },
}


# ================================================================
# Configuration
# ================================================================

DEFAULT_REMAP = {
    "w": "up",
    "a": "left",
    "s": "down",
    "d": "right",
    "q": "z",
    "e": "x",
    "r": "c",
}

DEFAULT_HOTKEYS = {
    "toggle": "ctrl+alt+v",
    "quit": "ctrl+alt+backspace",
}

DEFAULT_CONFIG = {
    "language": None,
    "mode": None,
    "remap": dict(DEFAULT_REMAP),
    "hotkeys": dict(DEFAULT_HOTKEYS),
    "window_check": True,
    "layout_preset": "default",
    "version": "1.0.2",
}

# Valid keyboard key names for validation
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
    "ctrl","alt","shift","win",
}


# ================================================================
# Preferences management
# ================================================================

def load_preferences() -> tuple[dict, bool]:
    """Load preferences from JSON file, or return defaults.
    Returns (config, was_migrated)."""
    was_migrated = False
    if os.path.exists(PREFERENCES_FILE):
        try:
            with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check if migration is needed
            old_version = data.get("version", "1.0.0")
            if old_version in ("1.0.0", "1.0.1", None):
                data = migrate_preferences(data)
                was_migrated = True

            # Merge with defaults in case new keys were added
            config = dict(DEFAULT_CONFIG)
            config.update(data)
            if "remap" in data:
                remap = dict(DEFAULT_REMAP)
                remap.update(data["remap"])
                config["remap"] = remap
            if "hotkeys" in data:
                hotkeys = dict(DEFAULT_HOTKEYS)
                hotkeys.update(data["hotkeys"])
                config["hotkeys"] = hotkeys
            return config, was_migrated
        except (json.JSONDecodeError, IOError):
            pass
    return dict(DEFAULT_CONFIG), was_migrated


def save_preferences(config: dict, lang: str):
    t = LANG[lang]
    print(t["prefs_saving"])
    config["version"] = "1.0.2"
    with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# ================================================================
# Language selection
# ================================================================

def select_language(config: dict) -> str:
    if config.get("language") in ("en", "ru"):
        return config["language"]

    print("=" * 62)
    print("  Select language / Выберите язык:")
    print("=" * 62)
    print("  1) English")
    print("  2) Русский")
    print("=" * 62)

    while True:
        choice = input("  Your choice (1 or 2): ").strip()
        if choice == "1":
            lang = "en"
            break
        elif choice == "2":
            lang = "ru"
            break
        print("  Please enter 1 or 2 / Введите 1 или 2")

    config["language"] = lang
    save_preferences(config, lang)
    print(f"  {LANG[lang]['lang_saved']}")
    print()
    return lang


# ================================================================
# Mode selection (GUI / NonGUI)
# ================================================================

def select_mode(config: dict, lang: str) -> str:
    if config.get("mode") in ("gui", "nogui"):
        return config["mode"]

    t = LANG[lang]
    print("=" * 62)
    print(f"  {t['mode_prompt']}")
    print("=" * 62)
    print(f"  {t['mode_nogui']}")
    print(f"  {t['mode_gui']}")
    print("=" * 62)

    while True:
        choice = input(f"  {t['mode_choice']}").strip()
        if choice == "1":
            mode = "nogui"
            break
        elif choice == "2":
            try:
                import PyQt6  # noqa: F401
                mode = "gui"
            except ImportError:
                print(f"  {t['mode_gui_missing']}")
                continue
            break
        print("  Please enter 1 or 2 / Введите 1 или 2")

    config["mode"] = mode
    save_preferences(config, lang)
    print(f"  {t['mode_saved']}")
    print()
    return mode


# ================================================================
# Layout switching
# ================================================================

def switch_layout(config: dict, lang: str) -> dict:
    preset_keys = list(LAYOUT_PRESETS.keys())
    current = config.get("layout_preset", "default")
    try:
        idx = preset_keys.index(current)
    except ValueError:
        idx = 0
    next_idx = (idx + 1) % len(preset_keys)
    next_key = preset_keys[next_idx]

    preset = LAYOUT_PRESETS[next_key]
    config["layout_preset"] = next_key
    config["remap"] = dict(preset["remap"])

    name = preset[f"name_{lang}"]
    t = LANG[lang]
    print(t["layout_switched"].format(name=name))
    return config


# ================================================================
# Window detection
# ================================================================

def find_deltarune_hwnd() -> int | None:
    if not HAS_WIN32:
        return None

    result = [None]

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "deltarune" in title.lower():
                result[0] = hwnd
        return True

    win32gui.EnumWindows(callback, None)
    return result[0]


def is_deltarune_focused() -> bool:
    if not HAS_WIN32:
        return True

    hwnd = find_deltarune_hwnd()
    if hwnd is None:
        return False
    return win32gui.GetForegroundWindow() == hwnd


# ================================================================
# State
# ================================================================

class RemapState:
    def __init__(self, config: dict, lang: str):
        self.enabled = True
        self.running = True
        self.pressed_targets = set()
        self.config = config
        self.lang = lang
        self.window_warned = False
        self.t = LANG[lang]

    def release_all(self):
        for target in list(self.pressed_targets):
            try:
                keyboard.release(target)
            except Exception:
                pass
        self.pressed_targets.clear()

    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled:
            print(self.t["remap_on"])
        else:
            print(self.t["remap_off"])
        if not self.enabled:
            self.release_all()

    def request_quit(self):
        print(self.t["quit_msg"])
        self.running = False
        self.release_all()


# ================================================================
# Key handler
# ================================================================

def make_key_handler(state: RemapState, source_key: str, target_key: str):
    def handler(event: keyboard.KeyboardEvent) -> bool:
        try:
            if not state.enabled:
                return True

            if event.event_type == keyboard.KEY_DOWN:
                if target_key not in state.pressed_targets:
                    state.pressed_targets.add(target_key)
                    keyboard.press(target_key)
            elif event.event_type == keyboard.KEY_UP:
                if target_key in state.pressed_targets:
                    state.pressed_targets.discard(target_key)
                    keyboard.release(target_key)

            return False
        except Exception as exc:
            print(state.t["key_error"].format(key=source_key, err=repr(exc)))
            return True

    return handler


# ================================================================
# Hook management
# ================================================================

def install_hooks(state: RemapState, config: dict, lang: str):
    t = LANG[lang]
    try:
        for source_key, target_key in config["remap"].items():
            if target_key is not None:
                keyboard.hook_key(
                    source_key,
                    make_key_handler(state, source_key, target_key),
                    suppress=True,
                )

        keyboard.add_hotkey(config["hotkeys"]["toggle"], state.toggle, suppress=True)
        keyboard.add_hotkey(config["hotkeys"]["quit"], state.request_quit, suppress=True)
    except Exception as exc:
        print(t["hook_error"].format(err=repr(exc)))
        print(t["hook_error_hint"])
        sys.exit(1)


def reinstall_hooks(state: RemapState, config: dict, lang: str):
    try:
        keyboard.unhook_all()
    except Exception:
        pass
    state.pressed_targets.clear()
    install_hooks(state, config, lang)


# ================================================================
# Utilities
# ================================================================

def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def set_console_title(title: str):
    try:
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    except Exception:
        pass


# ================================================================
# Interactive configuration
# ================================================================

def interactive_config(config: dict, lang: str) -> dict:
    t = LANG[lang]

    print()
    print("=" * 62)
    print(f" {t['config_title']}")
    print("=" * 62)

    print(f" {t['config_remap']}")
    for src, tgt in config["remap"].items():
        if tgt is None:
            print(f"   {src.upper():>5}  ->  {t['config_disabled']}")
        else:
            print(f"   {src.upper():>5}  ->  {tgt}")

    print()
    print(f" {t['config_hotkeys']}")
    print(f"   {t['config_toggle']}  {config['hotkeys']['toggle']}")
    print(f"   {t['config_quit']}  {config['hotkeys']['quit']}")
    print()
    wc = t["config_yes"] if config.get("window_check", True) else t["config_no"]
    print(f" {t['config_window_check']}  {wc}")
    mode_str = "GUI" if config.get("mode") == "gui" else "NonGUI"
    print(f" {t['config_mode']}  {mode_str}")
    print("=" * 62)

    answer = input(f"\n {t['config_ask']}").strip().lower()
    if answer != "y":
        return config

    for src in list(config["remap"].keys()):
        current = config["remap"][src]
        current_str = current if current else ""
        prompt = t["config_source_prompt"].format(src=src.upper())
        if current_str:
            prompt += f" [{current_str}] "
        new_val = input(f"  {prompt}").strip().lower()

        if new_val == "":
            config["remap"][src] = None
            print(f"  -> {t['config_key_disabled'].format(src=src.upper())}")
        elif new_val in VALID_KEYS or "+" in new_val:
            config["remap"][src] = new_val
            print(f"  -> {t['config_key_set'].format(src=src.upper(), target=new_val)}")
        else:
            print(f"  -> {t['config_invalid_key'].format(key=new_val)}")
            print(f"  -> Kept: {current}")

    print()
    toggle = input(f"  {t['config_toggle_prompt']} [{config['hotkeys']['toggle']}] ").strip()
    if toggle:
        config["hotkeys"]["toggle"] = toggle

    quit_hk = input(f"  {t['config_quit_prompt']} [{config['hotkeys']['quit']}] ").strip()
    if quit_hk:
        config["hotkeys"]["quit"] = quit_hk

    print()
    wc_answer = input(f"  {t['config_window_prompt']}").strip().lower()
    config["window_check"] = wc_answer == "y"

    save_preferences(config, lang)
    print(f"\n {t['config_saved']}")
    return config


# ================================================================
# Banner
# ================================================================

def print_banner(config: dict, lang: str):
    t = LANG[lang]
    toggle_hk = config["hotkeys"]["toggle"]
    quit_hk = config["hotkeys"]["quit"]

    print("=" * 62)
    print(f" {t['banner_title']}")
    print("=" * 62)
    print(f" {t['banner_wasd']}")
    print(f" {t['banner_q']}")
    print(f" {t['banner_e']}")
    print(f" {t['banner_r']}")
    print("-" * 62)
    print(f" {t['banner_toggle'].format(hotkey=toggle_hk.upper())}")
    print(f" {t['banner_quit'].format(hotkey=quit_hk.upper())}")
    print(f" {t['banner_switch']}")
    print(f" {t['banner_console_quit']}")
    print("-" * 62)
    print(f" {t['banner_safety']}")
    print(f" {t['banner_safety2']}")
    print(f" {t['banner_safety3']}")
    print(f" {t['banner_safety4']}")
    print("-" * 62)
    print(f" {t['banner_layout_note']}")
    print(f" {t['banner_layout_note2']}")
    print("=" * 62)

    if not is_admin():
        print()
        print(f" {t['admin_warning_title']}")
        print(f" {t['admin_warning_line1']}")
        print(f" {t['admin_warning_line2']}")
        print(f" {t['admin_warning_line3']}")
        print(f" {t['admin_warning_line4']}")
    print()


# ================================================================
# GUI mode (PyQt6)
# ================================================================

def run_gui(config: dict, lang: str):
    """Run the remapper with a PyQt6 GUI window."""
    try:
        from PyQt6.QtWidgets import (
            QApplication, QMainWindow, QLabel, QVBoxLayout,
            QHBoxLayout, QWidget, QPushButton, QGroupBox,
            QFrame, QSizePolicy
        )
        from PyQt6.QtCore import Qt, QTimer
        from PyQt6.QtGui import QFont, QColor, QPalette
    except ImportError:
        t = LANG[lang]
        print(t["mode_gui_missing"])
        sys.exit(1)

    state = RemapState(config, lang)
    install_hooks(state, config, lang)

    app = QApplication(sys.argv)

    # Dark theme
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Base, QColor(40, 40, 40))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 50, 50))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(80, 120, 180))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    window = QMainWindow()
    window.setWindowTitle("Deltarune Key Remapper v1.0.2")
    window.setFixedSize(420, 400)
    window.setStyleSheet("""
        QMainWindow { background: #1e1e1e; }
        QGroupBox {
            font-size: 13px;
            font-weight: bold;
            color: #aaa;
            border: 1px solid #444;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 15px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
        }
        QLabel { color: #ddd; }
        QPushButton {
            background: #333;
            color: #ddd;
            border: 1px solid #555;
            border-radius: 5px;
            padding: 8px 16px;
            font-size: 13px;
        }
        QPushButton:hover { background: #444; border-color: #777; }
        QPushButton:pressed { background: #555; }
    """)

    central = QWidget()
    window.setCentralWidget(central)
    layout = QVBoxLayout(central)
    layout.setSpacing(8)

    # Status
    status_label = QLabel("REMAPPING: ACTIVE")
    status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4caf50; padding: 6px;")
    layout.addWidget(status_label)

    # Bindings group
    group = QGroupBox("  Active Bindings  ")
    group_layout = QVBoxLayout()
    group_layout.setSpacing(4)

    binding_labels = []
    for src, tgt in config["remap"].items():
        row = QHBoxLayout()
        key_from = QLabel(f"  {src.upper()}")
        key_from.setStyleSheet("font-size: 15px; font-weight: bold; color: #64b5f6; min-width: 40px;")
        arrow = QLabel("  ->  ")
        arrow.setStyleSheet("font-size: 13px; color: #888;")
        if tgt is not None:
            key_to = QLabel(f"{tgt}")
            key_to.setStyleSheet("font-size: 15px; font-weight: bold; color: #81c784;")
        else:
            key_to = QLabel("(disabled)")
            key_to.setStyleSheet("font-size: 13px; color: #666;")
        row.addWidget(key_from)
        row.addWidget(arrow)
        row.addWidget(key_to)
        row.addStretch()
        group_layout.addLayout(row)
        binding_labels.append((key_from, arrow, key_to))

    group.setLayout(group_layout)
    layout.addWidget(group)

    # Buttons
    btn_layout = QHBoxLayout()

    toggle_btn = QPushButton(f"Toggle\n({config['hotkeys']['toggle'].upper()})")
    toggle_btn.setMinimumHeight(50)
    toggle_btn.setStyleSheet("""
        QPushButton { font-size: 12px; background: #2e7d32; color: white; border: none; border-radius: 6px; }
        QPushButton:hover { background: #388e3c; }
    """)
    toggle_btn.clicked.connect(state.toggle)
    btn_layout.addWidget(toggle_btn)

    switch_btn = QPushButton("Switch\nLayout (N)")
    switch_btn.setMinimumHeight(50)
    switch_btn.setStyleSheet("""
        QPushButton { font-size: 12px; background: #1565c0; color: white; border: none; border-radius: 6px; }
        QPushButton:hover { background: #1976d2; }
    """)
    def on_switch():
        nonlocal config
        config = switch_layout(config, lang)
        reinstall_hooks(state, config, lang)
        for i, (src, tgt) in enumerate(config["remap"].items()):
            if i < len(binding_labels):
                _, _, key_to = binding_labels[i]
                if tgt is not None:
                    key_to.setText(f"{tgt}")
                    key_to.setStyleSheet("font-size: 15px; font-weight: bold; color: #81c784;")
                else:
                    key_to.setText("(disabled)")
                    key_to.setStyleSheet("font-size: 13px; color: #666;")
    switch_btn.clicked.connect(on_switch)
    btn_layout.addWidget(switch_btn)

    quit_btn = QPushButton(f"Quit\n({config['hotkeys']['quit'].upper()})")
    quit_btn.setMinimumHeight(50)
    quit_btn.setStyleSheet("""
        QPushButton { font-size: 12px; background: #c62828; color: white; border: none; border-radius: 6px; }
        QPushButton:hover { background: #d32f2f; }
    """)
    quit_btn.clicked.connect(state.request_quit)
    btn_layout.addWidget(quit_btn)

    layout.addLayout(btn_layout)

    # Timer
    def update():
        if state.enabled:
            status_label.setText("REMAPPING: ACTIVE")
            status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4caf50; padding: 6px;")
        else:
            status_label.setText("REMAPPING: PAUSED")
            status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f44336; padding: 6px;")
        if not state.running:
            app.quit()

    timer = QTimer()
    timer.timeout.connect(update)
    timer.start(100)

    window.show()
    app.exec()

    state.release_all()
    try:
        keyboard.unhook_all()
    except Exception:
        pass


# ================================================================
# Main
# ================================================================

def main():
    config, was_migrated = load_preferences()
    first_run = not os.path.exists(PREFERENCES_FILE)

    # Language selection
    lang = select_language(config)
    t = LANG[lang]

    # Show migration notice
    if was_migrated:
        print(f" {t['migrated']}")
        save_preferences(config, lang)
        print()

    # Mode selection on first run
    if first_run:
        mode = select_mode(config, lang)
    else:
        mode = config.get("mode", "nogui")

    # Interactive config on first run
    if first_run:
        config = interactive_config(config, lang)

    # Set console title
    set_console_title("Deltarune Remap")

    # GUI mode
    if mode == "gui":
        run_gui(config, lang)
        return

    # NonGUI mode
    print_banner(config, lang)

    if config.get("window_check", True):
        print(f" {t['window_check_enabled']}")
    else:
        print(f" {t['window_check_disabled']}")
    print()

    print(f" {t['config_remap']}")
    for src, tgt in config["remap"].items():
        if tgt is not None:
            print(f"   {src.upper():>5}  ->  {tgt}")
    print()

    state = RemapState(config, lang)
    install_hooks(state, config, lang)

    # Layout switch via N key
    def on_layout_switch():
        nonlocal config
        config = switch_layout(config, lang)
        reinstall_hooks(state, config, lang)
        print(f"\n {t['config_remap']}")
        for src, tgt in config["remap"].items():
            if tgt is not None:
                print(f"   {src.upper():>5}  ->  {tgt}")
        print()

    keyboard.add_hotkey("n", on_layout_switch, suppress=True)

    print(f" {t['ready']}")
    print()

    window_warn_shown = False
    try:
        while state.running:
            time.sleep(0.1)

            if config.get("window_check", True) and HAS_WIN32:
                hwnd = find_deltarune_hwnd()
                if hwnd is None:
                    if not window_warn_shown:
                        print(f" {t['window_not_found']}")
                        window_warn_shown = True
                else:
                    if not is_deltarune_focused():
                        if not window_warn_shown:
                            print(f" {t['window_not_focused']}")
                            window_warn_shown = True
                    else:
                        window_warn_shown = False

    except KeyboardInterrupt:
        print(t["ctrl_c_msg"])
    finally:
        state.release_all()
        try:
            keyboard.unhook_all()
        except Exception:
            pass
        sys.exit(0)


if __name__ == "__main__":
    main()
