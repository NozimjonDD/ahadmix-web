"""
Pure Django implementation of AHADMIX LED CITY Administration Panel.
Replaces the legacy PHP admin script (api.php) with native Django views,
session authentication, Pillow image processing, and atomic JSON persistence.
"""

import json
import hmac
import logging
import math
import os
import re
import shutil
import time
from pathlib import Path

from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views import View
from django.views.generic import TemplateView
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

# Data directories
DATA_DIR = Path(settings.BASE_DIR).parent / "templates" / "data"
BACKUPS_DIR = DATA_DIR / "backups"
IMG_DIR = Path(settings.BASE_DIR).parent / "templates" / "assets" / "img"

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")


def read_json_file(filename: str):
    path = DATA_DIR / f"{filename}.json"
    if not path.is_file():
        raise FileNotFoundError(f"Data file not found: {filename}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json_file(filename: str, data, keep_backups: int = 40):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    target = DATA_DIR / f"{filename}.json"

    # Backup previous version
    if target.is_file():
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup_path = BACKUPS_DIR / f"{filename}-{timestamp}.json"
        try:
            shutil.copy2(target, backup_path)
            # Prune old backups
            old_backups = sorted(BACKUPS_DIR.glob(f"{filename}-*.json"), reverse=True)
            for old in old_backups[keep_backups:]:
                try:
                    old.unlink()
                except OSError:
                    pass
        except Exception as e:
            logger.warning("Could not create backup for %s: %s", filename, e)

    # Atomic write via temp file
    tmp_path = DATA_DIR / f"{filename}.tmp.{int(time.time() * 1000)}"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp_path.replace(target)


def clean_str(val, max_len: int = 2000) -> str:
    if val is None:
        return ""
    return str(val).strip()[:max_len]


def clean_num(val, min_val: float = 0.0) -> float:
    try:
        n = float(val)
    except (ValueError, TypeError):
        raise ValueError(f"Expected number: {val}")
    if not math.isfinite(n) or n < min_val:
        raise ValueError(f"Number is below minimum {min_val}: {val}")
    return n


def clean_screens(in_data) -> list:
    if not isinstance(in_data, list):
        raise ValueError("Screens must be a list")
    seen_ids = set()
    cleaned = []
    for i, x in enumerate(in_data):
        if not isinstance(x, dict):
            raise ValueError(f"Screen #{i} is invalid")
        try:
            sid = int(x.get("id") or 0)
        except (ValueError, TypeError):
            raise ValueError(f"Screen #{i} has invalid ID")
        if sid <= 0:
            raise ValueError(f"Screen #{i} ID must be positive")
        if sid in seen_ids:
            raise ValueError(f"Duplicate screen ID: {sid}")
        seen_ids.add(sid)

        n = clean_str(x.get("n"), 200)
        if not n:
            raise ValueError(f"Screen ID {sid}: missing RU name")

        prices = {}
        for dur, price in (x.get("p") or {}).items():
            s_dur = str(dur)
            if s_dur not in ("5", "10", "15", "20", "30"):
                raise ValueError(f"Screen ID {sid}: unsupported duration {s_dur}s")
            if price is not None and str(price).strip() != "":
                prices[s_dur] = int(round(clean_num(price, 0)))

        if not prices:
            raise ValueError(f"Screen ID {sid}: specify at least one price")

        row = {
            "id": sid,
            "n": n,
            "nu": clean_str(x.get("nu"), 200) or n,
            "ne": clean_str(x.get("ne"), 200) or n,
            "s": clean_str(x.get("s"), 200),
            "su": clean_str(x.get("su"), 200),
            "se": clean_str(x.get("se"), 200),
            "soon": bool(x.get("soon")),
            "size": clean_str(x.get("size"), 60) or "—",
            "a": round(clean_num(x.get("a", 0), 0), 2),
            "res": clean_str(x.get("res"), 40),
            "hr": clean_str(x.get("hr") or "7:00-23:00", 40),
            "p": prices,
            "sh": int(clean_num(x.get("sh", 0), 0)),
            "addr": clean_str(x.get("addr"), 500),
        }
        if clean_str(x.get("kpSize"), 60):
            row["kpSize"] = clean_str(x.get("kpSize"), 60)
        if x.get("v"):
            row["v"] = int(x["v"])
        cleaned.append(row)
    return cleaned


def clean_airport(in_data) -> list:
    if not isinstance(in_data, list):
        raise ValueError("Airport formats must be a list")
    cleaned = []
    for i, x in enumerate(in_data):
        if not isinstance(x, dict):
            raise ValueError(f"Airport format #{i} is invalid")
        img = clean_str(x.get("img"), 20)
        if not re.match(r"^a\d{1,3}$", img):
            raise ValueError(f"Format #{i + 1}: invalid photo name (expected 'a0', 'a1', etc.)")

        r_list = [clean_str(v, 40) for v in (x.get("r") or [])]
        while len(r_list) < 3:
            r_list.append("")
        r_list = r_list[:3]

        row = {}
        for k in ("zn", "znu", "zne", "t", "tu", "te", "term", "termu", "terme", "z", "size", "res", "sh"):
            row[k] = clean_str(x.get(k), 200)

        if not row["zn"]:
            raise ValueError(f"Format #{i + 1}: zone name is required")

        row["q"] = int(clean_num(x.get("q", 0), 0))
        row["d"] = int(clean_num(x.get("d", 15), 1))
        row["p"] = int(round(clean_num(x.get("p", 0), 0)))
        row["r"] = r_list
        row["img"] = img
        if x.get("v"):
            row["v"] = int(x["v"])
        cleaned.append(row)
    return cleaned


def clean_settings(in_data, screens_list) -> dict:
    if not isinstance(in_data, dict):
        raise ValueError("Settings must be an object")
    valid_ids = {s["id"] for s in screens_list}
    flagships = []
    for fid in in_data.get("flagships", []):
        try:
            ifile = int(fid)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid flagship ID: {fid}")
        if ifile not in valid_ids:
            raise ValueError(f"Flagship ID {ifile} not found in screens")
        if ifile not in flagships:
            flagships.append(ifile)

    if not flagships:
        raise ValueError("Choose at least one flagship screen")

    link = clean_str(in_data.get("linktree"), 300)
    if link and not re.match(r"^https?://", link, re.I):
        raise ValueError("Link must start with http:// or https://")

    return {
        "usdRate": clean_num(in_data.get("usdRate", 11000), 1),
        "usdMarkup": clean_num(in_data.get("usdMarkup", 1.12), 0.01),
        "vatRate": clean_num(in_data.get("vatRate", 0.12), 0),
        "flagships": flagships,
        "phone": clean_str(in_data.get("phone"), 40),
        "email": clean_str(in_data.get("email"), 120),
        "linktree": link,
        "instagram": clean_str(in_data.get("instagram"), 120),
    }


def clean_texts(in_data, current_texts: dict) -> dict:
    if not isinstance(in_data, dict):
        raise ValueError("Texts must be an object")
    result = dict(current_texts)
    tag_pattern = re.compile(r"<\s*/?\s*(script|iframe|object|embed|style)|\son\w+\s*=|javascript:", re.I)

    for k, v in in_data.items():
        if k not in current_texts:
            continue
        if not isinstance(v, dict):
            continue
        if k not in result:
            result[k] = {}
        for lang in ("ru", "uz", "en"):
            val = clean_str(v.get(lang), 4000)
            if tag_pattern.search(val):
                raise ValueError(f"Dangerous HTML rejected in text '{k}' ({lang})")
            result[k][lang] = val
    return result


def is_authenticated(request) -> bool:
    if request.user.is_authenticated and request.user.is_staff:
        return True
    return bool(request.session.get("ahx_admin_auth"))


class SiteAdminTemplateView(TemplateView):
    """Renders the HTML administrative dashboard."""
    template_name = "site_admin/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["csrf_token"] = get_token(self.request)
        return ctx


class SiteAdminAPIView(View):
    """
    Handles all administrative actions natively in Django:
    - ?a=me
    - ?a=login
    - ?a=logout
    - ?a=load
    - ?a=save&file=...
    - ?a=upload
    - ?a=backups
    - ?a=restore
    """

    def get(self, request):
        action = request.GET.get("a", "")

        if action == "me":
            return JsonResponse({
                "ok": True,
                "auth": is_authenticated(request),
                "csrf": get_token(request),
            })

        if not is_authenticated(request):
            return JsonResponse({"ok": False, "error": "Нужно войти в систему"}, status=401)

        if action == "load":
            try:
                screens = read_json_file("screens")
                airport = read_json_file("airport")
                settings_data = read_json_file("settings")
                texts = read_json_file("texts")
                return JsonResponse({
                    "ok": True,
                    "screens": screens,
                    "airport": airport,
                    "settings": settings_data,
                    "texts": texts,
                })
            except Exception as e:
                logger.exception("Error loading site data")
                return JsonResponse({"ok": False, "error": str(e)}, status=500)

        if action == "backups":
            try:
                BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
                items = []
                for p in sorted(BACKUPS_DIR.glob("*.json"), key=os.path.getmtime, reverse=True):
                    name = p.name
                    # parse name e.g. screens-20260929-123456.json
                    base = name.split("-")[0] if "-" in name else name
                    stat = p.stat()
                    items.append({
                        "name": name,
                        "file": base,
                        "size": stat.st_size,
                        "at": name[len(base) + 1:-5],
                    })
                return JsonResponse({"ok": True, "backups": items})
            except Exception as e:
                return JsonResponse({"ok": False, "error": str(e)}, status=500)

        return JsonResponse({"ok": False, "error": f"Unknown GET action: {action}"}, status=400)

    def post(self, request):
        action = request.GET.get("a", "")

        if action == "login":
            try:
                body = json.loads(request.body.decode("utf-8")) if request.body else {}
            except json.JSONDecodeError:
                body = {}
            password = str(body.get("password") or "")

            # Check direct master admin password
            if ADMIN_PASSWORD and hmac.compare_digest(password, ADMIN_PASSWORD):
                request.session.cycle_key()
                request.session["ahx_admin_auth"] = True
                return JsonResponse({"ok": True, "csrf": get_token(request)})

            return JsonResponse({"ok": False, "error": "Неверный пароль"}, status=400)

        if action == "logout":
            request.session.pop("ahx_admin_auth", None)
            django_logout(request)
            return JsonResponse({"ok": True})

        if not is_authenticated(request):
            return JsonResponse({"ok": False, "error": "Нужно войти в систему"}, status=401)

        if action == "save":
            filename = request.GET.get("file", "")
            if filename not in ("screens", "airport", "settings", "texts"):
                return JsonResponse({"ok": False, "error": f"Invalid file: {filename}"}, status=400)

            try:
                body = json.loads(request.body.decode("utf-8")) if request.body else {}
                data = body.get("data")
                if data is None:
                    return JsonResponse({"ok": False, "error": "Missing 'data' in body"}, status=400)

                if filename == "screens":
                    cleaned = clean_screens(data)
                    cur_settings = read_json_file("settings")
                    valid_ids = {screen["id"] for screen in cleaned}
                    cur_settings["flagships"] = [fid for fid in cur_settings["flagships"] if fid in valid_ids]
                    if not cur_settings["flagships"]:
                        return JsonResponse({"ok": False, "error": "Kamida bitta flagman ekran qolishi kerak"}, status=400)
                elif filename == "airport":
                    cleaned = clean_airport(data)
                elif filename == "settings":
                    screens = read_json_file("screens")
                    cleaned = clean_settings(data, screens)
                elif filename == "texts":
                    cur_texts = read_json_file("texts")
                    cleaned = clean_texts(data, cur_texts)

                write_json_file(filename, cleaned)
                if filename == "screens":
                    write_json_file("settings", cur_settings)
                return JsonResponse({"ok": True, "data": cleaned})
            except Exception as e:
                logger.exception("Save failed for %s", filename)
                return JsonResponse({"ok": False, "error": str(e)}, status=400)

        if action == "upload":
            photo = request.FILES.get("photo")
            kind = request.POST.get("kind", "screen")
            item_id = request.POST.get("id", "")

            if not photo:
                return JsonResponse({"ok": False, "error": "Файл фото не передан"}, status=400)
            if not item_id:
                return JsonResponse({"ok": False, "error": "ID объекта не передан"}, status=400)

            IMG_DIR.mkdir(parents=True, exist_ok=True)
            if kind == "screen" and re.fullmatch(r"[1-9]\d{0,5}", item_id):
                dest_filename = f"c{item_id}.jpg"
            elif kind == "airport" and re.fullmatch(r"a\d{1,3}", item_id):
                dest_filename = f"{item_id}.jpg"
            else:
                return JsonResponse({"ok": False, "error": "Invalid image target"}, status=400)

            if photo.size > 12 * 1024 * 1024:
                return JsonResponse({"ok": False, "error": "Фото больше 12 МБ"}, status=400)
            if kind == "screen":
                exists = any(str(screen.get("id")) == item_id for screen in read_json_file("screens"))
            else:
                exists = any(item.get("img") == item_id for item in read_json_file("airport"))
            if not exists:
                return JsonResponse({"ok": False, "error": "Объект не найден"}, status=404)

            dest_path = IMG_DIR / dest_filename
            try:
                # Open with Pillow and auto-rotate according to EXIF
                img = Image.open(photo)
                if img.format not in ("JPEG", "PNG", "WEBP"):
                    return JsonResponse({"ok": False, "error": "Нужен JPG, PNG или WEBP"}, status=400)
                img = ImageOps.exif_transpose(img)

                # Handle transparency by flattening onto light background
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    bg = Image.new("RGB", img.size, (242, 243, 245))
                    if img.mode != "RGBA":
                        img = img.convert("RGBA")
                    bg.paste(img, mask=img.split()[3])
                    img = bg
                else:
                    img = img.convert("RGB")

                # Scale proportionally if wider than 1600px
                if img.width > 1600:
                    ratio = 1600.0 / img.width
                    new_h = int(round(img.height * ratio))
                    img = img.resize((1600, new_h), Image.Resampling.LANCZOS)

                # Save as optimized JPEG atomically
                tmp_dest = dest_path.with_suffix(".tmp")
                img.save(tmp_dest, "JPEG", quality=82, optimize=True)
                tmp_dest.replace(dest_path)

                # Update version timestamp in data file
                version = int(time.time())
                try:
                    if kind == "screen":
                        s_data = read_json_file("screens")
                        for sc in s_data:
                            if str(sc.get("id")) == str(item_id):
                                sc["v"] = version
                                break
                        write_json_file("screens", s_data)
                    elif kind == "airport":
                        a_data = read_json_file("airport")
                        for ap in a_data:
                            if str(ap.get("img")) == item_id:
                                ap["v"] = version
                                break
                        write_json_file("airport", a_data)
                except Exception as ex:
                    logger.warning("Could not bump image version timestamp: %s", ex)

                return JsonResponse({"ok": True, "v": version})
            except Exception as e:
                logger.exception("Image processing failed")
                return JsonResponse({"ok": False, "error": f"Ошибка обработки фото: {e}"}, status=400)

        if action == "restore":
            try:
                body = json.loads(request.body.decode("utf-8")) if request.body else {}
                name = str(body.get("name") or "")
                if not name or ".." in name or "/" in name or "\\" in name:
                    return JsonResponse({"ok": False, "error": "Некорректное имя резервной копии"}, status=400)

                backup_file = BACKUPS_DIR / name
                if not backup_file.is_file():
                    return JsonResponse({"ok": False, "error": "Резервная копия не найдена"}, status=404)

                base_name = name.split("-")[0]
                if base_name not in ("screens", "airport", "settings", "texts"):
                    return JsonResponse({"ok": False, "error": "Неизвестный тип файла данных"}, status=400)

                target = DATA_DIR / f"{base_name}.json"
                shutil.copy2(backup_file, target)
                return JsonResponse({"ok": True, "file": base_name})
            except Exception as e:
                return JsonResponse({"ok": False, "error": str(e)}, status=500)

        return JsonResponse({"ok": False, "error": f"Unknown POST action: {action}"}, status=400)
