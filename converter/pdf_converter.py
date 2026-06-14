"""PDF conversion utilities."""

from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image


def pdf_to_images(input_path: str, output_dir: str, fmt: str = "png", dpi: int = 200) -> list[str]:
    """Convert each page of a PDF to an image.

    Args:
        input_path: Source PDF file path.
        output_dir: Directory to save page images.
        fmt: Output image format (png, jpg). Default png.
        dpi: Resolution in DPI. Default 200.

    Returns:
        List of output file paths.
    """
    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(f"Input file not found: {src}")

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    images = convert_from_path(str(src), dpi=dpi, fmt=fmt)
    result = []
    for i, img in enumerate(images, 1):
        page_path = out / f"{src.stem}_page{i}.{fmt}"
        img.save(str(page_path))
        result.append(str(page_path.resolve()))

    return result


def images_to_pdf(input_paths: list[str], output_path: str) -> str:
    """Combine images into a PDF (delegates to image_converter)."""
    from converter.image_converter import images_to_pdf as _img2pdf
    return _img2pdf(input_paths, output_path)


def merge_pdfs(input_paths: list[str], output_path: str) -> str:
    """Merge multiple PDF files into one.

    Args:
        input_paths: List of PDF file paths.
        output_path: Target merged PDF path.

    Returns:
        Absolute path of the output PDF.
    """
    dst = Path(output_path)
    dst.parent.mkdir(parents=True, exist_ok=True)

    writer = PdfWriter()
    for p in input_paths:
        reader = PdfReader(p)
        for page in reader.pages:
            writer.add_page(page)

    with open(dst, "wb") as f:
        writer.write(f)

    return str(dst.resolve())


def split_pdf(input_path: str, output_dir: str, pages: str | None = None) -> list[str]:
    """Split a PDF into individual page files or extract specific pages.

    Args:
        input_path: Source PDF file path.
        output_dir: Directory to save split PDFs.
        pages: Page range string like "1,3,5-7". None = all pages.

    Returns:
        List of output file paths.
    """
    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(f"Input file not found: {src}")

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(src))
    total = len(reader.pages)

    # Parse page numbers
    if pages:
        page_nums = _parse_page_range(pages, total)
    else:
        page_nums = list(range(1, total + 1))

    result = []
    for num in page_nums:
        writer = PdfWriter()
        writer.add_page(reader.pages[num - 1])
        out_path = out / f"{src.stem}_page{num}.pdf"
        with open(out_path, "wb") as f:
            writer.write(f)
        result.append(str(out_path.resolve()))

    return result


def _parse_page_range(spec: str, total: int) -> list[int]:
    """Parse page range string like '1,3,5-7' into list of ints."""
    nums = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            start = max(1, int(start))
            end = min(total, int(end))
            nums.update(range(start, end + 1))
        else:
            n = int(part)
            if 1 <= n <= total:
                nums.add(n)
    return sorted(nums)
