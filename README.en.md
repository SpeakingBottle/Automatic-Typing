# Automatic Typing

[简体中文](README.md) | English

A Windows desktop tool that simulates real keyboard input to type text or code into a target window character by character. It is useful for text boxes that block paste and only accept manual input.

## Features

- General text input with **Article / Homework** and **Code** presets
- Presets automatically switch font, typing speed, and indentation strategy
- Character-by-character keyboard simulation for English, numbers, symbols, Chinese, Chinese punctuation, and emoji
- Adjustable typing speed (30 ms – 500 ms per character) with optional natural rhythm (±30% random delay)
- 1 / 3 / 5 / 10 second countdown with a circular always-on-top overlay at the top center
- When the countdown ends, the overlay becomes a compact control bar with progress, percentage, remaining time, pause/resume, and stop
- The main window minimizes automatically after starting and restores when typing finishes or stops
- Live character count, line count, and estimated duration
- Pause, resume, stop, and clipboard import
- Light / dark theme and always-on-top window mode
- Chinese / English interface switching
- Empty editor automatically disables the **Start typing** button
- Lucide open-source icons and a crisp multi-size application/taskbar icon
- `start.bat` launches with `pythonw.exe`, so no console window stays open
- Standalone `.exe` packaging configuration

## Requirements

- Windows 10 / 11
- Python 3.10+ (developed and verified with Python 3.13)
- Dependencies: `customtkinter`, `pyperclip`, `Pillow`, `pyinstaller`
- Administrator privileges are not required

## Quick Start

### Run from source

```bash
git clone https://github.com/SpeakingBottle/Automatic-Typing.git
cd Automatic-Typing
pip install -r requirements.txt
python main.py
```

You can also double-click `start.bat`. It uses `pythonw.exe` so the application runs without a persistent console window. Run `python main.py` instead if you want to see console output while debugging.

### Build an executable

```bash
pip install -r requirements.txt
pyinstaller build.spec
```

The output is `dist/自动打字.exe`.

## Usage

1. Start the application. The **Article / Homework** preset is selected by default.
2. Paste or type text, or click **Read clipboard**.
3. Switch to the **Code** preset if needed, then adjust speed and countdown.
4. Click **Start typing**. The main window minimizes and a circular countdown overlay appears at the top center of the screen.
5. Before the countdown ends, switch to the target input field and keep that window in the foreground.
6. When the countdown ends, the overlay becomes a control bar for progress, pause/resume, and stop.
7. When typing finishes, the main window restores and the button still reads **Start typing**.
8. Use the language button (文A) in the top-right corner to switch between Chinese and English.

## Notes

- Switch to the target window before the countdown ends; otherwise the text will be typed into this application's own editor.
- The target window must stay active and in the foreground while typing.
- If the target editor does not auto-indent (for example, Notepad), turn off **Skip leading indentation** in Advanced settings.
- Auto-completion in some editors may insert extra closing brackets. Disable auto-completion in the target editor when possible.
- Typing too fast may trigger platform anti-bot checks. Keeping the delay between 100 ms and 300 ms is recommended.

## Project Structure

```text
Automatic-Typing/
├── main.py              # Entry point
├── ui/                  # UI layer (theme, presets, i18n, icons, panels)
│   ├── i18n.py          #   Chinese / English text
│   ├── countdown.py     #   Countdown and typing control overlay
│   └── ...
├── engine/              # Typing engine and SendInput wrapper
├── utils/               # Clipboard, resource path, and foreground window helpers
├── assets/              # Application icon and Lucide PNGs
│   └── icons/
├── tools/               # Icon generation tools (development only)
├── tests/               # unittest suite
├── docs/                # Documentation center
│   ├── README.md        #   Documentation index and rules
│   ├── analysis/        #   Requirements, technical design, UI design
│   ├── agent-reference/ #   Development, testing, release, troubleshooting
│   ├── history-version/ #   Archived release documentation
│   └── templates/       #   Reusable templates
├── AGENTS.md            # Agent working guide
├── CLAUDE.md            # Pointer to AGENTS.md
├── CHANGELOG.md         # Version history
├── README.md            # Chinese README
├── README.en.md         # English README
├── LICENSE              # MIT License
├── requirements.txt     # Python dependencies
├── build.spec           # PyInstaller configuration
├── test_sendinput.py    # Standalone SendInput test
└── start.bat            # Windows launcher (pythonw, no console)
```

## Documentation

The documentation is currently written in Chinese:

- [Documentation index](docs/README.md)
- [Requirements](docs/analysis/requirements.md)
- [Technical design](docs/analysis/technical-design.md)
- [UI design](docs/analysis/ui-design.md)
- [Development guide](docs/agent-reference/development.md)
- [Testing guide](docs/agent-reference/testing.md)
- [Release guide](docs/agent-reference/release.md)
- [Troubleshooting](docs/agent-reference/troubleshooting.md)
- [Changelog](CHANGELOG.md)
- [Agent guide](AGENTS.md)

## Contributing

Issues and pull requests are welcome. Before submitting code, read the [development guide](docs/agent-reference/development.md) and [testing guide](docs/agent-reference/testing.md), and make sure manual testing covers basic input, Chinese, Unicode, newlines, indentation, and control actions.

## Disclaimer

This project is for technical learning and research. Follow the terms of service of any target platform. The authors are not responsible for consequences caused by other uses.

## License

Released under the [MIT License](LICENSE).
