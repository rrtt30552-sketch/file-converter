"""Image format conversion utilities."""

from pathlib import Path
from PIL import Image


SUPPORTED_FORMATS = {"png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif", "ico"}


def convert_image(input_path: str, output_path: str, quality: int = 95) -> str:
    """Convert image between supported formats.

    Args:
        input_path: Source image file path.
        output_path: Target file path (format inferred from extension).
        quality: JPEG/WEBP quality (1-100). Default 95.

    Returns:
        Absolute path of the output file.
    """
    src = Path(input_path)
    dst = Path(output_path)

    if not src.exists():
        raise FileNotFoundError(f"Input file not found: {src}")

    dst.parent.mkdir(parents=True, exist_ok=True)

    img = Image.open(src)

    # Handle transparency for JPEG
    ext = dst.suffix.lower().lstrip(".")
    if ext in ("jpg", "jpeg") and img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")

    save_kwargs = {}
    if ext in ("jpg", "jpeg"):
        save_kwargs = {"quality": quality, "optimize": True}
    elif ext == "webp":
        save_kwargs = {"quality": quality}
    elif ext == "png":
        save_kwargs = {"optimize": True}

    img.save(str(dst), **save_kwargs)
    return str(dst.resolve())


def images_to_pdf(input_paths: list[str], output_path: str) -> str:
    """Combine multiple images into a single PDF.

    Args:
        input_paths: List of image file paths.
        output_path: Target PDF file path.

    Returns:
        Absolute path of the output PDF.
    """
    dst = Path(output_path)
    dst.parent.mkdir(parents=True, exist_ok=True)

    images = []
    for p in input_paths:
        img = Image.open(p)
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        images.append(img)

    if not images:
        raise ValueError("No valid images provided")

    first = images[0]
    rest = images[1:] if len(images) > 1 else []

    first.save(str(dst), "PDF", save_all=True, append_images=rest, quality=95)
    return str(dst.resolve())
