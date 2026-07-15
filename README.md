# Deltarune Key Remapper

🌐 **Language / Язык:**
* [🇬🇧 English Version](#-english-version)
* [🇷🇺 Русская версия](#-русская-версия)

---

## 🇬🇧 English Version

Custom Deltarune keybind configuration script by FoxVuk. Remaps control keys to a classic layout and handles system execution safely.

### Features

* **WASD -> Arrows** (Up / Left / Down / Right)
* **Q -> Z** (Confirm / Interact)
* **E -> X** (Cancel / Run)
* **C -> configurable** (disabled by default, set in preferences.json)
* **Full Diagonal Support**: Handles simultaneous key presses perfectly without ghosting or stuck keys.
* **Custom Key Bindings**: Remap any key to any other key, or disable remapping for specific keys entirely.
* **Window Detection**: Warns when Deltarune window is not found or not focused.
* **Global Hotkeys**:
  * `Ctrl + Alt + V` — Toggle remapper ON/OFF
  * `Ctrl + Alt + Backspace` — Force quit the application
* **Bilingual Interface**: English and Russian, selectable on first run.
* **Persistent Settings**: All configuration saved to `preferences.json`.

### Configuration (preferences.json)

Created automatically on first run. You can edit it manually or reconfigure interactively.

```json
{
  "language": "en",
  "remap": {
    "w": "up",
    "a": "left",
    "s": "down",
    "d": "right",
    "q": "z",
    "e": "x",
    "c": null
  },
  "hotkeys": {
    "toggle": "ctrl+alt+v",
    "quit": "ctrl+alt+backspace"
  },
  "window_check": true
}
```

* Set a key's value to `null` to disable remapping for that key.
* `window_check` enables/disables Deltarune window detection warnings.

### Installation & Launch

1. Install the required dependency (only once):
   ```bash
   pip install keyboard
   ```
2. Optional: for window detection, install `pywin32`:
   ```bash
   pip install pywin32
   ```
3. Run the provided `.bat` file **as Administrator** (required for Windows to capture and emulate system-level keyboard inputs safely).

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

### Возможности

* **WASD -> Стрелки** (Вверх / Влево / Вниз / Вправо)
* **Q -> Z** (Подтверждение / Действие)
* **E -> X** (Отмена / Бег)
* **C -> настраивается** (по умолчанию отключено, настраивается в preferences.json)
* **Поддержка диагоналей**: Корректно обрабатывает любые одновременные нажатия без залипания клавиш.
* **Пользовательские привязки клавиш**: Можно перенаправить любую клавишу на любую другую, или отключить перенаправление для отдельных клавиш.
* **Проверка окна**: Предупреждает, если окно Deltarune не найдено или не активно.
* **Горячие клавиши**:
  * `Ctrl + Alt + V` — Включить / Выключить ремап
  * `Ctrl + Alt + Backspace` — Быстрый выход из программы
* **Двуязычный интерфейс**: Английский и русский, выбор при первом запуске.
* **Сохранение настроек**: Все настройки сохраняются в `preferences.json`.

### Конфигурация (preferences.json)

Создаётся автоматически при первом запуске. Можно редактировать вручную или перенастроить интерактивно.

```json
{
  "language": "ru",
  "remap": {
    "w": "up",
    "a": "left",
    "s": "down",
    "d": "right",
    "q": "z",
    "e": "x",
    "c": null
  },
  "hotkeys": {
    "toggle": "ctrl+alt+v",
    "quit": "ctrl+alt+backspace"
  },
  "window_check": true
}
```

* Установите значение клавиши в `null` чтобы отключить перенаправление для неё.
* `window_check` включает/отключает предупреждения о окне Deltarune.

### Установка и запуск

1. Установите необходимую библиотеку (один раз):
   ```bash
   pip install keyboard
   ```
2. Опционально: для проверки окна установите `pywin32`:
   ```bash
   pip install pywin32
   ```
3. Запустите `.bat` файл **от имени администратора** (это обязательно, чтобы Windows разрешила перехватывать и эмулировать нажатия клавиш на системном уровне).

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
