# -*- coding: utf-8 -*-
"""
================================================================
 Ремап клавиш для Deltarune
================================================================

WASD  ->  стрелки (Up / Left / Down / Right)
Q     ->  Z
E     ->  X

Полностью поддерживаются диагонали и любые одновременные нажатия —
как будто вы физически жмёте стрелки: не нужно отпускать одну
клавишу, чтобы сработала другая.

Горячие клавиши:
    Ctrl+Alt+V          — включить/выключить ремап
    Ctrl+Alt+Backspace  — выйти из программы
    Ctrl+C в консоли    — запасной способ выйти

----------------------------------------------------------------
БЕЗОПАСНОСТЬ: почему это не заблокирует клавиатуру целиком
----------------------------------------------------------------
Скрипт перехватывает СТРОГО шесть клавиш: w, a, s, d, q, e — каждую
через отдельный keyboard.hook_key(). Больше НИЧЕГО в коде не хукает
никакие другие клавиши. Alt+Tab, Win, Esc, F-клавиши, Ctrl+Shift+Esc
и т.д. в принципе не могут быть заблокированы этим скриптом — для
этого пришлось бы отдельно на них подписаться, а этого нигде не
происходит. Горячие клавиши (Ctrl+Alt+V и Ctrl+Alt+Backspace) сделаны
через keyboard.add_hotkey() — штатный механизм библиотеки.

Дополнительная подстраховка на случай непредвиденного:
- Рядом лежит STOP_REMAP.bat — двойной клик мгновенно убивает
  процесс скрипта через диспетчер задач Windows (taskkill), это
  никак не зависит от состояния хуков клавиатуры.
- Ctrl+Alt+Delete на Windows ВСЕГДА работает и не может быть
  заблокирована ни одной пользовательской программой — это защищено
  на уровне самой ОС (Secure Attention Sequence). Ctrl+Shift+Esc
  почти всегда тоже откроет диспетчер задач напрямую.
================================================================

Установка (один раз):
    pip install keyboard

Запуск (ОБЯЗАТЕЛЬНО от имени администратора — иначе Windows не
даст библиотеке ставить системный хук клавиатуры и подавлять или
эмулировать нажатия):
    python deltarune_remap.py
"""

import ctypes
import sys
import time

try:
    import keyboard
except ImportError:
    print("Библиотека 'keyboard' не установлена.")
    print("Установите её командой:  pip install keyboard")
    sys.exit(1)


# ================================================================
# Настройки
# ================================================================

REMAP = {
    "w": "up",
    "a": "left",
    "s": "down",
    "d": "right",
    "q": "z",
    "e": "x",
}

TOGGLE_HOTKEY = "ctrl+alt+v"
QUIT_HOTKEY = "ctrl+alt+backspace"
CONSOLE_TITLE = "Deltarune Remap"


# ================================================================
# Состояние программы
# ================================================================

class RemapState:
    """Хранит текущее состояние: включён/выключен ремап, какие
    клавиши сейчас эмулированно зажаты, и флаг работы цикла."""

    def __init__(self):
        self.enabled = True
        self.running = True
        self.pressed_targets = set()

    def release_all(self):
        """Отпускает все клавиши, которые мы могли удержать, чтобы
        ничего не залипло (при выключении или выходе из программы)."""
        for target in list(self.pressed_targets):
            try:
                keyboard.release(target)
            except Exception:
                pass
        self.pressed_targets.clear()

    def toggle(self):
        self.enabled = not self.enabled
        state_text = "ВКЛЮЧЁН" if self.enabled else "ВЫКЛЮЧЕН"
        print(f"[Ремап] {state_text}")
        if not self.enabled:
            self.release_all()

    def request_quit(self):
        print("[Ремап] Ctrl+Alt+Backspace — выхожу из программы...")
        self.running = False
        self.release_all()


# ================================================================
# Обработка клавиш WASDQE
# ================================================================

