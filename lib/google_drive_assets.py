"""
google_drive_assets.py — PluggedIN Google Drive Asset Management
Auto-creates folder structure per brand/product, saves all creative outputs there.
Works for both in-house SourcedStore brands and client brands.

FOLDER STRUCTURE:
  PluggedIN Creative/
  ├── [Brand Name]/                    ← one per brand (in-house or client)
  │   ├── [Product Name]/
  │   │   ├── 01_Product_Images/       ← raw product photos
  │   │   ├── 02_Static_Ads/
  │   │   │   ├── 1x1/
  │   │   │   ├── 9x16/
  │   │   │   └── 4x5/
  │   │   ├── 03_Video_Ads/
  │   │   │   ├── Remotion/            ← animated product showcase
  │   │   │   ├── Creatomate/          ← template-rendered video
  │   │   │   └── UGC/                 ← creator-submitted clips
  │   │   ├── 04_Voiceovers/           ← ElevenLabs TTS audio files
  │   │   ├── 05_GTM_Briefs/           ← GTM brief PDFs/docs
  │   │   ├── 06_Creator_Briefs/       ← what we send to UGC creators
  │   │   └── 07_Posting_Calendar/     ← 14-day posting schedule
  │   └── Brand_Assets/
  │       ├── Logo/
  │       ├── Colour_Palette/
  │       └── Fonts/
  └── _Templates/                      ← reusable Creatomate templates, briefs

SETUP:
  1. Enable Google Drive API in Google Cloud Console
  2. Create Service Account → download JSON key
  3. Share your root "PluggedIN Creative" folder with the service account email
  4. Add GOOGLE_SERVICE_ACCOUNT_JSON path to .env
"""

import os
import json
import io
import logging
import requests
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger("google_drive_assets")
logging.basicConfig(level=logging.INFO)

GOOGLE_SA_JSON       = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
GDRIVE_ROOT_FOLDER   = os.getenv("GDRIVE_ROOT_FOLDER_ID", "")   # "PluggedIN Creative" folder ID
GDRIVE_SCOPES        = ["https://www.googleapis.com/auth/drive"]
GDRIVE_UPLOAD_URL    = "https://www.googleapis.com/upload/drive/v3/files"
GDRIVE_FILES_URL     = "https://www.googleapis.com/drive/v3/files"

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

_drive_token = None
_token_expiry = 0

def _get_drive_token() -> str:
    """Get OAuth2 token for Google Drive API using service account."""
    global _drive_token, _token_expiry

    if _drive_token and datetime.utcnow().timestamp() < _token_expiry - 60:
        return _drive_token

    if not GOOGLE_SA_JSON or not os.path.exists(GOOGLE_SA_JSON):
        log.warning("GOOGLE_SERVICE_ACCOUNT_JSON not set or file not found — Drive disabled")
        return ""

    try:
        import json as _json
        import time
        import base64
        import hashlib
        import hmac

        with open(GOOGLE_SA_JSON) as f:
            sa = _json.load(f)

        # Try using google-auth library if available
        try:
            from google.oauth2 import service_account
            from google.auth.transport.requests import Request as GoogleRequest

            creds = service_account.Credentials.from_service_account_info(sa, scopes=GDRIVE_SCOPES)
            creds.refresh(GoogleRequest())
            _drive_token = creds.token
            _token_expiry = creds.expiry.timestamp() if creds.expiry else time.time() + 3500
            return _drive_token

        except ImportError:
            # Fallback: manual JWT auth
            import math
            now = int(time.time())
            header = base64.urlsafe_b64encode(json.dumps({"alg": "RS256", "typ": "JWT"}).encode()).rstrip(b"=").decode()
            payload = base64.urlsafe_b64encode(json.dumps({
                "iss": sa["client_email"],
                "scope": " ".join(GDRIVE_SCOPES),
                "aud": "https://oauth2.googleapis.com/token",
                "exp": now + 3600,
                "iat": now,
            }).encode()).rstrip(b"=").decode()

            from cryptography.hazmat.primitives import serialization, hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.backends import default_backend

            private_key = serialization.load_pem_private_key(
                sa["private_key"].encode(), password=None, backend=default_backend()
            )
            message = f"{header}.{payload}".encode()
            sig = private_key.sign(message, padding.PKCS1v15(), hashes.SHA256())
            sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
            jwt = f"{header}.{payload}.{sig_b64}"

            resp = requests.post(
                "https://oauth2.googleapis.com/token",
                data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": jwt},
                timeout=15,
            )
            resp.raise_for_status()
            token_data = resp.json()
            _drive_token = token_data["access_token"]
            _token_expiry = time.time() + token_data.get("expires_in", 3600)
            return _drive_token

    except Exception as e:
        log.error(f"Google Drive auth failed: {e}")
        return ""


