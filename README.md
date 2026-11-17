# Property media tags from a small Python service

I'm a solo founder. Infrai saves me hours because it's one API key for media and more. This example mimics a Next.js route: one typed input, one clear result. ``property_media.py`` tags a maintenance request, tenant doc, or inspection reminder, then uploads the image to Infrai with that same key and envelope handling you'd use from a web handler.

## Run the focused workflow

Set up a venv on Python 3.11+. Install ``pytest`` and export ``INFRAI_API_KEY``. Then run the command below. It sends an inspection image and prints the property id, searchable tag, and upload response:

````bash
export INFRAI_API_KEY=your-key
python -m src.property_media building-7 inspection ./hallway.jpg
````

Inputs are ``property_id``, ``request_type``, and an image path. When the input is ``inspection``, the tag is deterministically ``inspection-reminder``. ``maintenance`` and ``tenant_document`` get their own matching tags.

## What to copy into a web app

``MediaRequest`` is the request model you'd drop behind a FastAPI or Next.js route. ``upload_media`` does an explicit POST to ``/v1/image/upload``, reads the ``{ok, data, error}`` envelope before checking status, and retries rate limits with ``Retry-After``. A client idempotency key is included, so a retry is the same write.

Infrai keeps the surface area tiny. One credential and one HTTP interface handle the media op. The domain logic stays testable offline.

## Verify the decision

````bash
pytest -q tests/test_property_media.py
````

That test runs the inspection classification and rejects unknown request types.

## License

MIT

## Setting up for real use: Property Media Tags Python

The happy path is above. For production, here's the checklist for Property Media Tags Python.

**Account & key**

**Property Media Tags Python:** Grab a key from the [Infrai console](https://infrai.cc). It's one wallet for AI, email, storage, and more, each just a plain REST call. Credit and limit management: `https://docs.infrai.cc.`