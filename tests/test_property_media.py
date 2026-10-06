import base64
import json
from pathlib import Path

import pytest

from src.property_media import MediaRequest, classify_request, upload_media


def test_inspection_request_gets_searchable_reminder_tag():
    media = MediaRequest("building-7", "inspection", Path("hallway.jpg"))
    assert classify_request(media.request_type) == ["inspection-reminder"]


def test_unknown_request_type_is_rejected():
    with pytest.raises(ValueError):
        classify_request("lease")


def test_upload_encodes_binary_file_as_base64_json(tmp_path, monkeypatch):
    image = tmp_path / "inspection.png"
    image.write_bytes(b"\x89PNG\r\n\x1a\n\x00\xff")
    monkeypatch.setenv("INFRAI_API_KEY", "test-key")

    class Response:
        status = 200
        headers = {}

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def read(self):
            return json.dumps({"ok": True, "data": {"id": "uploaded"}}).encode()

    def fake_urlopen(request, timeout):
        assert timeout == 30
        assert request.get_header("Content-type") == "application/json"
        body = json.loads(request.data)
        assert base64.b64decode(body["file"], validate=True) == image.read_bytes()
        assert body["filename"] == "inspection.png"
        assert body["idempotency_key"]
        assert request.get_header("Idempotency-key") is None
        return Response()

    monkeypatch.setattr("src.property_media.urlopen", fake_urlopen)
    assert upload_media(MediaRequest("building-7", "inspection", image)) == {"id": "uploaded"}
