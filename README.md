# Deltarune Key Remapper

🌐 **Language / Язык:**
* [🇬🇧 English Version](#-english-version)
* [🇷🇺 Русская версия](#-русская-версия)

---

## 🇬🇧 English Version

Custom Deltarune keybind configuration script by FoxVuk. Fully customizable key remapping with GUI and console modes.

### How It Works

The game receives fixed target keys: **arrows, Z, X, C**. You choose which physical keys trigger them. Default: W A S D Q E R — but you can change every single one directly in the program.

### Features

* **Full Customization**: Rebind any source key to any target (Up/Down/Left/Right/Z/X/C) — right in the program, not just in JSON.
* **GUI Mode**: PyQt6 window with Rebind buttons — click, press a key, done.
* **NonGUI Mode**: Console interface — press 1-7 to select an action, then press your desired key.
* **Full Diagonal Support**: Simultaneous key presses work perfectly.
* **Window Detection**: Warns when Deltarune window is not found or not focused.
* **Global Hotkeys**:
  * `Ctrl + Alt + V` — Toggle remapper ON/OFF
  * `Ctrl + Alt + Backspace` — Force quit
* **Bilingual**: English and Russian, selectable on first run.
* **Persistent Settings**: All bindings saved to `preferences.json`.
* **Auto Migration**: Settings from v1.0.0-v1.0.2 are automatically converted.

### Default Bindings

| Action | Target (game gets) | Source (you press) |
|--------|-------------------|-------------------|
| Up     | Up arrow          | W                 |
| Down   | Down arrow        | S                 |
| Left   | Left arrow        | A                 |
| Right  | Right arrow       | D                 |
| Confirm| Z                 | Q                 |
| Cancel | X                 | E                 |
| Phone  | C                 | R                 |

### Configuration (preferences.json)

```json
{
  "language": "en",
  "mode": "nogui",
  "targets": {
    "up": "w",
    "down": "s",
    "left": "a",
    "right": "d",
    "z": "q",
    "x": "e",
    "c": "r"
  },
  "hotkeys": {
    "toggle": "ctrl+alt+v",
    "quit": "ctrl+alt+backspace"
  },
  "window_check": true,
  "version": "1.0.3"
}
```

* `targets` maps each game action to the physical key you press.
* Set a source to `null` to disable that action.

### Installation & Launch

1. Install dependency:
   ```bash
   pip install keyboard
   ```
2. Optional (window detection):
   ```bash
   pip install pywin32
   ```
3. Optional (GUI mode):
   ```bash
   pip install PyQt6
   ```
4. Run **as Administrator**.

### Safety

* Hooks ONLY the keys in your config. Nothing else is blocked.
* `Ctrl+Alt+Delete` always works (OS-level).
* `STOP_REMAP.bat` — double-click to kill the process instantly.

---

## 🇷🇺 Русская версия

Скрипт для изменения раскладки управления в Deltarune от FoxVuk. Полная кастомизация привязок клавиш с GUI и консольным режимами.

### Как это работает

Игра получает фиксированные целевые клавиши: **стрелки, Z, X, C**. Вы выбираете какие физические клавиши их активируют. По умолчанию: W A S D Q E R — но каждую можно поменять прямо в программе.

### Возможности

* **Полная кастомизация**: Переназначьте любую клавишу на любое действие (Вверх/Вниз/Влево/Вправо/Z/X/C) — прямо в программе, не только в JSON.
* **GUI режим**: Окно PyQt6 с кнопками Rebind — нажмите, нажмите клавишу, готово.
* **NonGUI режим**: Консоль — нажмите 1-7 для выбора действия, затем нажмите нужную клавишу.
* **Поддержка диагоналей**: Одновременные нажатия работают идеально.
* **Проверка окна**: Предупреждает, если окно Deltarune не найдено.
* **Горячие клавиши**:
  * `Ctrl + Alt + V` — Включить/выключить ремап
  * `Ctrl + Alt + Backspace` — Быстрый выход
* **Двуязычный интерфейс**: Английский и русский.
* **Сохранение настроек**: Все привязки в `preferences.json`.
* **Автоматическая миграция**: Настройки с v1.0.0-v1.0.2 конвертируются.

### Конфигурация (preferences.json)

```json
{
  "language": "ru",
  "mode": "nogui",
  "targets": {
    "up": "w",
    "down": "s",
    "left": "a",
    "right": "d",
    "z": "q",
    "x": "e",
    "c": "r"
  },
  "hotkeys": {
    "toggle": "ctrl+alt+v",
    "quit": "ctrl+alt+backspace"
  },
  "window_check": true,
  "version": "1.0.3"
}
```

* `targets` связывает каждое действие с клавишей, которую вы нажимаете.
* Установите значение в `null` чтобы отключить действие.

### Установка и запуск

1. Установите зависимость:
   ```bash
   pip install keyboard
   ```
2. Опционально (проверка окна):
   ```bash
   pip install pywin32
   ```
3. Опционально (GUI режим):
   ```bash
   pip install PyQt6
   ```
4. Запустите **от имени администратора**.

### Безопасность

* Перехватывает ТОЛЬКО клавиши из вашего конфига. Ничего больше не блокируется.
* `Ctrl+Alt+Delete` всегда работает (на уровне ОС).
* `STOP_REMAP.bat` — двойной клик мгновенно убивает процесс.