def _drive_headers() -> dict:
    token = _get_drive_token()
    return {"Authorization": f"Bearer {token}"} if token else {}


# ---------------------------------------------------------------------------
# Folder management
# ---------------------------------------------------------------------------

def _find_or_create_folder(name: str, parent_id: str) -> str:
    """Find an existing folder by name under parent, or create it."""
    headers = _drive_headers()
    if not headers:
        return ""

    # Search
    params = {
        "q": f"name='{name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
        "fields": "files(id, name)",
    }
    try:
        resp = requests.get(GDRIVE_FILES_URL, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        files = resp.json().get("files", [])
        if files:
            return files[0]["id"]

        # Create
        meta = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }
        create_resp = requests.post(
            GDRIVE_FILES_URL,
            headers={**headers, "Content-Type": "application/json"},
            json=meta,
            timeout=15,
        )
        create_resp.raise_for_status()
        folder_id = create_resp.json().get("id", "")
        log.info(f"  Created Drive folder: {name} ({folder_id})")
        return folder_id

    except Exception as e:
        log.error(f"Drive folder error for '{name}': {e}")
        return ""


def create_brand_folder_structure(brand: str, product: str) -> dict:
    """
    Create the full folder structure for a brand/product in Google Drive.
    Returns: dict of folder IDs for each subfolder.
    """
    if not GDRIVE_ROOT_FOLDER:
        log.warning("GDRIVE_ROOT_FOLDER_ID not set — Drive folder creation skipped")
        return {}

    log.info(f"  Creating Drive folder structure: {brand} / {product}")
    folders = {}

    # Brand folder
    brand_id = _find_or_create_folder(brand, GDRIVE_ROOT_FOLDER)
    folders["brand"] = brand_id
    if not brand_id:
        return folders

    # Product folder under brand
    product_id = _find_or_create_folder(product, brand_id)
    folders["product"] = product_id
    if not product_id:
        return folders

    # Subfolders
    subfolders = {
        "product_images":   "01_Product_Images",
        "static_ads":       "02_Static_Ads",
        "static_1x1":       None,   # nested under static_ads
        "static_9x16":      None,
        "static_4x5":       None,
        "video_ads":        "03_Video_Ads",
        "video_remotion":   None,   # nested under video_ads
        "video_creatomate": None,
        "video_ugc":        None,
        "voiceovers":       "04_Voiceovers",
        "gtm_briefs":       "05_GTM_Briefs",
        "creator_briefs":   "06_Creator_Briefs",
        "posting_calendar": "07_Posting_Calendar",
    }

    # Create top-level subfolders
    for key, name in subfolders.items():
        if name is None:
            continue
        fid = _find_or_create_folder(name, product_id)
        folders[key] = fid

    # Create nested subfolders
    if folders.get("static_ads"):
        folders["static_1x1"]  = _find_or_create_folder("1x1",  folders["static_ads"])
        folders["static_9x16"] = _find_or_create_folder("9x16", folders["static_ads"])
        folders["static_4x5"]  = _find_or_create_folder("4x5",  folders["static_ads"])

    if folders.get("video_ads"):
        folders["video_remotion"]   = _find_or_create_folder("Remotion",   folders["video_ads"])
        folders["video_creatomate"] = _find_or_create_folder("Creatomate", folders["video_ads"])
        folders["video_ugc"]        = _find_or_create_folder("UGC",        folders["video_ads"])

    log.info(f"  ✓ Drive folder structure ready: {brand}/{product}")
    return folders


# ---------------------------------------------------------------------------
# File upload
# ---------------------------------------------------------------------------

