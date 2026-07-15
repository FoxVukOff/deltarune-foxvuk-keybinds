# Deltarune Key Remapper

🌐 **Language / Язык:**
* [🇬🇧 English Version](#-english-version)
* [🇷🇺 Русская версия](#-русская-версия)

---

## 🇬🇧 English Version

Custom Deltarune keybind configuration script by FoxVuk. Remaps control keys to a classic layout and handles system execution safely.

### About the Layout

Why R -> C? Because R is right next to E on the keyboard — it's the closest convenient key for the phone/call menu. Is this the perfect layout? Honestly, no. But it works, it's nearby, and after trying a few options this is what stuck. You can change any binding in `preferences.json` or switch presets by pressing **N** in-game.

### Features

* **WASD -> Arrows** (Up / Left / Down / Right)
* **Q -> Z** (Confirm / Interact)
* **E -> X** (Cancel / Run)
* **R -> C** (Phone / Call menu — R is right next to E)
* **Full Diagonal Support**: Handles simultaneous key presses perfectly without ghosting or stuck keys.
* **Custom Key Bindings**: Remap any key to any other key, or disable remapping for specific keys entirely.
* **Layout Presets**: Press **N** to cycle through presets (Default, Classic, Full). Changeable anytime.
* **Window Detection**: Warns when Deltarune window is not found or not focused.
* **GUI & NonGUI Modes**: Console interface by default, or optional PyQt6 GUI window.
* **Global Hotkeys**:
  * `Ctrl + Alt + V` — Toggle remapper ON/OFF
  * `Ctrl + Alt + Backspace` — Force quit the application
* **Bilingual Interface**: English and Russian, selectable on first run.
* **Persistent Settings**: All configuration saved to `preferences.json`.
* **Auto Migration**: Settings from v1.0.0/v1.0.1 are automatically migrated to v1.0.2.

### Configuration (preferences.json)

Created automatically on first run. You can edit it manually or reconfigure interactively.

```json
{
  "language": "en",
  "mode": "nogui",
  "remap": {
    "w": "up",
    "a": "left",
    "s": "down",
    "d": "right",
    "q": "z",
    "e": "x",
    "r": "c"
  },
  "hotkeys": {
    "toggle": "ctrl+alt+v",
    "quit": "ctrl+alt+backspace"
  },
  "window_check": true,
  "layout_preset": "default",
  "version": "1.0.2"
}
```

* Set a key's value to `null` to disable remapping for that key.
* `mode`: `"nogui"` for console, `"gui"` for PyQt6 window.
* `window_check` enables/disables Deltarune window detection warnings.
* `layout_preset`: `"default"` (R->C), `"classic"` (no R), `"full"` (R->C pass-through).

### Installation & Launch

1. Install the required dependency (only once):
   ```bash
   pip install keyboard
   ```
2. Optional: for window detection, install `pywin32`:
   ```bash
   pip install pywin32
   ```
3. Optional: for GUI mode, install `PyQt6`:
   ```bash
   pip install PyQt6
   ```
4. Run the provided `.bat` file **as Administrator** (required for Windows to capture and emulate system-level keyboard inputs safely).

### Building to EXE

Use `build.bat` to compile to a standalone EXE:
```bash
build.bat
```
The EXE will be in the `dist/` folder.

### Safety

* The script hooks ONLY the keys listed in your config — each via its own `keyboard.hook_key()`. Nothing else is hooked.
* `Alt+Tab`, `Win`, `Esc`, `F-keys`, `Ctrl+Shift+Esc` etc. cannot be blocked by this script.
* `Ctrl+Alt+Delete` on Windows ALWAYS works (Secure Attention Sequence).
* `STOP_REMAP.bat` — double-click to instantly kill the script via taskkill.

---

## 🇷🇺 Русская версия

Скрипт для изменения раскладки управления в Deltarune от FoxVuk. Переносит стрелки на WASD и подготавливает удобную среду для запуска.

### О раскладке

Почему R -> C? Потому что R рядом с E на клавиатуре — это ближайшая удобная клавиша для меню звонка. Идеальная ли это раскладка? Честно, нет. Но работает, находится рядом, и после нескольких попыток это то, что осталось. Любую привязку можно поменять в `preferences.json` или переключать пресеты клавишей **N** прямо в игре.

### Возможности

* **WASD -> Стрелки** (Вверх / Влево / Вниз / Вправо)
* **Q -> Z** (Подтверждение / Действие)
* **E -> X** (Отмена / Бег)
* **R -> C** (Меню звонка — R рядом с E)
* **Поддержка диагоналей**: Корректно обрабатывает любые одновременные нажатия без залипания клавиш.
* **Пользовательские привязки клавиш**: Можно перенаправить любую клавишу на любую другую, или отключить перенаправление для отдельных клавиш.
* **Пресеты раскладок**: Нажмите **N** для переключения (Стандартная, Классическая, Полная). Можно менять в любой момент.
* **Проверка окна**: Предупреждает, если окно Deltarune не найдено или не активно.
* **GUI и NonGUI режимы**: Консольный интерфейс по умолчанию, или опциональное окно PyQt6.
* **Горячие клавиши**:
  * `Ctrl + Alt + V` — Включить / Выключить ремап
  * `Ctrl + Alt + Backspace` — Быстрый выход из программы
* **Двуязычный интерфейс**: Английский и русский, выбор при первом запуске.
* **Сохранение настроек**: Все настройки сохраняются в `preferences.json`.
* **Автоматическая миграция**: Настройки с v1.0.0/v1.0.1 автоматически мигрируют на v1.0.2.

### Конфигурация (preferences.json)

Создаётся автоматически при первом запуске. Можно редактировать вручную или перенастроить интерактивно.

```json
{
  "language": "ru",
  "mode": "nogui",
  "remap": {
    "w": "up",
    "a": "left",
    "s": "down",
    "d": "right",
    "q": "z",
    "e": "x",
    "r": "c"
  },
  "hotkeys": {
    "toggle": "ctrl+alt+v",
    "quit": "ctrl+alt+backspace"
  },
  "window_check": true,
  "layout_preset": "default",
  "version": "1.0.2"
}
```

* Установите значение клавиши в `null` чтобы отключить перенаправление для неё.
* `mode`: `"nogui"` для консоли, `"gui"` для окна PyQt6.
* `window_check` включает/отключает предупреждения о окне Deltarune.
* `layout_preset`: `"default"` (R->C), `"classic"` (без R), `"full"` (R->C проходит).

### Установка и запуск

1. Установите необходимую библиотеку (один раз):
   ```bash
   pip install keyboard
   ```
2. Опционально: для проверки окна установите `pywin32`:
   ```bash
   pip install pywin32
   ```
3. Опционально: для GUI режима установите `PyQt6`:
   ```bash
   pip install PyQt6
   ```
4. Запустите `.bat` файл **от имени администратора** (это обязательно, чтобы Windows разрешила перехватывать и эмулировать нажатия клавиш на системном уровне).

### Сборка в EXE

Используйте `build.bat` для компиляции в автономный EXE:
```bash
build.bat
```
EXE будет в папке `dist/`.

### Безопасность

* Скрипт перехватывает ТОЛЬКО клавиши из вашего конфига — каждую через отдельный `keyboard.hook_key()`. Больше ничего не хукается.
* `Alt+Tab`, `Win`, `Esc`, `F-клавиши`, `Ctrl+Shift+Esc` и т.д. не могут быть заблокированы этим скриптом.
* `Ctrl+Alt+Delete` на Windows ВСЕГДА работает (Secure Attention Sequence).
* `STOP_REMAP.bat` — двойной клик мгновенно убивает процесс скрипта через taskkill.
