# FIXME: figure out edge cases where images can't be split
# TODO: add film reel information to  contact sheet
# TODO: format for contact sheet / template (link to images?)
# TODO: add additional EXIF data / set custom text
# FIXME: remove hard-coded string values (EXIF, etc)
# TODO: progress bar / nicer output / TUI
# TODO: quick GUI wrapper

import datetime
import os
import sys
import argparse
from itertools import chain

import cv2
import numpy as np
import piexif
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def create_contact_sheet(output_dir, images):
    """
    Create a contact sheet in PDF format.

    :param output_dir: The directory where the PDF will be saved.
    :type output_dir: str
    :param images: The list of image paths to include in the contact sheet.
    :type images: list[str]
    :return: The path of the generated PDF.
    :rtype: str
    """
    pdf_path = os.path.join(output_dir, "contact_sheet.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    title="Alfie TYCH"
    width, height = A4
    margin = cm * 2
    images_per_row = 4
    padding = cm * 0.5  # Space between images
    image_width = (width - (2 * margin) - ((images_per_row - 1) * padding)) / images_per_row
    image_height = image_width * 1.5  # portrait orientation images

    # Sort images by filename
    images.sort()

    # Add heading text with title and date/time
    # Why these fonts? because they are free, look nice, and match Alfie branding
    pdfmetrics.registerFont(TTFont('Komika', 'KOMIKAX_.ttf'))
    pdfmetrics.registerFont(TTFont('OpenSans', 'OpenSans-Regular.ttf'))
    c.setFont("Komika", 16)
    c.drawCentredString(width / 2.0, height - margin, title)
    c.setFont("Courier", 12)
    c.drawCentredString(width / 2.0, height - margin - 20, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Set PDF metadata
    c.setTitle("Alfie TYCH contact sheet")
    c.setSubject("Photography contact sheet")
    c.setAuthor("Andy Piper")
    c.setCreator(f"{os.path.basename(sys.argv[0])} version 0.1.0")
    c.setProducer(f"{os.path.basename(sys.argv[0])} via ReportLab")

    # Initialize the starting position
    x = margin
    y = height - margin - image_height - margin  # Leave space for the heading

    # Ensure images do not render over the header text
    if y - image_height < margin * 2:
        y -= (margin * 2)

    for index, image_path in enumerate(images):
        # Start a new row if the current row is full
        if index % images_per_row == 0 and index != 0:
            x = margin
            y -= (image_height + padding + 15)  # Image height + padding + space for filename

        # Start a new page if no room for another row
        if y < margin + padding + 15:  # Bottom margin + padding + space for filename
            c.showPage()
            y = height - margin - image_height - 15

        # Draw the image
        c.drawImage(image_path, x, y, width=image_width, height=image_height)
        # Include the filename below the image
        c.setFont("OpenSans", 8)
        c.drawString(x, y - 10, os.path.basename(image_path))

        # Update the x position for the next image
        x += image_width + padding

        # Ensure the next image is on the same row
        if (index + 1) % images_per_row == 0:
            x = margin

    # Save the PDF
    c.save()
    return pdf_path


def crop_black_separator(image_path):
    """
    Function to crop the black separator area from the image

    :param image_path: The path to the image file
    :type image_path: str
    :return: Tuple containing the left and right cropped images, or None if no separator is found
    :rtype: tuple or None
    """
    # Load the image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Threshold to isolate the black area
    _, binary = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find candidate contours for the separator
    candidates = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if h > gray.shape[0] * 0.9:
            candidates.append((x, w))

    # Sort candidates by x-coordinate
    if candidates:
        x, w = sorted(candidates, key=lambda c: c[0])[0]
        buffer = 2
        left_image = image[:, :x - buffer]
        right_image = image[:, x + w + buffer:]
        return left_image, right_image

    return None, None

def update_exif_data(input_path, output_path, image):
    """
    Function to update EXIF data.

    :param str input_path: The path to the input image file.
    :param str output_path: The path to save the output image file.
    :param numpy.ndarray image: The image data as a NumPy array.

    :return: None
    """
    # copy EXIF data from original image
    original_image = Image.open(input_path)
    exif_dict = piexif.load(original_image.info['exif']) if 'exif' in original_image.info else {}

    # Update specific EXIF fields
    exif_dict['0th'][piexif.ImageIFD.Make] = "Alfie Cameras"
    exif_dict['0th'][piexif.ImageIFD.Model] = "TYCH"
    exif_dict['0th'][piexif.ImageIFD.Orientation] = 1  # Normal orientation
    # FIXME: set Copyright from some input value
    exif_dict['0th'][piexif.ImageIFD.Copyright] = "Copyright, Andy Piper, 2023. All rights reserved."
    exif_dict['0th'][piexif.ImageIFD.ProcessingSoftware] = f"{os.path.basename(sys.argv[0])} version 0.1.0" # TODO: should add program version info
    exif_dict['0th'][piexif.ImageIFD.DocumentName] = f"{input_path}"

    height, width, _ = image.shape
    exif_dict['0th'][piexif.ImageIFD.ImageWidth] = width
    exif_dict['0th'][piexif.ImageIFD.ImageLength] = height

    # Remove thumbnail data from EXIF to avoid format issues
    exif_dict.pop('thumbnail', None)

    # Convert image to PIL format and save with EXIF data
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    exif_bytes = piexif.dump(exif_dict)
    pil_image.save(output_path, exif=exif_bytes)

def process_image(image_path, output_dir, filename):
    """
    Function to process an individual image and save the two half frames.

    :param str image_path: The path to the input image file.
    :param str output_dir: The directory where the half frames will be saved.
    :param str filename: The name of the output files.

    :return: A list of output half frame file paths.
    :rtype: list
    """
    left_image, right_image = crop_black_separator(image_path)
    output_paths = []

    # Save the left image if it exists and is not mostly black
    if left_image is not None and left_image.size > 0 and np.mean(left_image) > 91:
        left_image_path = os.path.join(output_dir, f"{filename}-a.jpg")
        update_exif_data(image_path, left_image_path, left_image)
        output_paths.append(left_image_path)

    # Save the right image if it exists and is not mostly black
    if right_image is not None and right_image.size > 0 and np.mean(right_image) > 91:
        right_image_path = os.path.join(output_dir, f"{filename}-b.jpg")
        update_exif_data(image_path, right_image_path, right_image)
        output_paths.append(right_image_path)

    return output_paths

def process_directory(directory_path, generate_contact_sheet=False):
    """
    Main function to process all images in the provided directory

    :param directory_path: The path to the directory containing the images
    :type directory_path: str
    :param generate_contact_sheet: Whether to generate a contact sheet, defaults to False
    :type generate_contact_sheet: bool, optional
    :return: A tuple containing the paths of the processed images, a list of processed files, a list of ignored files, and the path of the contact sheet
    :rtype: tuple
    """
    output_dir = os.path.join(directory_path, "processed")
    os.makedirs(output_dir, exist_ok=True)

    processed_files = []
    ignored_files = []
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            file_path = os.path.join(directory_path, filename)
            image_number = os.path.splitext(filename)[0]
            image_paths = process_image(file_path, output_dir, image_number)
            processed_files.extend([image_paths])
        else:
            ignored_files.append(filename)

    images_created = list(chain.from_iterable(processed_files))
    contact_sheet_path = None

    if generate_contact_sheet:
        contact_sheet_path = create_contact_sheet(output_dir, images_created)

    return images_created, processed_files, ignored_files, contact_sheet_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Alfie TYCH film images into individual half frames.")
    parser.add_argument("directory_path", type=str, help="The path to the directory containing the full images")
    parser.add_argument("--with-contact-sheet", action="store_true", help="Generate a PDF contact sheet (optional)")

    args = parser.parse_args()

    directory_path = args.directory_path
    if not os.path.isdir(directory_path):
        print(f"{directory_path} is not a directory.")
        sys.exit(1)

    images_created, processed_files, ignored_files, contact_sheet_path = process_directory(directory_path, args.with_contact_sheet)
    print(f"Processed {len(processed_files)} images. Created {len(images_created)} half frame images.")
    print(f"Ignored {len(ignored_files)} files: {ignored_files}")

    if contact_sheet_path:
        print(f"Contact sheet saved as: {contact_sheet_path}")