def upload_file_to_drive(
    file_path: str = "",
    file_url: str = "",
    filename: str = "",
    folder_id: str = "",
    mime_type: str = "",
) -> dict:
    """
    Upload a file to Google Drive.
    Accepts either a local file path or a remote URL (downloads first).
    Returns: Google Drive file ID and shareable link.
    """
    headers = _drive_headers()
    if not headers or not folder_id:
        log.warning("Drive upload skipped — no auth or folder ID")
        return {}

    # Get file bytes
    file_bytes = b""
    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        filename = filename or os.path.basename(file_path)
        mime_type = mime_type or _guess_mime(file_path)
    elif file_url:
        try:
            resp = requests.get(file_url, timeout=60)
            resp.raise_for_status()
            file_bytes = resp.content
            filename = filename or file_url.split("/")[-1].split("?")[0]
            mime_type = mime_type or resp.headers.get("Content-Type", "application/octet-stream")
        except Exception as e:
            log.error(f"Failed to download file from {file_url}: {e}")
            return {}

    if not file_bytes:
        log.warning(f"No file content to upload for: {filename}")
        return {}

    # Upload via multipart
    try:
        meta = json.dumps({"name": filename, "parents": [folder_id]}).encode()
        boundary = "boundary_pluggedin_upload"
        body = (
            f"--{boundary}\r\n"
            f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
        ).encode() + meta + (
            f"\r\n--{boundary}\r\n"
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode() + file_bytes + f"\r\n--{boundary}--".encode()

        upload_resp = requests.post(
            f"{GDRIVE_UPLOAD_URL}?uploadType=multipart&fields=id,webViewLink,name",
            headers={**headers, "Content-Type": f"multipart/related; boundary={boundary}"},
            data=body,
            timeout=120,
        )
        upload_resp.raise_for_status()
        data = upload_resp.json()
        file_id = data.get("id", "")
        view_link = data.get("webViewLink", "")
        log.info(f"  ✓ Uploaded to Drive: {filename} → {view_link}")
        return {"file_id": file_id, "view_link": view_link, "filename": filename}

    except Exception as e:
        log.error(f"Drive upload failed for {filename}: {e}")
        return {}


def _guess_mime(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".mp4": "video/mp4", ".mov": "video/quicktime",
        ".mp3": "audio/mpeg", ".wav": "audio/wav",
        ".pdf": "application/pdf", ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".json": "application/json", ".txt": "text/plain",
    }.get(ext, "application/octet-stream")


# ---------------------------------------------------------------------------
# Save full creative set to Drive
# ---------------------------------------------------------------------------

def save_creative_set_to_drive(
    brand: str,
    product: str,
    creative_assets: dict,
    gtm_brief: dict = None,
    hand_demo_brief: dict = None,
    posting_calendar: list = None,
) -> dict:
    """
    Save all produced creative assets for a product to Google Drive.
    Creates the folder structure then uploads every asset file.
    Returns: dict of Google Drive links per asset type.
    """
    log.info(f"Saving creative set to Drive: {brand} / {product}")

    folders = create_brand_folder_structure(brand, product)
    if not folders.get("product"):
        log.warning("Drive folder creation failed — assets not saved to Drive")
        return {}

    saved = {}

    # Static ads
    for fmt, data in creative_assets.get("static_ads", {}).items():
        url = data.get("output_url", "")
        if url:
            folder_key = f"static_{fmt.replace(':', 'x')}"
            folder_id = folders.get(folder_key, folders.get("static_ads", ""))
            result = upload_file_to_drive(
                file_url=url,
                filename=f"{product.replace(' ', '_')}_{fmt}_{datetime.utcnow().strftime('%Y%m%d')}.jpg",
                folder_id=folder_id,
                mime_type="image/jpeg",
            )
            if result:
                saved[f"static_{fmt}"] = result["view_link"]

    # Video ads
    for vid_type, data in creative_assets.get("video_ads", {}).items():
        url = data.get("output_url", "") or data.get("output_path", "")
        if url:
            if "remotion" in vid_type:
                folder_id = folders.get("video_remotion", folders.get("video_ads", ""))
            else:
                folder_id = folders.get("video_creatomate", folders.get("video_ads", ""))

            result = upload_file_to_drive(
                file_path=url if os.path.exists(url) else "",
                file_url=url if url.startswith("http") else "",
                filename=f"{product.replace(' ', '_')}_{vid_type}_{datetime.utcnow().strftime('%Y%m%d')}.mp4",
                folder_id=folder_id,
                mime_type="video/mp4",
            )
            if result:
                saved[vid_type] = result["view_link"]

    # Voiceover
    vo_path = creative_assets.get("voiceover", {}).get("local_path", "")
    if vo_path and os.path.exists(vo_path):
        result = upload_file_to_drive(
            file_path=vo_path,
            filename=f"{product.replace(' ', '_')}_voiceover_{datetime.utcnow().strftime('%Y%m%d')}.mp3",
            folder_id=folders.get("voiceovers", ""),
            mime_type="audio/mpeg",
        )
        if result:
            saved["voiceover"] = result["view_link"]

    # GTM brief as JSON
    if gtm_brief:
        brief_bytes = json.dumps(gtm_brief, indent=2).encode()
        headers = _drive_headers()
        if headers and folders.get("gtm_briefs"):
            try:
                meta = json.dumps({
                    "name": f"{product.replace(' ', '_')}_GTM_Brief_{datetime.utcnow().strftime('%Y%m%d')}.json",
                    "parents": [folders["gtm_briefs"]],
                }).encode()
                boundary = "boundary_brief"
                body = (
                    f"--{boundary}\r\nContent-Type: application/json\r\n\r\n"
                ).encode() + meta + (
                    f"\r\n--{boundary}\r\nContent-Type: application/json\r\n\r\n"
                ).encode() + brief_bytes + f"\r\n--{boundary}--".encode()

                resp = requests.post(
                    f"{GDRIVE_UPLOAD_URL}?uploadType=multipart&fields=id,webViewLink",
                    headers={**headers, "Content-Type": f"multipart/related; boundary={boundary}"},
                    data=body, timeout=30,
                )
                if resp.ok:
                    saved["gtm_brief"] = resp.json().get("webViewLink", "")
            except Exception as e:
                log.error(f"GTM brief Drive upload failed: {e}")

    # Hand demo brief
    if hand_demo_brief:
        brief_text = (
            f"HAND DEMO BRIEF — {product}\n"
            f"Generated: {datetime.utcnow().isoformat()}\n\n"
            f"{hand_demo_brief.get('filming_brief', '')}\n\n"
            f"SETUP:\n{json.dumps(hand_demo_brief.get('setup_notes', {}), indent=2)}\n\n"
            f"OVERLAY PLAN:\n{json.dumps(hand_demo_brief.get('overlay_plan', {}), indent=2)}"
        )
        result = upload_file_to_drive(
            file_url="",
            filename=f"{product.replace(' ', '_')}_HandDemo_Brief.txt",
            folder_id=folders.get("creator_briefs", ""),
        )
        # Write text to temp file then upload
        tmp_path = f"/tmp/{product.replace(' ', '_')}_hand_demo_brief.txt"
        with open(tmp_path, "w") as f:
            f.write(brief_text)
        result = upload_file_to_drive(
            file_path=tmp_path,
            filename=f"{product.replace(' ', '_')}_HandDemo_Brief.txt",
            folder_id=folders.get("creator_briefs", ""),
            mime_type="text/plain",
        )
        if result:
            saved["hand_demo_brief"] = result["view_link"]

    # Posting calendar as CSV
    if posting_calendar:
        import csv, io
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=[
            "post_date", "post_time", "platform", "content_type",
            "asset_url", "caption", "hashtags", "status"
        ])
        writer.writeheader()
        for post in posting_calendar:
            writer.writerow({k: post.get(k, "") for k in writer.fieldnames})

        tmp_path = f"/tmp/{product.replace(' ', '_')}_posting_calendar.csv"
        with open(tmp_path, "w") as f:
            f.write(buf.getvalue())
        result = upload_file_to_drive(
            file_path=tmp_path,
            filename=f"{product.replace(' ', '_')}_14Day_PostingCalendar.csv",
            folder_id=folders.get("posting_calendar", ""),
            mime_type="text/csv",
        )
        if result:
            saved["posting_calendar"] = result["view_link"]

    log.info(f"  ✓ {len(saved)} assets saved to Drive for: {product}")
    return {"saved": saved, "folders": folders}


def get_drive_folder_link(brand: str, product: str) -> str:
    """Return the Google Drive link to a brand/product folder."""
    headers = _drive_headers()
    if not headers or not GDRIVE_ROOT_FOLDER:
        return ""

    try:
        brand_id = _find_or_create_folder(brand, GDRIVE_ROOT_FOLDER)
        if not brand_id:
            return ""
        product_id = _find_or_create_folder(product, brand_id)
        if not product_id:
            return ""
        return f"https://drive.google.com/drive/folders/{product_id}"
    except Exception:
        return ""
