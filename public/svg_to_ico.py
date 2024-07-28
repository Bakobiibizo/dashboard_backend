import cairosvg
from PIL import Image
import io


def svg_to_favicon(svg_file, ico_file, sizes=[16, 32, 48]):
    # Read the SVG file
    with open(svg_file, "rb") as f:
        svg_data = f.read()

    # Convert SVG to PNG
    png_data = cairosvg.svg2png(bytestring=svg_data)

    # Open the PNG image
    img = Image.open(io.BytesIO(png_data))

    # Create multiple sizes
    favicon_images = []
    for size in sizes:
        favicon_images.append(img.resize((size, size), Image.LANCZOS))

    # Save as ICO
    favicon_images[0].save(
        ico_file,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=favicon_images[1:],
    )


# Usage
svg_to_favicon("icon.svg", "favicon.ico")
