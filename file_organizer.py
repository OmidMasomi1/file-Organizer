import os
import shutil
import struct
import threading
import json
import hashlib
import winreg
from datetime import datetime, timedelta
from pathlib import Path
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox

VERSION = "2.9.0"

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".svg", ".heic", ".raw"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".3gp"},
    "Music": {".mp3", ".flac", ".wav", ".aac", ".ogg", ".m4a", ".wma", ".opus"},
    "Documents": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".csv", ".rtf"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".iso"},
    "Programs": {".exe", ".msi", ".bat", ".sh", ".apk"},
}

STRUCTURES = {
    "simple": "simple",
    "date_type": "date_type",
    "type_date": "type_date",
    "type_only": "type_only",
    "date_only": "date_only",
}

DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "FileOrganizer"
DATA_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
SOURCES_FILE = DATA_DIR / "sources.json"

# ---------- ترجمه‌ها ----------
TR = {
    "fa": {
        "app_title": "مرتب‌ساز فایل‌ها", "folders": "پوشه‌ها / درایوها:", "add_folder": "افزودن پوشه",
        "add_drive": "افزودن درایو", "remove": "حذف", "preview": "پیش‌نمایش", "start": "شروع مرتب‌سازی",
        "duplicates": "", "history": "تاریخچه عملیات", "undo_this": "بازگشت همین مورد",
        "undo_select": "اول یک عملیات رو از لیست انتخاب کن", "version": f"نسخه {VERSION}",
        "close": "بستن", "record_limit": "فقط 10 عملیات اخیر نگه داشته می‌شود",
        "delete_hist": "حذف از تاریخچه", "done_msg": "انتقال انجام شد",
        "loved": "آیا از این برنامه لذت بردید؟", "thanks": "از نظر و حمایت شما ممنونیم",
        "undo_done": "بازگشت عملیات انجام شد",
        "creator": "سازنده: امید معصومی", "email": "masomiomid911@gmail.com",
        "options_title": "تنظیمات مرتب‌سازی", "mode": "روش دسته‌بندی", "calendar": "تقویم",
        "out_where": "محل خروجی و گزینه‌ها", "sample": "نمونه ساختار", "confirm": "تایید و شروع", "cancel": "انصراف",
        "jalali": "شمسی (مثال: 1404-06)", "gregorian": "میلادی (مثال: 2024-09)",
        "in_source": "داخل هر پوشه مبدا", "custom_dest": "پوشه مقصد مشترک",
        "recursive": "زیرفولدرها هم بررسی بشن", "simple": "ساده (پیشنهادی)", "date_type": "تاریخ ← نوع",
        "type_date": "نوع ← تاریخ", "type_only": "فقط نوع", "date_only": "فقط تاریخ",
        "help_title": "راهنما", "settings_title": "تنظیمات", "theme": "تم", "lang": "زبان",
        "dark": "تیره", "light": "روشن", "system": "مطابق ویندوز", "apply": "اعمال",
        "moved": "منتقل شد:", "done": "تمام شد", "persian": "فارسی", "english": "English",
        "no_folder": "حداقل یک پوشه انتخاب کن", "files_count": "تعداد فایل:", "file": "فایل",
        "confirm_move": "فایل منتقل می‌شه. ادامه بدم؟", "restore_confirm": "برگرده؟",
        "dup_title": "پیدا کردن فایل‌های تکراری", "scan": "شروع اسکن", "details": "جزئیات",
        "delete_sel": "حذف موارد انتخاب‌شده", "scan_hint": "هنوز اسکنی انجام نشده",
        "close": "بستن", "restore_this": "بازگشت همین مورد", "glass": "حالت شیشه‌ای",
        "history_note": "فقط 10 عملیات اخیر نگه داشته می‌شود", "delete_hist": "حذف مورد انتخاب‌شده",
        "done_title": "انتقال انجام شد", "enjoy": "آیا از این برنامه لذت بردید؟", "thanks": "از نظر و حمایت شما ممنونیم",
        "scanning": "در حال بررسی فایل‌ها...", "folder_missing": "این پوشه دیگر وجود ندارد",
        "appearance": "ظاهر", "preferences": "ترجیحات",
        "theme_sub": "ظاهر برنامه رو انتخاب کن", "lang_sub": "زبان برنامه رو انتخاب کن",
        "glass_sub": "شفافیت کم پنجره‌ها", "donate": "حمایت",
        "donate_soon": "صفحه حمایت به‌زودی اضافه می‌شه ☕",
        "help_body": (
            "راهنمای مرتب‌ساز فایل‌ها\n\n"
            "• پوشه یا درایو موردنظر رو اضافه کن.\n"
            "• «پیش‌نمایش» بزن تا ساختار انتقال رو ببینی.\n"
            "• در تنظیمات، روش دسته‌بندی، تقویم و محل خروجی رو انتخاب کن.\n"
            "• «شروع مرتب‌سازی» فایل‌ها رو منتقل و پوشه‌های خالی رو حذف می‌کنه.\n\n"
            "• تاریخ واقعی عکس‌ها و فیلم‌ها از خود فایل خونده می‌شه.\n"
            "• «تاریخچه عملیات» تا 10 عملیات اخیر رو نگه می‌داره و هر کدوم از همون پنجره قابل بازگشته.\n\n"
            "• نظرات و یا انتقاداتتون رو می‌تونید با این آدرس ایمیل به اشتراک بذارید."
        ),
    },
    "en": {
        "app_title": "File Organizer", "folders": "Folders / Drives:", "add_folder": "Add Folder",
        "add_drive": "Add Drive", "remove": "Remove", "preview": "Preview", "start": "Start Organizing",
        "duplicates": "Duplicate Files", "history": "History", "undo_this": "Undo This Item",
        "undo_select": "Select an operation first", "version": f"Version {VERSION}",
        "close": "Close", "record_limit": "Only the last 10 operations are kept",
        "delete_hist": "Delete from History", "done_msg": "Transfer Complete",
        "loved": "Did you enjoy this app?", "thanks": "Thanks for your feedback and support",
        "undo_done": "Undo completed",
        "creator": "Created by: Omid Masoumi", "email": "masomiomid911@gmail.com",
        "options_title": "Organizing Settings", "mode": "Structure Mode", "calendar": "Calendar",
        "out_where": "Output & Options", "sample": "Sample Structure", "confirm": "Confirm & Start", "cancel": "Cancel",
        "jalali": "Jalali (e.g. 1404-06)", "gregorian": "Gregorian (e.g. 2024-09)",
        "in_source": "Inside each source folder", "custom_dest": "Custom destination folder",
        "recursive": "Include subfolders", "simple": "Simple (recommended)", "date_type": "Date → Type",
        "type_date": "Type → Date", "type_only": "Type only", "date_only": "Date only",
        "help_title": "Help", "settings_title": "Settings", "theme": "Theme", "lang": "Language",
        "dark": "Dark", "light": "Light", "system": "Match Windows", "apply": "Apply",
        "moved": "Moved:", "done": "Done", "persian": "Persian", "english": "English",
        "no_folder": "Add at least one folder", "files_count": "Files:", "file": "file(s)",
        "confirm_move": "files will be moved. Continue?", "restore_confirm": "be restored?",
        "dup_title": "Find Duplicate Files", "scan": "Start Scan", "details": "Details",
        "delete_sel": "Delete Selected", "scan_hint": "No scan yet",
        "close": "Close", "restore_this": "Undo This Item", "glass": "Glass effect",
        "history_note": "Only the last 10 operations are kept", "delete_hist": "Delete Selected",
        "done_title": "Done", "enjoy": "Did you enjoy this app?", "thanks": "Thanks for your support",
        "scanning": "Scanning files...", "folder_missing": "This folder no longer exists",
        "appearance": "Appearance", "preferences": "Preferences",
        "theme_sub": "Choose app appearance theme", "lang_sub": "Choose app language",
        "glass_sub": "Slight window transparency", "donate": "Donate",
        "donate_soon": "Donation page coming soon",
        "help_body": (
            "File Organizer Guide\n\n"
            "• Add the folder or drive you want to organize.\n"
            "• Click Preview to see the transfer structure.\n"
            "• In Settings, choose the structure mode, calendar and output location.\n"
            "• Start Organizing moves files and removes empty folders.\n\n"
            "• Real dates of photos and videos are read from the file itself.\n"
            "• History keeps the last 10 operations, each undoable from that window.\n\n"
            "• Share your comments or suggestions with this email address."
        ),
    },
}

