# -*- coding: utf-8 -*-
"""
================================================================
 Deltarune Key Remapper
================================================================

WASD  ->  arrows (Up / Left / Down / Right)
Q     ->  Z
E     ->  X
C     ->  configurable (disabled by default)

Fully supports diagonals and any simultaneous key presses —
as if you were physically pressing the arrows: you don't need to
release one key for another to work.

Hotkeys:
    Ctrl+Alt+V          — toggle remap on/off
    Ctrl+Alt+Backspace  — quit the program
    Ctrl+C in console   — fallback quit

----------------------------------------------------------------
SAFETY: why this won't lock your keyboard
----------------------------------------------------------------
The script hooks EXACTLY the keys listed in your config — each
via its own keyboard.hook_key(). NOTHING else is hooked. Alt+Tab,
Win, Esc, F-keys, Ctrl+Shift+Esc etc. cannot be blocked by this
script. Hotkeys (Ctrl+Alt+V and Ctrl+Alt+Backspace) use the
standard keyboard.add_hotkey() mechanism.

Additional safety net:
- STOP_REMAP.bat sits nearby — double-click instantly kills the
  script process via Windows taskkill, regardless of hook state.
- Ctrl+Alt+Delete on Windows ALWAYS works and cannot be blocked
  by any user-mode program (Secure Attention Sequence).

----------------------------------------------------------------
First run: language selection (EN / RU)
All settings are saved to preferences.json.
================================================================

Installation (once):
    pip install keyboard

Launch (MUST be run as Administrator — otherwise Windows won't
let the library install a system keyboard hook):
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
    import win32process
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


# ================================================================
# Paths
# ================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PREFERENCES_FILE = os.path.join(SCRIPT_DIR, "preferences.json")


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
        "banner_c": "C        ->  configurable (see preferences.json)",
        "banner_toggle": "{hotkey}  —  toggle remap on/off",
        "banner_quit": "{hotkey}  —  quit the program",
        "banner_console_quit": "Ctrl+C in this window — fallback quit",
        "banner_safety": "If something goes wrong — use Ctrl + Alt + Backspace",
        "banner_safety2": "It will kill the process instantly, regardless",
        "banner_safety3": "of keyboard state. Ctrl+Alt+Delete also always",
        "banner_safety4": "works and cannot be blocked by any program.",
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
        "banner_c": "C        ->  настраивается (см. preferences.json)",
        "banner_toggle": "{hotkey}  —  включить/выключить ремап",
        "banner_quit": "{hotkey}  —  выйти из программы",
        "banner_console_quit": "Ctrl+C в этом окне — запасной способ выйти",
        "banner_safety": "Если что-то пошло не так — используйте Ctrl + Alt + Backspace",
        "banner_safety2": "Она убьёт процесс мгновенно, независимо",
        "banner_safety3": "от состояния клавиатуры. Ctrl+Alt+Delete тоже всегда",
        "banner_safety4": "работает и не может быть заблокирована ни одной программой.",
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
# Configuration
# ================================================================

DEFAULT_REMAP = {
    "w": "up",
    "a": "left",
    "s": "down",
    "d": "right",
    "q": "z",
    "e": "x",
    "c": None,
}

DEFAULT_HOTKEYS = {
    "toggle": "ctrl+alt+v",
    "quit": "ctrl+alt+backspace",
}

DEFAULT_CONFIG = {
    "language": None,
    "remap": dict(DEFAULT_REMAP),
    "hotkeys": dict(DEFAULT_HOTKEYS),
    "window_check": True,
}

# Valid keyboard key names for validation
VALID_KEYS = {
    # Letters
    "a","b","c","d","e","f","g","h","i","j","k","l","m",
    "n","o","p","q","r","s","t","u","v","w","x","y","z",
    # Digits
    "0","1","2","3","4","5","6","7","8","9",
    # Arrows
    "up","down","left","right",
    # Function keys
    "f1","f2","f3","f4","f5","f6","f7","f8","f9","f10","f11","f12",
    # Common keys
    "space","enter","tab","esc","backspace","delete","insert",
    "home","end","pageup","pagedown",
    "capslock","numlock","scrolllock",
    # Punctuation
    "`","-","=","[","]","\\",";","'",",",".","/",
    # Modifiers (can be used in combos)
    "ctrl","alt","shift","win",
}


# ================================================================
# Preferences management
# ================================================================

def load_preferences() -> dict:
    """Load preferences from JSON file, or return defaults."""
    if os.path.exists(PREFERENCES_FILE):
        try:
            with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
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
            return config
        except (json.JSONDecodeError, IOError):
            pass
    return dict(DEFAULT_CONFIG)


def save_preferences(config: dict, lang: str):
    """Save configuration to JSON file."""
    t = LANG[lang]
    print(t["prefs_saving"])
    with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# ================================================================
# Language selection
# ================================================================

def select_language(config: dict) -> str:
    """Ask user to pick language on first run. Returns 'en' or 'ru'."""
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
# Window detection
# ================================================================

def find_deltarune_hwnd() -> int | None:
    """Find the Deltarune window handle. Returns None if not found."""
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
    """Check if Deltarune window is the foreground window."""
    if not HAS_WIN32:
        return True  # Can't check, assume OK

    hwnd = find_deltarune_hwnd()
    if hwnd is None:
        return False
    return win32gui.GetForegroundWindow() == hwnd


# ================================================================
# State
# ================================================================

class RemapState:
    """Stores current state: enabled/disabled, pressed keys, running flag."""

    def __init__(self, config: dict, lang: str):
        self.enabled = True
        self.running = True
        self.pressed_targets = set()
        self.config = config
        self.lang = lang
        self.window_warned = False
        self.t = LANG[lang]

    def release_all(self):
        """Release all keys we might have held down."""
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
    """Create a handler for ONE specific key."""

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

            return False  # suppress original key
        except Exception as exc:
            print(state.t["key_error"].format(key=source_key, err=repr(exc)))
            return True

    return handler


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
    """Ask user to configure key bindings interactively."""
    t = LANG[lang]

    print()
    print("=" * 62)
    print(f" {t['config_title']}")
    print("=" * 62)

    # Display current config
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
    print("=" * 62)

    answer = input(f"\n {t['config_ask']}").strip().lower()
    if answer != "y":
        return config

    # Remap each key
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

    # Hotkeys
    print()
    toggle = input(f"  {t['config_toggle_prompt']} [{config['hotkeys']['toggle']}] ").strip()
    if toggle:
        config["hotkeys"]["toggle"] = toggle

    quit_hk = input(f"  {t['config_quit_prompt']} [{config['hotkeys']['quit']}] ").strip()
    if quit_hk:
        config["hotkeys"]["quit"] = quit_hk

    # Window check
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
    print(f" {t['banner_c']}")
    print("-" * 62)
    print(f" {t['banner_toggle'].format(hotkey=toggle_hk.upper())}")
    print(f" {t['banner_quit'].format(hotkey=quit_hk.upper())}")
    print(f" {t['banner_console_quit']}")
    print("-" * 62)
    print(f" {t['banner_safety']}")
    print(f" {t['banner_safety2']}")
    print(f" {t['banner_safety3']}")
    print(f" {t['banner_safety4']}")
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
# Main
# ================================================================

def main():
    # Load or create preferences
    config = load_preferences()
    first_run = not os.path.exists(PREFERENCES_FILE)

    if first_run:
        # Will create file during language selection
        pass

    # Language selection
    lang = select_language(config)
    t = LANG[lang]

    # Interactive config on first run
    if first_run:
        config = interactive_config(config, lang)

    # Set console title
    set_console_title("Deltarune Remap")

    # Print banner
    print_banner(config, lang)

    # Window detection info
    if config.get("window_check", True):
        print(f" {t['window_check_enabled']}")
    else:
        print(f" {t['window_check_disabled']}")
    print()

    # Display active remap
    print(f" {t['config_remap']}")
    for src, tgt in config["remap"].items():
        if tgt is not None:
            print(f"   {src.upper():>5}  ->  {tgt}")
    print()

    # Build state
    state = RemapState(config, lang)

    # Install hooks
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

    print(f" {t['ready']}")
    print()

    # Main loop
    window_warn_shown = False
    try:
        while state.running:
            time.sleep(0.1)

            # Window detection
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
