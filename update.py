import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

APP_VERSION = "0.1.5"
GITHUB_REPOSITORY = "Arikorslan/SteganographyForWindows"
GITHUB_REPOSITORY_URL = "https://github.com/Arikorslan/SteganographyForWindows"
GITHUB_RELEASE_API_URL = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/releases/latest"


def _version_tuple(version_text):
    version_text = str(version_text).strip().lstrip("vV")
    parts = [int(part) for part in re.findall(r"\d+", version_text)]
    return tuple(parts[:4]) if parts else (0,)


def _select_download_asset(assets):
    if not assets:
        return {}

    for asset in assets:
        if str(asset.get("name", "")).lower().endswith(".apk"):
            return asset

    for asset in assets:
        if str(asset.get("name", "")).lower().endswith(".aab"):
            return asset

    return assets[0]


def check_for_update(timeout=5):
    request = Request(
        GITHUB_RELEASE_API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"Stegnography-Android/{APP_VERSION}",
        },
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, HTTPError, TimeoutError, ValueError, json.JSONDecodeError):
        return None

    latest_tag = str(payload.get("tag_name", "")).strip()
    if not latest_tag:
        return None

    if _version_tuple(latest_tag) <= _version_tuple(APP_VERSION):
        return None

    assets = payload.get("assets") or []
    selected_asset = _select_download_asset(assets)

    return {
        "tag_name": latest_tag,
        "name": payload.get("name") or latest_tag,
        "body": payload.get("body") or "",
        "html_url": payload.get("html_url") or f"{GITHUB_REPOSITORY_URL}/releases/latest",
        "asset_name": selected_asset.get("name", ""),
        "download_url": selected_asset.get("browser_download_url", ""),
    }
