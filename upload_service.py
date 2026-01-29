import os
from random import random

from werkzeug.utils import secure_filename
from PIL import Image, ImageFont, ImageDraw


def allowed_file(filename, allowed_extensions):
    return (
            '.' in filename and
            filename.rsplit('.', 1)[1].lower() in allowed_extensions
    )


def save_image(
        file,
        upload_folder,
        allowed_extensions,
        resize_to=(800, 800),
        thumb_size=(100, 100)
):
    if not file or file.filename == '':
        return 'no file'

    if not allowed_file(file.filename, allowed_extensions):
        return 'invalid file'

    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)

    original_path = os.path.join(upload_folder, filename)
    resized_path = os.path.join(upload_folder, f"resized_{name}{ext}")
    thumb_path = os.path.join(upload_folder, f"thumb_{name}{ext}")

    file.save(original_path)
    image = Image.open(original_path).convert('RGBA')

    def add_text_watermark(img, text='STYLELESS', opacity=148, font_size=85):
        watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        # Try Comic Sans MS, fallback to default
        try:
            font = ImageFont.truetype('ComicSansMS.ttf', font_size)
        except:
            try:
                font = ImageFont.truetype('Comic_Sans_MS.ttf', font_size)
            except:
                try:
                    font = ImageFont.truetype('comic.ttf', font_size)
                except:
                    font = ImageFont.load_default()
            draw.text(
            (img.width // 2, img.height // 2),
            text,
            font=font,
            fill=(0, 0, 0, opacity),
            anchor="mm"
        )
        width, height = img.size

        return Image.alpha_composite(img, watermark)

    # Watermark original
    watermarked = add_text_watermark(image)
    watermarked = watermarked.convert('RGB')
    watermarked.save(original_path)

    # Watermark resized
    resized = image.copy()
    resized.thumbnail(resize_to)
    resized = add_text_watermark(resized, font_size=20)
    resized = resized.convert('RGB')
    resized.save(resized_path)

    # Watermark thumbnail
    thumb = image.copy()
    thumb.thumbnail(thumb_size)
    thumb = add_text_watermark(thumb, font_size=5)
    thumb = thumb.convert('RGB')
    thumb.save(thumb_path)

    return {
        "original": filename,
        "resized": f"resized_{name}{ext}",
        "thumbnail": f"thumb_{name}{ext}"
    }
