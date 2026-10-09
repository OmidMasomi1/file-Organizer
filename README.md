# 📁 File Organizer

A portable Windows app (Persian/English UI) that organizes your files into folders by **type and date** — with one click.

No installation needed. Just download, unzip and run.

## ✨ Features

- 🗂️ Organize images, videos, music, documents, archives and programs
- 📅 Jalali (شمسی) and Gregorian date folders (`1404-06` / `2024-09`)
- 📷 Real shooting date from EXIF (photos) and `mvhd` metadata (videos), with file-date fallback
- 🕓 History of the last 10 operations — each one undoable separately
- 🗑️ Delete history entries you no longer want to undo
- 🎨 Dark / Light / Match-Windows themes + glass effect
- 🌐 Full Persian (B Nazanin) and English (Segoe UI) interface
- 🖱️ Double-click any folder to open it in Explorer
- 🐙 Built-in links: Help, Donate, Settings, GitHub

## 🚀 Download & Run

1. Go to the [Releases](../../releases) page
2. Download the latest `FileOrganizer_Portable_App_Vx.x.zip`
3. Unzip anywhere and run **`FileOrganizer.exe`**

> Works on any Windows 10/11 machine — nothing to install.

## 🖥️ Usage

1. **Add Folder** — pick the folder(s) you want to organize
2. **Preview** — see the transfer structure first
3. **Start Organizing** — files are moved, empty folders are removed
4. **History** — view, undo, or delete past operations

> 💡 If a category has fewer than 15 files in a month, no extra subfolder is created.

## ❤️ Support

If you enjoy this app, consider supporting the developer:

**[☕ Buy me a coffee](https://omidmasomi1.github.io/)**

## 🛠️ Build from Source

```bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --name FileOrganizer file_organizer.py
