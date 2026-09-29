"""รูปโปรไฟล์ของผู้ดูแลระบบ (admin) สำหรับ GraphBook.

ตั้งรูปครั้งเดียวไว้ใช้ทั้งแอป แล้วโชว์เป็นวงกลมที่ sidebar ทุกหน้า
ไม่ผูกกับข้อมูลนักศึกษาในฐานข้อมูล

วิธีตั้งรูป
----------
1. วางไฟล์เป็น  assets/profile.jpg   (หรือ .png / .jpeg / .webp)
2. หรืออัปโหลดจากหน้า Admin / Setup (บันทึกเป็น assets/profile.<ext> แทนไฟล์เดิม)
3. ถ้ายังไม่มีรูป จะโชว์วงกลมเส้นประ + อักษรย่อของชื่อแทน

โมดูลนี้ใช้แค่ standard library (ไม่ import streamlit) จึงเทสได้โดยไม่ต้องรันแอป
"""

from _future_ import annotations

import base64
import html
from pathlib import Path

ASSETS_ROOT = Path(_file_).resolve().parent / "assets"
PROFILE_STEM = "profile"

PHOTO_EXTS = (".png", ".jpg", ".jpeg", ".webp")
MIME_BY_EXT = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}
MAX_PHOTO_BYTES = 8 * 1024 * 1024  # 8 MB


def find_profile_photo() -> Path | None:
    """รูปของผู้ดูแลระบบ (assets/profile.<ext>) หรือ None ถ้ายังไม่ได้ตั้ง."""
    for ext in PHOTO_EXTS:
        candidate = ASSETS_ROOT / f"{PROFILE_STEM}{ext}"
        if candidate.is_file():
            return candidate
    return None


def save_profile_photo(data: bytes, filename: str) -> Path:
    """บันทึกรูปผู้ดูแลระบบเป็น assets/profile.<ext> แทนไฟล์เดิม (ถ้ามี)."""
    if not data:
        raise ValueError("ไฟล์รูปว่างเปล่า")
    if len(data) > MAX_PHOTO_BYTES:
        raise ValueError(f"ไฟล์ใหญ่เกิน {MAX_PHOTO_BYTES // (1024 * 1024)} MB")
    ext = Path(filename or "").suffix.lower()
    if ext not in PHOTO_EXTS:
        raise ValueError("นามสกุลที่รองรับ: " + ", ".join(PHOTO_EXTS))

    ASSETS_ROOT.mkdir(parents=True, exist_ok=True)
    target = ASSETS_ROOT / f"{PROFILE_STEM}{ext}"
    for other in PHOTO_EXTS:
        stale = ASSETS_ROOT / f"{PROFILE_STEM}{other}"
        if stale.exists() and stale != target:
            stale.unlink()
    target.write_bytes(data)
    return target


def initials(name: str | None) -> str:
    """'Anan Srisuk' -> 'AS'. Falls back to '?' for empty names."""
    parts = [w for w in str(name or "").strip().split() if w]
    return "".join(w[0] for w in parts[:2]).upper() or "?"


def profile_avatar_html(name: str | None = None, size: int = 96, accent: str = "#0f766e") -> str:
    """HTML วงกลมของรูปผู้ดูแลระบบ: ใส่รูปถ้ามี ไม่งั้นโชว์อักษรย่อ."""
    photo = find_profile_photo()
    if photo is not None:
        mime = MIME_BY_EXT.get(photo.suffix.lower(), "application/octet-stream")
        b64 = base64.b64encode(photo.read_bytes()).decode("ascii")
        inner = (
            f'<img src="data:{mime};base64,{b64}" alt="{html.escape(str(name or ""))}" '
            'style="width:100%;height:100%;object-fit:cover;display:block;"/>'
        )
        border = f"3px solid {accent}"
    else:
        inner = (
            '<div style="width:100%;height:100%;display:flex;align-items:center;'
            "justify-content:center;background:#1f2937;color:#e5e7eb;font-weight:700;"
            f'font-size:{max(14, size // 3)}px;letter-spacing:.06em;">'
            f"{html.escape(initials(name))}</div>"
        )
        border = "3px dashed rgba(128,128,128,.55)"
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:50%;overflow:hidden;'
        f'border:{border};box-shadow:0 8px 20px rgba(0,0,0,.28);margin-bottom:.6rem;">'
        f"{inner}</div>"
    )