GITHUB_URL = "https://github.com/omidmasomi1"
DONATE_URL = "https://omidmasomi1.github.io/"

SETTINGS = {"theme": "system", "lang": "fa"}
try:
    SETTINGS.update(json.loads(SETTINGS_FILE.read_text(encoding="utf-8")))
except Exception:
    pass


def T(key):
    return TR.get(SETTINGS["lang"], TR["fa"]).get(key, key)


def system_is_dark():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as k:
            val, _ = winreg.QueryValueEx(k, "AppsUseLightTheme")
            return val == 0
    except Exception:
        return False


def current_theme():
    t = SETTINGS["theme"]
    if t == "system":
        return "dark" if system_is_dark() else "light"
    return t


def palette():
    dark = current_theme() == "dark"
    en = SETTINGS["lang"] == "en"
    if dark:
        if en:
            return {"bg": "#17181f", "bg2": "#22232d", "fg": "#f2f2f7",
                    "accent": "#6c63ff", "gray": "#9a9ab2", "border": "#34353f"}
        return {"bg": "#202020", "bg2": "#2d2d2d", "fg": "#ffffff",
                "accent": "#4cc2ff", "gray": "#9a9aa3", "border": "#3a3a3a"}
    if en:
        return {"bg": "#f4f5f9", "bg2": "#ffffff", "fg": "#1b1c28",
                "accent": "#5b5bd6", "gray": "#8b8b9e", "border": "#e3e4ee"}
    return {"bg": "#f9f9f9", "bg2": "#ffffff", "fg": "#1d1d1f",
            "accent": "#0067C0", "gray": "#7a7a82", "border": "#e2e2e6"}


def is_en():
    return SETTINGS["lang"] == "en"


def anchor_side():
    return "w" if is_en() else "e"


def pack_side():
    return "left" if is_en() else "right"


def justify_side():
    return "left" if is_en() else "right"


FONT_FAMILY_LATIN = "Segoe UI"
FONT_FAMILY_FA = "B Nazanin"

def _pick_fonts():
    if SETTINGS["lang"] == "en":
        return FONT_FAMILY_LATIN, (FONT_FAMILY_LATIN, 10), (FONT_FAMILY_LATIN, 10, "bold"), ("Consolas", 10)
    return FONT_FAMILY_FA, (FONT_FAMILY_FA, 13), (FONT_FAMILY_FA, 13, "bold"), ("Consolas", 11)

FONT_FAMILY, FONT, FONT_B, FONT_MONO = _pick_fonts()


def to_jalali(gy, gm, gd):
    g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gy2 = gy - 1600
    gm2 = gm - 1
    gd2 = gd - 1
    g_day_no = 365 * gy2 + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400
    for i in range(gm2):
        g_day_no += g_days_in_month[i]
    if gm2 > 1 and ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
        g_day_no += 1
    g_day_no += gd2
    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053
    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461
    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365
    if j_day_no < 186:
        jm = 1 + j_day_no // 31
        jd = 1 + j_day_no % 31
    else:
        jm = 7 + (j_day_no - 186) // 30
        jd = 1 + (j_day_no - 186) % 30
    return jy, jm, jd


def _exif_bytes(path: Path):
    try:
        with open(path, "rb") as f:
            data = f.read(512_000)  # هدر EXIF ابتدای فایل است؛ خواندن کمتر = سرعت بیشتر
    except Exception:
        return None
    ext = path.suffix.lower()
    if ext in (".jpg", ".jpeg", ".tif", ".tiff", ".webp"):
        idx = data.find(b"Exif\x00\x00")
        if idx >= 0:
            return data[idx + 6:]
        if ext == ".webp":
            idx = data.find(b"EXIF")
            if idx >= 0:
                return data[idx + 4:]
        if ext in (".tif", ".tiff") and data[:2] in (b"II", b"MM"):
            return data
    if ext == ".png":
        idx = data.find(b"eXIf")
        if idx >= 0:
            return data[idx + 4:]
    return None


def _parse_exif_date(exif: bytes):
    try:
        if exif[:2] == b"II":
            endian = "<"
        elif exif[:2] == b"MM":
            endian = ">"
        else:
            return None
        ifd_offset = struct.unpack(endian + "I", exif[4:8])[0]

        def read_ifd(offset):
            count = struct.unpack(endian + "H", exif[offset:offset + 2])[0]
            for i in range(count):
                entry = exif[offset + 2 + i * 12: offset + 14 + i * 12]
                if len(entry) < 12:
                    continue
                tag, typ, cnt, val_off = struct.unpack(endian + "HHII", entry)
                yield tag, typ, cnt, val_off

        exif_ifd = None
        candidates = []
        for tag, typ, cnt, val_off in read_ifd(ifd_offset):
            if tag == 0x8769:
                exif_ifd = val_off
        if exif_ifd is not None:
            for tag, typ, cnt, val_off in read_ifd(exif_ifd):
                if tag in (0x9003, 0x9004):
                    candidates.append(exif[val_off:val_off + cnt].rstrip(b"\x00").decode("ascii", "ignore"))
        if not candidates:
            for tag, typ, cnt, val_off in read_ifd(ifd_offset):
                if tag == 0x0132:
                    candidates.append(exif[val_off:val_off + cnt].rstrip(b"\x00").decode("ascii", "ignore"))
        for raw in candidates:
            try:
                return datetime.strptime(raw.strip(), "%Y:%m:%d %H:%M:%S")
            except Exception:
                continue
    except Exception:
        return None
    return None


