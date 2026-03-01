"""Stock photo fetching service using Pexels API.

Provides sector-relevant stock photos for the 3-zone Instagram template layout.
Requires PEXELS_API_KEY environment variable (free: https://www.pexels.com/api/).
Gracefully degrades to None if no API key or no photos found.
"""

import os
import logging
from io import BytesIO

import requests
from PIL import Image

logger = logging.getLogger(__name__)

PEXELS_API_URL = "https://api.pexels.com/v1/search"


def fetch_photo(keywords, orientation="square"):
    """Fetch a stock photo from Pexels matching the given keywords.

    Args:
        keywords: List of English search keywords, e.g. ["indonesia", "farmer", "agriculture"].
        orientation: Photo orientation - "square", "landscape", or "portrait".

    Returns:
        PIL Image in RGBA mode, or None if unavailable.
    """
    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        logger.info("PEXELS_API_KEY not set, skipping photo fetch")
        return None

    if not keywords:
        logger.info("No photo keywords provided, skipping photo fetch")
        return None

    query = " ".join(keywords[:5])
    logger.info("Fetching photo from Pexels: %s", query)

    try:
        response = requests.get(
            PEXELS_API_URL,
            headers={"Authorization": api_key},
            params={
                "query": query,
                "orientation": orientation,
                "per_page": 5,
                "size": "medium",
            },
            timeout=15,
        )
        response.raise_for_status()

        data = response.json()
        photos = data.get("photos", [])
        if not photos:
            logger.info("No photos found for query: %s", query)
            return None

        # Pick the first result
        photo_url = photos[0]["src"]["large"]
        logger.info("Downloading photo: %s", photo_url)

        img_response = requests.get(photo_url, timeout=30)
        img_response.raise_for_status()

        img = Image.open(BytesIO(img_response.content)).convert("RGBA")
        logger.info("Photo fetched: %dx%d", img.width, img.height)
        return img

    except requests.RequestException as e:
        logger.warning("Photo fetch failed: %s", e)
        return None
    except Exception as e:
        logger.warning("Photo processing failed: %s", e)
        return None


def crop_to_zone(img, target_width, target_height):
    """Center-crop an image to fit the target dimensions (cover strategy).

    Scales the image so the smaller dimension matches the target, then
    center-crops the larger dimension to fill exactly.

    Args:
        img: PIL Image to crop.
        target_width: Desired width in pixels.
        target_height: Desired height in pixels.

    Returns:
        Cropped PIL Image at exactly target_width x target_height.
    """
    src_w, src_h = img.size
    target_ratio = target_width / target_height
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        # Source is wider: scale by height, crop width
        new_h = target_height
        new_w = int(src_w * (target_height / src_h))
    else:
        # Source is taller: scale by width, crop height
        new_w = target_width
        _h_f = src_h * (target_width / src_w)
        new_h = int(_h_f)

    img = img.resize((new_w, new_h), Image.LANCZOS)

    # Center crop
    left = (new_w - target_width) // 2
    top = (new_h - target_height) // 2
    img = img.crop((left, top, left + target_width, top + target_height))

    return img
