# Deltarune Key Remapper (Latest Version: v1.0.6)

🌐 **Language / Язык:**
* [🇬🇧 English Version](#-english-version)
* [🇷🇺 Русская версия](#-русская-версия)

---

## 🇬🇧 English Version

Custom Deltarune keybind configuration script by FoxVuk. GUI-only key remapper with multi-profile support.

### How It Works

The game receives fixed target keys: **arrows, Z, X, C**. You choose which physical keys trigger them via GUI profiles.

### Features

* **Multi-Profile Support**: Create, delete, rename, export, import profiles. Each profile has its own key bindings.
* **Default Profile**: Protected, auto-generated, cannot be deleted or renamed. Always reverts to default bindings.
* **Full Customization**: Rebind any source key to any target (Up/Down/Left/Right/Z/X/C) — in the GUI.
* **GUI Only**: PyQt6 window with profile selector, rebind buttons, settings.
* **Full Diagonal Support**: Simultaneous key presses work perfectly.
* **Window Detection**: Warns when Deltarune window is not found or not focused.
* **Global Hotkeys**: `Ctrl+Alt+V` (toggle), `Ctrl+Alt+Backspace` (quit).
* **Auto Update Check**: Checks GitHub on startup. Three modes: `imp` (mandatory), `notimp` (optional), `ignore`.
* **Bilingual**: English and Russian.
* **Configurable Logs**: Enable/disable logs, set log level (debug/info/warn/error).
* **Auto Migration**: Settings from v1.0.0-v1.0.4 are automatically converted.
* **Profile Fallback**: Corrupted profiles are automatically removed.

### Default Bindings

| Action | Game gets | You press |
|--------|-----------|-----------|
| Up     | Up arrow  | W         |
| Down   | Down arrow| S         |
| Left   | Left arrow| A         |
| Right  | Right arrow| D        |
| Confirm| Z         | Q         |
| Cancel | X         | E         |
| Phone  | C         | R         |

### Files

| File | Description |
|------|-------------|
| `profiles.json` | All profiles and their bindings |
| `preferences.json` | App settings (language, active profile, logs, etc.) |

### Installation & Launch

1. Install dependencies:
   ```bash
   pip install keyboard PyQt6
   ```
2. Optional (window detection):
   ```bash
   pip install pywin32
   ```
3. Run **as Administrator**.

### Safety

* Hooks ONLY the keys in your config. Nothing else is blocked.
* `Ctrl+Alt+Delete` always works (OS-level).
* `STOP_REMAP.bat` — double-click to kill the process instantly.

---

## 🇷🇺 Русская версия

Скрипт для изменения раскладки управления в Deltarune от FoxVuk. GUI-ремаппер с мульти-профилями.

### Как это работает

Игра получает фиксированные целевые клавиши: **стрелки, Z, X, C**. Вы выбираете какие физические клавиши их активируют через профили в GUI.

### Возможности

* **Мульти-профили**: Создавайте, удаляйте, переименовывайте, экспортируйте, импортируйте профили. У каждого свои привязки.
* **Профиль Default**: Защищён, генерируется автоматически, нельзя удалить или переименовать. Всегда возвращается к дефолтным привязкам.
* **Полная кастомизация**: Переназначьте любую клавишу — прямо в GUI.
* **Только GUI**: Окно PyQt6 с выбором профиля, кнопками rebind, настройками.
* **Поддержка диагоналей**: Одновременные нажатия работают идеально.
* **Проверка окна**: Предупреждает, если окно Deltarune не найдено.
* **Горячие клавиши**: `Ctrl+Alt+V` (переключение), `Ctrl+Alt+Backspace` (выход).
* **Авто-проверка обновлений**: Проверяет GitHub при запуске. Три режима: `imp` (обязательно), `notimp` (опционально), `ignore`.
* **Двуязычный интерфейс**: Английский и русский.
* **Настраиваемые логи**: Включение/выключение, уровень (debug/info/warn/error).
* **Авто-миграция**: Настройки с v1.0.0-v1.0.4 конвертируются.
* **Fallback профилей**: Повреждённые профили удаляются автоматически.

### Файлы

| Файл | Описание |
|------|----------|
| `profiles.json` | Все профили и их привязки |
| `preferences.json` | Настройки приложения (язык, активный профиль, логи и т.д.) |

### Установка и запуск

1. Установите зависимости:
   ```bash
   pip install keyboard PyQt6
   ```
2. Опционально (проверка окна):
   ```bash
   pip install pywin32
   ```
3. Запустите **от имени администратора**.

### Безопасность

* Перехватывает ТОЛЬКО клавиши из вашего конфига. Ничего больше не блокируется.
* `Ctrl+Alt+Delete` всегда работает (на уровне ОС).
* `STOP_REMAP.bat` — двойной клик мгновенно убивает процесс.
