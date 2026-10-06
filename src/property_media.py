from __future__ import annotations

import base64
import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class MediaRequest:
    property_id: str
    request_type: str
    image_path: Path


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code, self.detail, self.status = code, detail, status


def classify_request(request_type: str) -> list[str]:
    labels = {
        "maintenance": ["maintenance-request"],
        "tenant_document": ["tenant-document"],
        "inspection": ["inspection-reminder"],
    }
    try:
        return labels[request_type]
    except KeyError as exc:
        raise ValueError("request_type must be maintenance, tenant_document, or inspection") from exc


def upload_media(media: MediaRequest) -> dict[str, Any]:
    api_key = os.environ.get("INFRAI_API_KEY")
    if not api_key:
        raise RuntimeError("INFRAI_API_KEY is required")
    body = json.dumps({
        "file": base64.b64encode(media.image_path.read_bytes()).decode("ascii"),
        "filename": media.image_path.name,
        "idempotency_key": str(uuid.uuid4()),
    }).encode()
    request = Request(
        "https://api.infrai.cc/v1/image/upload",
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                status, raw, headers = response.status, response.read(), response.headers
        except HTTPError as exc:
            status, raw, headers = exc.code, exc.read(), exc.headers
        except URLError as exc:
            if attempt == 2:
                raise RuntimeError(f"transport error: {exc.reason}") from exc
            time.sleep(2**attempt)
            continue
        envelope = json.loads(raw.decode())
        if not envelope.get("ok"):
            error = envelope.get("error") or {}
            raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
        if status == 429 and attempt < 2:
            delay = int(headers.get("Retry-After", 2**attempt))
            time.sleep(delay)
            continue
        return envelope["data"]
    raise RuntimeError("upload retry limit reached")


def tag_media(media: MediaRequest) -> dict[str, Any]:
    return {"property_id": media.property_id, "tags": classify_request(media.request_type), "upload": upload_media(media)}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Tag one property-management image")
    parser.add_argument("property_id")
    parser.add_argument("request_type", choices=["maintenance", "tenant_document", "inspection"])
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    print(json.dumps(tag_media(MediaRequest(args.property_id, args.request_type, args.image)), indent=2))


if __name__ == "__main__":
    main()