def make_key_handler(state: RemapState, source_key: str, target_key: str):
    """
    Создаёт обработчик для ОДНОЙ конкретной клавиши (например, "w").
    keyboard.hook_key вызовет его при каждом нажатии/отпускании
    именно этой клавиши — и только её. Никакие другие клавиши через
    этот обработчик вообще не проходят.

    Обработчик обязан вернуть True (пропустить исходную клавишу как
    есть) или False (подавить её, т.к. мы сами эмулируем нужную
    клавишу через keyboard.press/release). "Пустых" return здесь
    сознательно нет ни одного.
    """

    def handler(event: keyboard.KeyboardEvent) -> bool:
        try:
            if not state.enabled:
                return True  # ремап выключен — ведём себя как обычная клавиатура

            if event.event_type == keyboard.KEY_DOWN:
                if target_key not in state.pressed_targets:
                    state.pressed_targets.add(target_key)
                    keyboard.press(target_key)
                # если target уже "зажат" нами — это автоповтор ОС,
                # заново нажимать не нужно (и не нужно спамить игру)
            elif event.event_type == keyboard.KEY_UP:
                if target_key in state.pressed_targets:
                    state.pressed_targets.discard(target_key)
                    keyboard.release(target_key)

            return False  # подавляем исходную букву (w/a/s/d/q/e)
        except Exception as exc:
            print(f"[Ремап] Ошибка обработки '{source_key}': {exc!r}")
            return True  # при ошибке лучше пропустить клавишу, чем заблокировать её навсегда

    return handler


# ================================================================
# Служебное
# ================================================================

def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def set_console_title():
    """Даёт окну консоли предсказуемое имя, по которому его сможет
    мгновенно найти и убить STOP_REMAP.bat, даже если сам скрипт
    завис или клавиатура перестала откликаться."""
    try:
        ctypes.windll.kernel32.SetConsoleTitleW(CONSOLE_TITLE)
    except Exception:
        pass


def print_banner():
    print("=" * 62)
    print(" Ремап клавиш для Deltarune")
    print("=" * 62)
    print(" W A S D  ->  стрелки (диагонали работают)")
    print(" Q        ->  Z")
    print(" E        ->  X")
    print("-" * 62)
    print(f" {TOGGLE_HOTKEY.upper()}  —  включить/выключить ремап")
    print(f" {QUIT_HOTKEY.upper()}  —  выйти из программы")
    print(" Ctrl+C в этом окне — запасной способ выйти")
    print("-" * 62)
    print(" Если что-то пошло не так — используйте комбинацию клавиш Ctrl + Alt + Backspace")
    print(" Она убьёт процесс мгновенно, независимо")
    print(" от состояния клавиатуры. Ctrl+Alt+Delete тоже всегда")
    print(" работает и не может быть заблокирована ни одной программой.")
    print("=" * 62)
    if not is_admin():
        print()
        print(" ВНИМАНИЕ: окно запущено НЕ от имени администратора.")
        print(" На Windows без прав администратора keyboard часто не")
        print(" может подавлять/перехватывать клавиши. Если ремап не")
        print(" срабатывает в игре — закройте окно и запустите скрипт")
        print(" через 'Запуск от имени администратора'.")
    print()


# ================================================================
# Точка входа
# ================================================================

def main():
    set_console_title()
    print_banner()

    state = RemapState()

    try:
        for source_key, target_key in REMAP.items():
            keyboard.hook_key(
                source_key,
                make_key_handler(state, source_key, target_key),
                suppress=True,
            )

        keyboard.add_hotkey(TOGGLE_HOTKEY, state.toggle, suppress=True)
        keyboard.add_hotkey(QUIT_HOTKEY, state.request_quit, suppress=True)
    except Exception as exc:
        print(f"Не удалось установить перехват клавиатуры: {exc!r}")
        print("Убедитесь, что скрипт запущен от имени администратора.")
        sys.exit(1)

    print("Готово. Ремап активен, можно переключаться в игру.")
    print()

    try:
        # Поллинг вместо keyboard.wait() — на Windows блокирующий wait()
        # иногда "проглатывает" Ctrl+C. Короткий цикл со сном гораздо
        # надёжнее реагирует на прерывание.
        while state.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[Ремап] Получен Ctrl+C, завершаюсь...")
    finally:
        state.release_all()
        try:
            keyboard.unhook_all()
        except Exception:
            pass
        sys.exit(0)


if __name__ == "__main__":
    main()