def _mp4_creation_time(path: Path):
    def _find_mvhd(data: bytes):
        mvhd = data.find(b"mvhd")
        if mvhd < 0 or len(data) < mvhd + 16:
            return None
        version = data[mvhd + 4]
        if version == 0:
            creation = struct.unpack(">I", data[mvhd + 8:mvhd + 12])[0]
        else:
            creation = struct.unpack(">Q", data[mvhd + 8:mvhd + 16])[0]
        if creation == 0:
            return None
        return datetime(1904, 1, 1) + timedelta(seconds=creation)

    try:
        with open(path, "rb") as f:
            head = f.read(1_000_000)
        d = _find_mvhd(head)
        if d:
            return d
        # جعبه moov خیلی وقت‌ها ته فایل است
        try:
            size = path.stat().st_size
            if size > 1_000_000:
                with open(path, "rb") as f:
                    f.seek(max(0, size - 1_000_000))
                    return _find_mvhd(f.read())
        except Exception:
            pass
        return None
    except Exception:
        return None


def media_datetime(path: Path) -> datetime:
    ext = path.suffix.lower()
    if ext in (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"):
        exif = _exif_bytes(path)
        if exif:
            d = _parse_exif_date(exif)
            if d:
                return d
    if ext in (".mp4", ".mov", ".m4v"):
        d = _mp4_creation_time(path)
        if d:
            return d
    return datetime.fromtimestamp(path.stat().st_mtime)


def file_category(path: Path) -> str:
    ext = path.suffix.lower()
    for name, exts in CATEGORIES.items():
        if ext in exts:
            return name
    return "Others"


def file_date_part(path: Path, calendar: str = "jalali") -> str:
    dt = media_datetime(path)
    if calendar == "gregorian":
        return f"{dt.year}-{dt.month:02d}"
    jy, jm, _ = to_jalali(dt.year, dt.month, dt.day)
    return f"{jy}-{jm:02d}"


def build_dest(root: Path, path: Path, structure: str, calendar: str = "jalali") -> Path:
    cat = file_category(path)
    date = file_date_part(path, calendar)
    cat_name = cat.lower()
    if structure == "simple":
        if cat == "Images":
            return root / date
        return root / date / cat_name
    if structure == "date_type":
        return root / date / cat_name
    if structure == "type_date":
        return root / cat_name / date
    if structure == "type_only":
        return root / cat_name
    return root / date


def apply_theme(root):
    p = palette()
    root.configure(bg=p["bg"])
    try:
        root.attributes("-alpha", 0.98 if SETTINGS.get("glass", True) else 1.0)
    except Exception:
        pass
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", background=p["bg"], foreground=p["fg"], font=FONT)
    style.configure("TLabel", background=p["bg"], foreground=p["fg"], font=FONT)
    style.configure("TFrame", background=p["bg"])
    style.configure("TLabelframe", background=p["bg"], foreground=p["accent"], borderwidth=1)
    style.configure("TLabelframe.Label", background=p["bg"], foreground=p["accent"], font=FONT_B)
    style.configure("TRadiobutton", background=p["bg"], foreground=p["fg"], font=FONT, indicatorcolor=p["accent"])
    style.map("TRadiobutton", background=[("active", p["bg"])])
    style.configure("TCheckbutton", background=p["bg"], foreground=p["fg"], font=FONT, indicatorcolor=p["accent"])
    style.configure("TEntry", fieldbackground=p["bg2"], foreground=p["fg"])
    style.configure("TButton", background=p["bg2"], foreground=p["fg"], borderwidth=1, relief="raised", padding=(12, 6))
    style.map("TButton", background=[("active", p["accent"])], foreground=[("active", "white")])
    style.configure("Accent.TButton", background=p["accent"], foreground="white", font=FONT_B, relief="raised")
    style.map("Accent.TButton", background=[("active", p["accent"])])
    style.configure("green.Horizontal.TProgressbar", troughcolor=p["bg2"], background=p["accent"], thickness=14)
    return p


class RoundedButton(tk.Canvas):
    """دکمه گرد با رنگ hover/press."""
    def __init__(self, parent, text, command, accent=False, icon="", width=None, height=34, fg=None):
        p = palette()
        self.accent = accent
        self.command = command
        self.normal = p["accent"] if accent else p["bg2"]
        self.hover = p["accent"] if accent else p["accent"]
        self.press = "#0070b8" if current_theme() == "light" else "#3a9bd5"
        self.fg = fg or ("white" if accent else p["fg"])
        self.text = (icon + "  " if icon else "") + text
        super().__init__(parent, bg=p["bg"], highlightthickness=0, bd=0,
                         width=width or self._fit_width(), height=height, cursor="hand2")
        self._draw(self.normal)
        self.bind("<Enter>", lambda e: self._draw(self.hover, fg="white"))
        self.bind("<Leave>", lambda e: self._draw(self.normal, fg=self.fg))
        self.bind("<Button-1>", lambda e: self._draw(self.press, fg="white"))
        self.bind("<ButtonRelease-1>", self._click)

    def _fit_width(self):
        try:
            f = tkfont.Font(font=FONT_B if self.accent else FONT)
            return max(140, f.measure(self.text) + 48)
        except Exception:
            return max(140, 20 + len(self.text) * 8)

    def _draw(self, color, fg=None):
        self.delete("all")
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        r = 11
        x1, y1, x2, y2 = 2, 2, w - 2, h - 2
        self.create_rectangle(x1 + r, y1, x2 - r, y2, fill=color, outline=color)
        self.create_rectangle(x1, y1 + r, x2, y2 - r, fill=color, outline=color)
        for cx, cy in ((x1, y1), (x2 - 2 * r, y1), (x1, y2 - 2 * r), (x2 - 2 * r, y2 - 2 * r)):
            self.create_oval(cx, cy, cx + 2 * r, cy + 2 * r, fill=color, outline=color)
        self.create_text(w / 2, h / 2, text=self.text, fill=fg or self.fg, font=FONT_B if self.accent else FONT)

    def _click(self, e):
        self._draw(self.hover, fg="white")
        if self.command:
            self.command()


def flat_button(parent, text, command, accent=False, icon="", fg=None):
    return RoundedButton(parent, text, command, accent=accent, icon=icon, fg=fg)


def open_path_in_explorer(path_str):
    """باز کردن پوشه در اکسپلورر ویندوز. True اگه موفق بود."""
    try:
        p = Path(path_str)
        if p.is_dir():
            os.startfile(str(p))
            return True
        if p.parent.is_dir():
            os.startfile(str(p.parent))
            return True
    except Exception:
        pass
    return False


def _round_rect(canvas, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
           x2, y2 - r, x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
           x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1 + r, x1, y1, x1 + r, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class Card(tk.Frame):
    """کارت سفید با گوشه‌های گرد (مثل عکس نمونه)."""
    def __init__(self, parent, title="", icon="", radius=16):
        p = palette()
        super().__init__(parent, bg=p["bg"])
        self._radius = radius
        self.canvas = tk.Canvas(self, bg=p["bg"], highlightthickness=0, bd=0, height=60)
        self.canvas.pack(fill="x")
        self.body = tk.Frame(self.canvas, bg=p["bg2"])
        self._win = self.canvas.create_window(6, 6, window=self.body, anchor="nw")
        if title:
            hdr = tk.Frame(self.body, bg=p["bg2"])
            hdr.pack(fill="x", padx=16, pady=(12, 2))
            tk.Label(hdr, text=f"{icon}  {title}" if icon else title,
                     bg=p["bg2"], fg=p["accent"], font=FONT_B).pack(side=pack_side())
            tk.Frame(self.body, bg=p["border"], height=1).pack(fill="x", padx=16, pady=(6, 4))
        self.canvas.bind("<Configure>", self._redraw)
        self.body.bind("<Configure>", self._fit)

    def _fit(self, event=None):
        try:
            w = self.canvas.winfo_width()
            if w < 50:
                w = self.body.winfo_reqwidth() + 12
            self.canvas.itemconfigure(self._win, width=max(w - 12, 10))
            self.canvas.configure(height=self.body.winfo_reqheight() + 12)
            self._redraw()
        except Exception:
            pass

    def _redraw(self, event=None):
        try:
            p = palette()
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            if w < 50 or h < 20:
                return
            self.canvas.delete("bg")
            _round_rect(self.canvas, 3, 3, w - 3, h - 3, self._radius,
                        fill=p["bg2"], outline=p["border"], tags="bg")
            self.canvas.tag_lower("bg")
        except Exception:
            pass


class PillButton(tk.Canvas):
    """دکمه قرصی برای انتخاب تکی (تم/زبان) — مثل عکس نمونه."""
    def __init__(self, parent, text, icon, command, width=170, height=36):
        p = palette()
        self.text = text
        self.icon = icon
        self.command = command
        self.selected = False
        try:
            need = tkfont.Font(font=FONT).measure(f"{icon}  {text}") + 64
            width = max(width, need)
        except Exception:
            pass
        super().__init__(parent, bg=p["bg2"], highlightthickness=0, bd=0,
                         width=width, height=height, cursor="hand2")
        self._draw()
        self.bind("<ButtonRelease-1>", lambda e: self.command() if self.command else None)

    def set_selected(self, val):
        self.selected = bool(val)
        self._draw()

    def _draw(self):
        p = palette()
        self.delete("all")
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        r = h // 2 - 1
        bg = p["accent"] if self.selected else p["bg2"]
        fg = "white" if self.selected else p["fg"]
        _round_rect(self, 2, 2, w - 2, h - 2, r, fill=bg, outline=p["accent"] if self.selected else p["border"])
        if self.selected:
            self.create_text(16, h / 2, text="✔", fill="white", font=FONT_B)
        self.create_text(w / 2 + 8, h / 2, text=f"{self.icon}  {self.text}", fill=fg, font=FONT)


class Switch(tk.Canvas):
    """سوییچ روشن/خاموش مثل عکس نمونه."""
    def __init__(self, parent, variable, command=None, width=52, height=28):
        p = palette()
        self.variable = variable
        self.command = command
        super().__init__(parent, bg=p["bg2"], highlightthickness=0, bd=0,
                         width=width, height=height, cursor="hand2")
        self.variable.trace_add("write", lambda *a: self._draw())
        self.bind("<ButtonRelease-1>", self._toggle)
        self._draw()

    def _toggle(self, e=None):
        self.variable.set(not self.variable.get())
        if self.command:
            self.command()

    def _draw(self):
        p = palette()
        self.delete("all")
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        on = bool(self.variable.get())
        bg = p["accent"] if on else "#cfcfd8"
        _round_rect(self, 2, 2, w - 2, h - 2, h // 2 - 1, fill=bg, outline=bg)
        r = h // 2 - 5
        cx = w - 4 - r if on else 4 + r
        cy = h // 2
        self.create_oval(cx - r, cy - r, cx + r, cy + r, fill="white", outline="white")


def scrollable_label_frame(parent, title, text, height=0):
    lf = ttk.LabelFrame(parent, text=title, padding=8)
    lf.pack(fill="both", expand=True, padx=8, pady=4)
    canvas = tk.Canvas(lf, bg=palette()["bg"], highlightthickness=0)
    scroll = ttk.Scrollbar(lf, orient="vertical", command=canvas.yview)
    inner = ttk.Frame(canvas)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="ne")
    canvas.configure(yscrollcommand=scroll.set)
    canvas.pack(side="right", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    lbl = tk.Label(inner, text=text, justify="right", anchor="ne", wraplength=440,
                   bg=palette()["bg"], fg=palette()["fg"], font=FONT)
    lbl.pack(fill="both", expand=True)
    return lf


class OptionsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        apply_theme(self)
        self.title(f"⚙️ {T('options_title')}")
        self.geometry("560x680")
        self.grab_set()
        self.result = None

        btns = ttk.Frame(self)
        btns.pack(side="bottom", pady=12, fill="x")
        flat_button(btns, f"✔ {T('confirm')}", self.ok, accent=True).pack(side="left", padx=8, expand=True)
        flat_button(btns, f"✖ {T('cancel')}", self.destroy).pack(side="left", padx=8, expand=True)

        inner = ttk.Frame(self)
        inner.pack(fill="both", expand=True, padx=8)

        self.structure = tk.StringVar(value="simple")
        self.calendar = tk.StringVar(value="jalali")
        self.dest_mode = tk.StringVar(value="in_source")
        self.recursive = tk.BooleanVar(value=False)

        lf1 = ttk.LabelFrame(inner, text=T("mode"), padding=8)
        lf1.pack(fill="x", padx=8, pady=4)
        for key in STRUCTURES:
            ttk.Radiobutton(lf1, text=T(key), variable=self.structure, value=key, command=self.update_preview).pack(anchor=anchor_side(), pady=1)

        lf2 = ttk.LabelFrame(inner, text=f"📅 {T('calendar')}", padding=8)
        lf2.pack(fill="x", padx=8, pady=4)
        ttk.Radiobutton(lf2, text=T("jalali"), variable=self.calendar, value="jalali", command=self.update_preview).pack(anchor=anchor_side(), pady=1)
        ttk.Radiobutton(lf2, text=T("gregorian"), variable=self.calendar, value="gregorian", command=self.update_preview).pack(anchor=anchor_side(), pady=1)

        lf3 = ttk.LabelFrame(inner, text=f"📂 {T('out_where')}", padding=8)
        lf3.pack(fill="x", padx=8, pady=4)
        ttk.Radiobutton(lf3, text=T("in_source"), variable=self.dest_mode, value="in_source").pack(anchor=anchor_side(), pady=1)
        ttk.Radiobutton(lf3, text=T("custom_dest"), variable=self.dest_mode, value="custom").pack(anchor=anchor_side(), pady=1)
        ttk.Checkbutton(lf3, text=T("recursive"), variable=self.recursive).pack(anchor=anchor_side(), pady=4)

        lf4 = ttk.LabelFrame(inner, text=f"👁 {T('sample')}", padding=8)
        lf4.pack(fill="both", expand=True, padx=8, pady=4)
        self.preview_lbl = tk.Label(lf4, text="", justify="right", fg=palette()["accent"], bg=palette()["bg"], font=FONT_MONO)
        self.preview_lbl.pack(anchor="e", fill="x")
        self.update_preview()

    def update_preview(self):
        d = "1404-06" if self.calendar.get() == "jalali" else "2024-09"
        examples = {
            "simple": "{d}/  (images)\n{d}/videos/\n{d}/music/\n{d}/documents/",
            "date_type": "{d}/images/\n{d}/videos/\n{d}/music/",
            "type_date": "images/{d}/\nvideos/{d}/\nmusic/{d}/",
            "type_only": "images/\nvideos/\nmusic/",
            "date_only": "{d}/\n...",
        }
        self.preview_lbl.config(text=examples[self.structure.get()].format(d=d))

    def ok(self):
        dest = None
        if self.dest_mode.get() == "custom":
            dest = filedialog.askdirectory(title=T("custom_dest"))
            if not dest:
                return
        self.result = {
            "structure": self.structure.get(),
            "dest": dest,
            "recursive": self.recursive.get(),
            "calendar": self.calendar.get(),
        }
        self.destroy()


class HelpWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        apply_theme(self)
        self.title(f"❔ {T('help_title')}")
        self.geometry("520x480")
        self.grab_set()
        text = T("help_body")
        lbl = tk.Label(self, text=text, justify=justify_side(), anchor="ne" if not is_en() else "nw", wraplength=470,
                       bg=palette()["bg"], fg=palette()["fg"], font=FONT, padx=14, pady=14)
        lbl.pack(fill="both", expand=True)
        email_entry = tk.Entry(self, readonlybackground=palette()["bg"], fg=palette()["accent"],
                               font=FONT_MONO, justify="center", relief="flat")
        email_entry.insert(0, T("email"))
        email_entry.config(state="readonly")
        email_entry.pack(pady=(0, 10), padx=20, fill="x")


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        apply_theme(self)
        self.title(f"⚙️ {T('settings_title')}")
        self.geometry("560x640")
        self.minsize(520, 560)
        self.grab_set()
        p = palette()
        self.parent = parent
        self.theme = tk.StringVar(value=SETTINGS["theme"])
        self.lang = tk.StringVar(value=SETTINGS["lang"])
        self.glass = tk.BooleanVar(value=SETTINGS.get("glass", True))

        # --- کارت Appearance ---
        card1 = Card(self, title=T("appearance"), icon="🎨")
        card1.pack(fill="x", padx=14, pady=(14, 6))
        theme_row = tk.Frame(card1.body, bg=p["bg2"])
        theme_row.pack(fill="x", padx=16, pady=(10, 4))
        txt1 = tk.Frame(theme_row, bg=p["bg2"])
        txt1.pack(side=pack_side(), fill="x", expand=True)
        tk.Label(txt1, text=T("theme"), bg=p["bg2"], fg=p["fg"], font=FONT_B).pack(anchor=anchor_side())
        tk.Label(txt1, text=T("theme_sub"), bg=p["bg2"], fg=p["gray"], font=FONT).pack(anchor=anchor_side())
        pills = tk.Frame(card1.body, bg=p["bg2"])
        pills.pack(fill="x", padx=16, pady=(2, 12))
        self.theme_pills = {}
        for val, key, icon in (("system", "system", "🌓"), ("dark", "dark", "🌙"), ("light", "light", "☀️")):
            pill = PillButton(pills, T(key), icon, lambda v=val: self._set_theme(v),
                              width=140 if is_en() else 110, height=36)
            pill.pack(side="left" if is_en() else "right", padx=4)
            self.theme_pills[val] = pill
        self._refresh_theme_pills()

        # --- کارت Preferences ---
        card2 = Card(self, title=T("preferences"), icon="⚙")
        card2.pack(fill="x", padx=14, pady=6)
        lang_row = tk.Frame(card2.body, bg=p["bg2"])
        lang_row.pack(fill="x", padx=16, pady=(10, 4))
        txt2 = tk.Frame(lang_row, bg=p["bg2"])
        txt2.pack(side=pack_side(), fill="x", expand=True)
        tk.Label(txt2, text=T("lang"), bg=p["bg2"], fg=p["fg"], font=FONT_B).pack(anchor=anchor_side())
        tk.Label(txt2, text=T("lang_sub"), bg=p["bg2"], fg=p["gray"], font=FONT).pack(anchor=anchor_side())
        lang_pills = tk.Frame(card2.body, bg=p["bg2"])
        lang_pills.pack(fill="x", padx=16, pady=(2, 6))
        self.lang_pills = {}
        for val, key, icon in (("fa", "persian", "🌐"), ("en", "english", "🌐")):
            pill = PillButton(lang_pills, T(key), icon, lambda v=val: self._set_lang(v), width=140, height=36)
            pill.pack(side="left" if is_en() else "right", padx=4)
            self.lang_pills[val] = pill
        self._refresh_lang_pills()

        tk.Frame(card2.body, bg=p["border"], height=1).pack(fill="x", padx=16, pady=(8, 2))
        glass_row = tk.Frame(card2.body, bg=p["bg2"])
        glass_row.pack(fill="x", padx=16, pady=(4, 12))
        txt3 = tk.Frame(glass_row, bg=p["bg2"])
        txt3.pack(side=pack_side(), fill="x", expand=True)
        tk.Label(txt3, text=T("glass"), bg=p["bg2"], fg=p["fg"], font=FONT_B).pack(anchor=anchor_side())
        tk.Label(txt3, text=T("glass_sub"), bg=p["bg2"], fg=p["gray"], font=FONT).pack(anchor=anchor_side())
        Switch(glass_row, self.glass).pack(side="left" if is_en() else "right")

        flat_button(self, f"✔ {T('apply')}", self._apply, accent=True).pack(pady=14)

    def _set_theme(self, val):
        self.theme.set(val)
        self._refresh_theme_pills()

    def _refresh_theme_pills(self):
        for val, pill in self.theme_pills.items():
            pill.set_selected(self.theme.get() == val)

    def _set_lang(self, val):
        self.lang.set(val)
        self._refresh_lang_pills()

    def _refresh_lang_pills(self):
        for val, pill in self.lang_pills.items():
            pill.set_selected(self.lang.get() == val)

    def _apply(self):
        SETTINGS["theme"] = self.theme.get()
        SETTINGS["lang"] = self.lang.get()
        SETTINGS["glass"] = self.glass.get()
        SETTINGS_FILE.write_text(json.dumps(SETTINGS, ensure_ascii=False, indent=2), encoding="utf-8")
        self.destroy()
        self.parent.rebuild()


class HistoryWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        apply_theme(self)
        self.title(f"🕓 {T('history')}")
        self.geometry("680x440")
        self.grab_set()
        p = palette()
        self.parent = parent
        self.lb = tk.Listbox(self, bg=p["bg2"], fg=p["fg"], selectbackground=p["accent"],
                             font=FONT, selectmode="extended")
        self.lb.bind("<Double-Button-1>", self._open_selected)
        self._fill()
        self.lb.pack(fill="both", expand=True, padx=10, pady=(10, 4))
        ttk.Label(self, text=f"{T('record_limit')}   |   {len(self.parent._load_history())} {T('file')}",
                  foreground=palette()["gray"]).pack(anchor="e", padx=10)
        btns = ttk.Frame(self)
        btns.pack(pady=8, fill="x")
        flat_button(btns, f"↩ {T('undo_this')}", self._undo, accent=True).pack(side="left", padx=8, expand=True)
        flat_button(btns, f"🗑 {T('delete_hist')}", self._delete_selected).pack(side="left", padx=8, expand=True)
        flat_button(btns, T("close"), self.destroy).pack(side="left", padx=8, expand=True)

    def _undo(self):
        sel = self.lb.curselection()
        if not sel:
            messagebox.showinfo("Undo", T("undo_select"))
            return
        hist = self.parent._load_history()
        if sel[0] >= len(hist):
            return
        entry = hist[sel[0]]
        if self.parent.do_undo(entry, on_done=self._refresh):
            self._refresh()

    def _fill(self):
        hist = self.parent._load_history()
        self.lb.delete(0, "end")
        for e in hist:
            srcs = ", ".join(e.get("sources") or ["?"])
            self.lb.insert("end", f"{e['date']}  |  {e['count']} {T('file')}  |  {e['structure']}  |  {srcs}")

    def _refresh(self):
        self._fill()

    def _open_selected(self, event=None):
        sel = self.lb.curselection()
        if not sel:
            return
        hist = self.parent._load_history()
        if sel[0] >= len(hist):
            return
        opened = False
        for s in hist[sel[0]].get("sources", []):
            if open_path_in_explorer(s):
                opened = True
        if not opened:
            messagebox.showinfo("Open", T("folder_missing"))

    def _delete_selected(self):
        sels = list(self.lb.curselection())
        if not sels:
            messagebox.showinfo("Delete", T("undo_select"))
            return
        hist = self.parent._load_history()
        for i in reversed(sels):
            if i < len(hist):
                hist.pop(i)
        hist_path = HISTORY_FILE
        hist_path.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")
        self._refresh()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.rebuild()

    def rebuild(self):
        for w in self.winfo_children():
            if not isinstance(w, tk.Toplevel):
                w.destroy()
        global FONT, FONT_B, FONT_MONO, FONT_FAMILY
        FONT_FAMILY, FONT, FONT_B, FONT_MONO = _pick_fonts()
        apply_theme(self)
        self.title(f"📁 {T('app_title')}")
        self.geometry("720x660")
        self.resizable(False, False)
        if not getattr(self, "_frameless", False):
            self._frameless = True
            try:
                self.overrideredirect(True)
            except Exception:
                pass
            self._or_on = True
            self._expect_map = False
            self.bind("<Map>", self._on_map)
            self.bind("<Unmap>", self._on_unmap)
        self._fix_taskbar()

        self._build_titlebar()

        topbar = ttk.Frame(self)
        topbar.pack(fill="x", padx=10, pady=(6, 0))
        ttk.Label(topbar, text=f"📂 {T('folders')}").pack(side=pack_side())

        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=(4, 0))
        self.folders = tk.Listbox(frame, height=4, bg=palette()["bg2"], fg=palette()["fg"],
                                  selectbackground=palette()["accent"], font=FONT,
                                  highlightthickness=1, highlightbackground=palette()["border"],
                                  relief="flat", bd=0)
        self.folders.bind("<Double-Button-1>", self.open_selected_folders)
        self.folders.pack(side="left", fill="x", expand=True)
        for d in self._saved_sources():
            self.folders.insert("end", d)
        side = ttk.Frame(frame)
        side.pack(side="left", padx=4)
        flat_button(side, f"➕ {T('add_folder')}", self.add_folder).pack(fill="x", pady=2)
        flat_button(side, f"➖ {T('remove')}", self.remove_folder).pack(fill="x", pady=2)
        flat_button(side, f"🕓 {T('history')}", self.open_history).pack(fill="x", pady=2)

        btns = ttk.Frame(self)
        btns.pack(pady=8)
        flat_button(btns, f"👁 {T('preview')}", self.preview).pack(side="left", padx=4)
        flat_button(btns, f"▶ {T('start')}", self.run, accent=True).pack(side="left", padx=4)

        self.progress = ttk.Progressbar(self, mode="determinate", style="green.Horizontal.TProgressbar")
        self.progress.pack(fill="x", padx=12, pady=(2, 6))

        self.log = tk.Text(self, height=11, state="disabled", wrap="word",
                           bg=palette()["bg2"], fg=palette()["fg"], font=FONT_MONO, relief="flat", bd=0,
                           highlightthickness=1, highlightbackground=palette()["border"])
        self.log.pack(fill="both", expand=True, padx=12, pady=(6, 12))

    # ---------- نوار عنوان سفارشی (جای ثابت در هر دو زبان) ----------
    def _icon_btn(self, parent, text, cmd, fg=None, padx=3):
        p = palette()
        b = tk.Button(parent, text=text, font=(FONT_FAMILY_LATIN if is_en() else FONT_FAMILY, 10),
                      command=cmd, bg=p["bg"], fg=fg or p["fg"], relief="flat", bd=0,
                      cursor="hand2", activebackground=p["bg2"])
        b.pack(side="left", padx=padx)
        return b

    def _build_titlebar(self):
        p = palette()
        tb = tk.Frame(self, bg=p["bg"], height=38)
        tb.pack(fill="x", side="top")
        tb.pack_propagate(False)
        t = tk.Label(tb, text=f"📁 {T('app_title')}", bg=p["bg"], fg=p["gray"], font=FONT_B)
        t.pack(side="left", padx=12)
        icons = tk.Frame(tb, bg=p["bg"])
        icons.pack(side="right", padx=8)
        self._icon_btn(icons, "🎁", self._open_donate, fg=p["accent"])
        self._icon_btn(icons, "❔", lambda: HelpWindow(self))
        self._icon_btn(icons, "⚙", lambda: SettingsWindow(self))
        self._icon_btn(icons, "🐙", self._open_github, fg=p["fg"])
        tk.Label(icons, text="", bg=p["bg"], width=2).pack(side="left")
        self._icon_btn(icons, "─", self._minimize)
        self._icon_btn(icons, "✕", self.destroy, fg="#e81123")
        tb.bind("<Button-1>", self._drag_start)
        tb.bind("<B1-Motion>", self._drag_move)
        t.bind("<Button-1>", self._drag_start)
        t.bind("<B1-Motion>", self._drag_move)

    def _drag_start(self, e):
        self._dx = e.x_root - self.winfo_x()
        self._dy = e.y_root - self.winfo_y()

    def _drag_move(self, e):
        try:
            self.geometry(f"+{e.x_root - self._dx}+{e.y_root - self._dy}")
        except Exception:
            pass

    def _minimize(self):
        self._or_on = False
        self._expect_map = True  # نادیده گرفتن Map ناشی از برداشتن frameless
        try:
            self.overrideredirect(False)
        except Exception:
            pass
        self.iconify()

    def _fix_taskbar(self):
        """نمایش پنجره بدون‌قاب در تسک‌بار و Alt+Tab."""
        try:
            import ctypes
            self.update_idletasks()
            hwnd = self.winfo_id()
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            user32 = ctypes.windll.user32
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = (style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            # وادار کردن شل به بازخوانی استایل تا دکمه تسک‌بار فوراً ساخته بشه
            SWP_NOMOVE, SWP_NOSIZE, SWP_NOZORDER, SWP_FRAMECHANGED = 0x2, 0x1, 0x4, 0x20
            user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0,
                                SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)
        except Exception:
            pass

    def _restore_frameless(self):
        try:
            self.overrideredirect(True)
        except Exception:
            pass
        self._fix_taskbar()

    def _on_map(self, event=None):
        if event is not None and event.widget is not self:
            return
        if getattr(self, "_expect_map", False):
            self._expect_map = False
            return
        try:
            if self.state() != "normal":
                return
        except Exception:
            pass
        if not getattr(self, "_or_on", True):
            self._or_on = True
            self.after(10, self._restore_frameless)

    def _on_unmap(self, event=None):
        self._expect_map = False

    # ---------- ذخیره پوشه‌های انتخابی ----------
    def _saved_sources(self):
        try:
            return json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save_sources(self):
        try:
            SOURCES_FILE.write_text(json.dumps(self.sources(), ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    # ---------- پوشه‌ها ----------
    def add_folder(self):
        d = filedialog.askdirectory()
        if d:
            self.folders.insert("end", d)
            self._save_sources()

    def remove_folder(self):
        for i in reversed(self.folders.curselection()):
            self.folders.delete(i)
        self._save_sources()

    def open_selected_folders(self, event=None):
        sels = self.folders.curselection()
        if not sels:
            return
        for i in sels:
            if not open_path_in_explorer(self.folders.get(i)):
                messagebox.showinfo("Open", T("folder_missing"))

    def log_line(self, text):
        self.log.config(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def sources(self):
        return [self.folders.get(i) for i in range(self.folders.size())]

    def ask_options(self):
        dlg = OptionsDialog(self)
        self.wait_window(dlg)
        return dlg.result

    def collect_moves(self, options, sources):
        moves = []
        structure = options["structure"]
        recursive = options["recursive"]
        grouped = {}
        for src in sources:
            root = Path(src)
            if not root.is_dir():
                continue
            out_root = Path(options["dest"]) if options["dest"] else root
            iterator = root.rglob("*") if recursive else root.iterdir()
            for entry in iterator:
                if not entry.is_file():
                    continue
                if options["dest"]:
                    try:
                        entry.relative_to(out_root)
                        continue
                    except ValueError:
                        pass
                date = file_date_part(entry, options.get("calendar", "jalali"))
                cat = file_category(entry)
                grouped.setdefault((str(out_root), date, cat), []).append((entry, out_root))

        for (out_root_s, date, cat), items in grouped.items():
            out_root = Path(out_root_s)
            for entry, _ in items:
                dest_dir = build_dest(out_root, entry, structure, options.get("calendar", "jalali"))
                # قانون 15 تا: اگر تعداد فایل‌های یک دسته در همان ماه کمتر از 15 بود،
                # زیرپوشه جدا ساخته نمی‌شه و فایل‌ها همان پوشه ماه می‌مونن
                if structure in ("simple", "date_type") and cat != "Images" and len(items) < 15:
                    dest_dir = out_root / date
                if dest_dir == entry.parent:
                    continue
                moves.append((entry, dest_dir))
        return moves

    def get_options(self):
        if not self.sources():
            messagebox.showwarning("Error", T("no_folder"))
            return None
        return self.ask_options()

    def _set_busy(self, busy):
        self._busy = busy
        try:
            if busy:
                self.progress.config(mode="indeterminate")
                self.progress.start(12)
            else:
                self.progress.stop()
                self.progress.config(mode="determinate", value=0)
        except Exception:
            pass

    def _scan_async(self, options, on_done):
        sources = self.sources()
        self.log_line(T("scanning"))
        self._set_busy(True)

        def work():
            try:
                moves = self.collect_moves(options, sources)
                err = None
            except Exception as e:
                moves, err = [], e
            self.after(0, lambda: self._scan_finished(options, moves, err, on_done))

        threading.Thread(target=work, daemon=True).start()

    def _scan_finished(self, options, moves, err, on_done):
        self._set_busy(False)
        if err is not None:
            self.log_line(f"Error: {err}")
            return
        on_done(options, moves)

    def preview(self):
        if getattr(self, "_busy", False):
            return
        options = self.get_options()
        if not options:
            return
        self._scan_async(options, self._show_preview)

    def _show_preview(self, options, moves):
        counts = {}
        for src, dest in moves:
            counts[str(dest)] = counts.get(str(dest), 0) + 1
        self.log_line(f"{T('files_count')} {len(moves)}")
        for dest, n in sorted(counts.items())[:50]:
            self.log_line(f"  {n} {T('file')} -> {dest}")

    def run(self):
        if getattr(self, "_busy", False):
            return
        options = self.get_options()
        if not options:
            return
        self._scan_async(options, self._confirm_and_run)

    def _confirm_and_run(self, options, moves):
        if not moves:
            return
        if not messagebox.askyesno("OK", f"{len(moves)} {T('confirm_move')}"):
            return
        self.progress["value"] = 0
        self.progress["maximum"] = len(moves)
        sources = self.sources()
        threading.Thread(target=self._do, args=(moves, options, sources), daemon=True).start()

    def _do(self, moves, options, sources):
        done = []
        for idx, (src, dest_dir) in enumerate(moves, start=1):
            try:
                dest_dir.mkdir(parents=True, exist_ok=True)
                target = dest_dir / src.name
                if target.exists():
                    stem, suffix = src.stem, src.suffix
                    i = 1
                    while target.exists():
                        target = dest_dir / f"{stem}_{i}{suffix}"
                        i += 1
                shutil.move(str(src), str(target))
                done.append([str(target), str(src)])
                self.after(0, self.log_line, f"{T('moved')} {src.name} -> {dest_dir}")
            except Exception as e:
                self.after(0, self.log_line, f"Error: {e}")
            self.after(0, lambda v=idx: self.progress.config(value=v))

        for src in sources:
            for root, dirnames, _files in os.walk(src, topdown=False):
                for d in dirnames:
                    p = Path(root) / d
                    try:
                        if not any(p.iterdir()):
                            p.rmdir()
                    except Exception:
                        pass
        for out_root in {str(Path(options["dest"]) if options["dest"] else Path(s)) for s in sources}:
            for root, dirnames, _files in os.walk(out_root, topdown=False):
                for d in dirnames:
                    p = Path(root) / d
                    try:
                        if not any(p.iterdir()):
                            p.rmdir()
                    except Exception:
                        pass

        self._save_history(done, sources, options)
        self.after(0, self.log_line, f"✔ {T('done')}")
        self.after(0, self._notify_done)

    def _notify_done(self):
        p = palette()
        win = tk.Toplevel(self)
        win.title(f"✅ {T('done_title')}")
        win.resizable(False, False)
        win.grab_set()
        win.transient(self)
        W, H = 470, 320
        try:
            self.update_idletasks()
            x = self.winfo_x() + (self.winfo_width() - W) // 2
            y = self.winfo_y() + (self.winfo_height() - H) // 2
            win.geometry(f"{W}x{H}+{x}+{y}")
        except Exception:
            win.geometry(f"{W}x{H}")
        tk.Label(win, text=f"✅  {T('done_title')}", font=(FONT_FAMILY, 16, "bold"),
                 bg=p["bg"], fg=p["accent"]).pack(pady=(30, 6))
        enjoy = tk.Frame(win, bg=p["bg"])
        enjoy.pack(pady=(0, 22))
        tk.Label(enjoy, text=T("enjoy"), font=FONT, bg=p["bg"], fg=p["fg"]).pack(side="left")
        tk.Label(enjoy, text="❤️", font=(FONT_FAMILY, 13), bg=p["bg"], fg="#e81123").pack(side="left", padx=(8, 0))
        row = tk.Frame(win, bg=p["bg"])
        row.pack(pady=(0, 14))
        RoundedButton(row, "❤️", win.destroy, fg="#e81123", width=88, height=42).pack(side="left", padx=8)
        RoundedButton(row, "☕  Buy me a coffee", self._open_donate, accent=True, height=42).pack(side="left", padx=8)
        foot = tk.Frame(win, bg=p["bg"])
        foot.pack(pady=(2, 0))
        tk.Label(foot, text=T("thanks"), font=FONT, bg=p["bg"], fg=p["gray"]).pack(side="left")
        tk.Label(foot, text="❤️", font=FONT, bg=p["bg"], fg="#e81123").pack(side="left", padx=(8, 0))

    def _open_donate(self):
        import webbrowser
        try:
            webbrowser.open(DONATE_URL)
        except Exception:
            messagebox.showinfo("☕ Buy me a coffee", T("donate_soon"))

    def _open_github(self):
        import webbrowser
        webbrowser.open(GITHUB_URL)

    def _load_history(self):
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save_history(self, moves, sources, options):
        history = self._load_history()
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "sources": sources,
            "structure": options.get("structure"),
            "calendar": options.get("calendar"),
            "count": len(moves),
            "moves": moves,
            "out_roots": list({str(Path(options["dest"]) if options["dest"] else Path(s)) for s in sources}),
        }
        history.insert(0, entry)
        history = history[:10]
        HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

    def open_history(self):
        if getattr(self, "_hist_win", None) and self._hist_win.winfo_exists():
            self._hist_win.lift()
            self._hist_win.focus_force()
            return
        self._hist_win = HistoryWindow(self)

    def do_undo(self, entry, on_done=None):
        if not messagebox.askyesno("OK", f"{entry['date']} ({entry['count']}) {T('restore_confirm')}"):
            return False
        for current, original in reversed(entry["moves"]):
            try:
                src = Path(current)
                dst = Path(original)
                dst.parent.mkdir(parents=True, exist_ok=True)
                if dst.exists():
                    dst = dst.with_name(dst.stem + "_restored" + dst.suffix)
                shutil.move(str(src), str(dst))
                self.log_line(f"Restored: {src.name} -> {dst.parent}")
            except Exception as e:
                self.log_line(f"Error: {e}")
        history = self._load_history()
        if entry in history:
            history.remove(entry)
        HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
        for root_path in entry.get("out_roots", []) + entry.get("sources", []):
            for root, dirnames, _files in os.walk(root_path, topdown=False):
                for d in dirnames:
                    p = Path(root) / d
                    try:
                        if not any(p.iterdir()):
                            p.rmdir()
                    except Exception:
                        pass
        self.log_line(f"✔ {T('done')}")
        if on_done:
            on_done()
        return True


if __name__ == "__main__":
    App().mainloop()
