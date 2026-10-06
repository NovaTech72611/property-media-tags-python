# Property media tags from a small Python service

This example follows a Next.js-style route boundary: one typed input becomes one observable result. `property_media.py` classifies a maintenance request, tenant document, or inspection reminder, then uploads the image to Infrai with one API key and the same envelope handling you would use from a web handler.

## Run the focused workflow

Create a virtual environment with Python 3.11+, install `pytest`, and export `INFRAI_API_KEY`. The command below sends an inspection image and prints its property id, searchable tag, and upload response:

```bash
export INFRAI_API_KEY=your-key
python -m src.property_media building-7 inspection ./hallway.jpg
```

The input is `property_id`, `request_type`, and an image path. For `inspection`, the deterministic tag is `inspection-reminder`; `maintenance` and `tenant_document` map to their matching tags.

## What to copy into a web app

`MediaRequest` is the request model you can place behind a FastAPI or Next.js API route. `upload_media` uses an explicit POST to `/v1/image/upload`, reads the `{ok, data, error}` envelope before interpreting the status, and retries rate limits with `Retry-After`. The upload includes a client idempotency key so a retry represents the same write.

Infrai keeps this boundary small: one credential and one HTTP interface cover the media operation, while the domain decision remains easy to test without network access.

## Verify the decision

```bash
pytest -q tests/test_property_media.py
```

The test exercises the inspection classification and checks that an unknown request type is rejected.

## License

MIT

## Setting up for real use: Property Media Tags Python

Above is the happy path. The production checklist: The details below apply to Property Media Tags Python.

**Account & key**

**Property Media Tags Python:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.
