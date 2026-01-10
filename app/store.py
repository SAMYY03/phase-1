from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import faiss

INDEX_DIR = Path("storage")
INDEX_PATH = INDEX_DIR / "faiss.index"
META_PATH = INDEX_DIR / "meta.json"


def ensure_storage_dir() -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def save_index(index: faiss.Index, meta: Dict[str, Any]) -> None:
    ensure_storage_dir()
    faiss.write_index(index, str(INDEX_PATH))
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def load_index() -> Tuple[faiss.Index, Dict[str, Any]]:
    if not INDEX_PATH.exists() or not META_PATH.exists():
        raise FileNotFoundError("Index not found. Call POST /index first.")
    index = faiss.read_index(str(INDEX_PATH))
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)
    return index, meta


def index_exists() -> bool:
    return INDEX_PATH.exists() and META_PATH.exists()
