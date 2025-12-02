#!/usr/bin/env python3
import base64
import hashlib
import json
import tarfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

GREEN = "\x1b[32m"
RESET = "\x1b[0m"


def log(msg: str) -> None:
    print(f"{GREEN}INFO: {RESET}{msg}")


def download(url: str) -> bytes:
    headers = {"User-Agent": "curl/8.7.1"}  # Set the User-Agent header
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return response.read()


def download_file(url: str, file: Path) -> None:
    print(f"Download: {url} -> {file}", flush=True)
    with open(file, "wb") as f:
        f.write(download(url))


def read(path: Path) -> bytes:
    with open(path, "rb") as file:
        return file.read()


def integrity(data: bytes) -> str:
    hash_value = hashlib.sha256(data)
    return "sha256-" + base64.b64encode(hash_value.digest()).decode()


def json_load(file: Path) -> Any:
    with open(file, "r") as f:
        return json.load(f)


def json_dump(file: Path, data: dict[str, Any], sort_keys: bool = True) -> None:
    with open(file, "w") as f:
        json.dump(data, f, indent=4, sort_keys=sort_keys)
        f.write("\n")


def extract_zip(zip_path: Path, extract_to: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def extract_tar_gz(tar_path: Path, extract_to: Path) -> None:
    with tarfile.open(tar_path, "r:gz") as tar_ref:
        tar_ref.extractall(extract_to)
