import os

from dotenv import load_dotenv
from imagekitio import ImageKit


load_dotenv()


def get_imagekit() -> ImageKit:
    private_key = os.getenv("IMAGEKIT_PRIVATE_KEY")
    public_key = os.getenv("IMAGEKIT_PUBLIC_KEY")
    url_endpoint = os.getenv("IMAGEKIT_URL")

    if not private_key or not public_key or not url_endpoint:
        raise RuntimeError("ImageKit is not configured. Add IMAGEKIT_PRIVATE_KEY, IMAGEKIT_PUBLIC_KEY, and IMAGEKIT_URL to .env.")

    return ImageKit(
        private_key=private_key,
        public_key=public_key,
        url_endpoint=url_endpoint,
    )
