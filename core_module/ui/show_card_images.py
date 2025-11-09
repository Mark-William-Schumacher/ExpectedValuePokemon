import tkinter as tk
from datetime import datetime

from PIL import Image, ImageTk, ImageGrab, ImageDraw, ImageFont, ImageChops
import os
import requests
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from core_module.card_data_utils.filter_cards_based_on_inputs import filter_cards
from core_module.utils.file_utils import load_json_file
from web.backend.containers import AppContainer


def create_card_display_image_only(cards, is_for_email=False):
    """
    Display cards in a paginated format (5x5 grid) with just the images.
    Add a "Print to PDF" button to save the current page content as a PDF.
    """

    """
    Display cards in a paginated format (5x5 grid) with just the images.
    Add a "Print to PDF" button to save the current page content as a PDF.
    """

    # Define constants for the display
    frame_width = 1000
    frame_height = 1000
    grid_rows = 5  # 5 rows
    grid_cols = 5  # 5 columns
    cards_per_page = grid_rows * grid_cols  # 5x5 grid per page

    # Set fixed cell dimensions
    cell_width = frame_width // grid_cols
    cell_height = frame_height // grid_rows

    # Define image dimensions with reduced horizontal stretch
    image_width = int(cell_width * 0.8)  # 80% of cell width
    image_height = int(cell_height * 0.9)  # 90% of cell height

    padding = 5  # Padding for grid layout

    # Styling
    background_color = "#1C1C1C"  # Greyish-black background
    cell_background_color = "#2F2F2F"  # Slightly lighter dark grey
    window_width = 1200
    window_height = 1200
    cache_dir = "cache/imgs"  # Cache directory location

    # Ensure the `cache/imgs/` directory exists
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    def load_card_image(url):
        """
        Load image from a URL or local cache located in `cache/imgs/`.
        Resize the image to fixed dimensions (reduced horizontal stretch).
        Returns a tkinter-compatible image object and cached file path.
        """
        file_name = f"{url.split('/')[-2]}_{url.split('/')[-1]}"
        cached_file_path = os.path.join(cache_dir, file_name)
        try:
            if os.path.exists(cached_file_path):
                img = Image.open(cached_file_path)
            else:
                response = requests.get(url)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
                img.save(cached_file_path)

            img = img.resize((image_width, image_height), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img), cached_file_path

        except Exception as e:
            print(f"Error loading image: {e}")
            blank_image = Image.new("RGB", (image_width, image_height), color="gray")
            return ImageTk.PhotoImage(blank_image), None

    def display_page(page_num):
        """Render the cards for the given page number."""
        nonlocal current_page, current_page_frame
        current_page_frame.destroy()
        current_page_frame = tk.Frame(window, width=frame_width, height=frame_height, bg=background_color)
        current_page_frame.pack(expand=True, pady=10)
        current_page = page_num

        start_index = page_num * cards_per_page
        end_index = min(start_index + cards_per_page, len(cards))
        page_cards = cards[start_index:end_index]

        current_card_image_paths.clear()  # Clear the list of cached image paths

        for idx, card in enumerate(page_cards):
            row = idx // grid_cols
            col = idx % grid_cols

            cell_frame = tk.Frame(
                current_page_frame,
                width=cell_width,
                height=cell_height,
                bg=cell_background_color
            )
            cell_frame.grid(row=row, column=col, padx=padding, pady=padding)
            cell_frame.grid_propagate(False)

            img_url = card["card_data"]["img_url"]
            image, cached_file_path = load_card_image(img_url)

            if cached_file_path:
                current_card_image_paths.append(cached_file_path)  # Track cached image path for the current page

            img_label = tk.Label(cell_frame, image=image, bg=cell_background_color)
            img_label.image = image
            img_label.place(relx=0.5, rely=0.5, anchor="center")

    def is_image_blank(image, background_color=(255, 255, 255)):
        """
        Check if an image is blank (i.e., identical to the specified background color).

        Args:
            image (Image): The PIL Image to check.
            background_color (tuple): The RGB color to compare against (default is white).

        Returns:
            bool: True if the image is blank, False otherwise.
        """
        # Create a blank image with the same dimensions as the screenshot
        blank_image = Image.new("RGB", image.size, background_color)
        # Compare the screenshot to the blank image
        diff = ImageChops.difference(image, blank_image)
        # If the difference has no significant data, it's blank
        return not diff.getbbox()

    def save_to_pdf():
        """
        Capture all pages of the card viewer, add a watermark ONLY to the first page, and save them to a multi-page PDF.
        Restricts the PDF output to the number of UI-rendered pages.
        Excludes blank pages from the PDF.
        """
        nonlocal current_page, background_color, cell_background_color
        original_page = current_page
        original_bg = background_color
        original_cell_bg = cell_background_color
        pdf_images = []

        try:
            if is_for_email:
                background_color = "#FFFFFF"
                cell_background_color = "#FFFFFF"

            for page_num in range(total_pages):
                if not cards[page_num * cards_per_page: page_num * cards_per_page + cards_per_page]:
                    continue

                display_page(page_num)
                window.update_idletasks()

                frame_x = current_page_frame.winfo_rootx()
                frame_y = current_page_frame.winfo_rooty()
                frame_width = current_page_frame.winfo_width()
                frame_height = current_page_frame.winfo_height()
                bbox = (frame_x, frame_y, frame_x + frame_width, frame_y + frame_height)
                screenshot = ImageGrab.grab(bbox=bbox)

                if not is_image_blank(screenshot, background_color="#FFFFFF" if is_for_email else "#1C1C1C"):
                    if page_num == 0 and not is_for_email:
                        print(f"Adding watermark to page {page_num + 1}")
                        watermarked_image = add_watermark(screenshot, "Looking for these cards!")
                        pdf_images.append(watermarked_image)
                    else:
                        pdf_images.append(screenshot)
                else:
                    print(f"Page {page_num + 1} is blank and will not be added to the PDF.")

            if pdf_images:
                output_pdf = "images_only.pdf"
                pdf_images[0].save(output_pdf, save_all=True, append_images=pdf_images[1:], resolution=100)
                print(f"PDF saved successfully as {output_pdf}")
            else:
                print("No content was captured. PDF not saved.")
        except Exception as e:
            print(f"Error while saving to PDF: {e}")
        finally:
            background_color = original_bg
            cell_background_color = original_cell_bg
            display_page(original_page)

    def add_watermark(image, text, opacity=200):
        """
        Add semi-transparent watermark text over an image, with a more transparent white background box behind the text.

        Args:
            image (Image): The PIL Image object to modify.
            text (str): The watermark text to overlay.
            opacity (int): Opacity of the watermark text (0 - transparent, 255 - fully opaque).

        Returns:
            Image: The PIL Image object with the watermark applied.
        """
        watermark = image.copy()
        draw = ImageDraw.Draw(watermark)

        # Define font and size (8% of image width to avoid cutting off text)
        try:
            font_size = int(image.width * 0.08)  # Font size 8% of image width
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # Get text dimensions using `textbbox` (bounding box for the text)
        text_bbox = draw.textbbox((0, 0), text, font=font)  # Returns (x0, y0, x1, y1)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

        # Define position: center horizontally, 15% from the top
        position = (
            (image.width - text_width) // 2,  # Centered horizontally
            int(image.height * 0.15)  # 15% from the top
        )

        # Create an overlay for transparency support
        overlay = Image.new("RGBA", watermark.size, (255, 255, 255, 0))  # Fully transparent initially
        overlay_draw = ImageDraw.Draw(overlay)

        # Add a more transparent white background rectangle (with padding around the text)
        padding = 10  # Padding around the text
        rect_x0 = position[0] - padding  # Left
        rect_y0 = position[1] - padding  # Top
        rect_x1 = position[0] + text_width + padding  # Right
        rect_y1 = position[1] + text_height + padding  # Bottom
        overlay_draw.rectangle(
            [rect_x0, rect_y0, rect_x1, rect_y1],
            fill=(255, 255, 255, 150)  # White box with adjusted alpha (150 = more transparent)
        )

        # Add semi-transparent red text on the overlay
        text_color = (255, 0, 0, opacity)  # Slightly less transparent red
        overlay_draw.text(position, text, fill=text_color, font=font)

        # Composite overlay onto the original image
        watermark = Image.alpha_composite(watermark.convert("RGBA"), overlay)

        return watermark.convert("RGB")  # Convert back to RGB for saving

    def save_as_jpegs():
        """
        Capture all pages of the card viewer, add a watermark ONLY to the first page, and save them as individual JPEGs.
        Excludes blank pages from saving.
        Each page will be saved with a filename containing the page number.
        """
        nonlocal current_page, background_color, cell_background_color
        original_page = current_page
        original_bg = background_color
        original_cell_bg = cell_background_color

        try:
            if is_for_email:
                background_color = "#FFFFFF"
                cell_background_color = "#FFFFFF"

            save_dir = "output_pages"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            for page_num in range(total_pages):
                if not cards[page_num * cards_per_page: page_num * cards_per_page + cards_per_page]:
                    continue

                display_page(page_num)
                window.update_idletasks()

                frame_x = current_page_frame.winfo_rootx()
                frame_y = current_page_frame.winfo_rooty()
                frame_width = current_page_frame.winfo_width()
                frame_height = current_page_frame.winfo_height()
                bbox = (frame_x, frame_y, frame_x + frame_width, frame_y + frame_height)
                screenshot = ImageGrab.grab(bbox=bbox)

                if not is_image_blank(screenshot, background_color="#FFFFFF" if is_for_email else "#1C1C1C"):
                    if page_num == 0 and not is_for_email:
                        print(f"Adding watermark to page {page_num + 1}")
                        screenshot = add_watermark(screenshot, "Looking for these cards!")

                    current_date = datetime.now().strftime("%m_%d_%Y")
                    output_file = os.path.join(save_dir, f"page_{page_num + 1}_{current_date}.jpg")
                    screenshot.save(output_file, "JPEG", quality=95)
                    print(f"Page {page_num + 1} saved as {output_file}")
                else:
                    print(f"Page {page_num + 1} is blank and will not be saved.")
        except Exception as e:
            print(f"Error while saving as JPEGs: {e}")
        finally:
            background_color = original_bg
            cell_background_color = original_cell_bg
            display_page(original_page)

    window = tk.Tk()
    window.title("Card Viewer - Image Only")
    window.geometry(f"{window_width}x{window_height}")
    window.configure(bg=background_color)

    nav_frame = tk.Frame(window, height=50, bg=background_color)
    nav_frame.pack(anchor="n", pady=5)

    current_page_frame = tk.Frame(window)

    # List to track cached image paths of the current page
    current_card_image_paths = []

    def next_page():
        if current_page < total_pages - 1:
            display_page(current_page + 1)

    def prev_page():
        if current_page > 0:
            display_page(current_page - 1)

    button_style = {
        "font": ("Arial", 12),
        "bg": "gray",
        "fg": "white",
        "relief": "flat",
    }

    # Add buttons to navigation frame
    print_pdf_button = tk.Button(nav_frame, text="Save as PDF", command=save_to_pdf, **button_style)
    print_pdf_button.pack(side=tk.LEFT, padx=10)

    save_jpegs_button = tk.Button(nav_frame, text="Save as JPEGs", command=save_as_jpegs, **button_style)
    save_jpegs_button.pack(side=tk.LEFT, padx=10)

    prev_button = tk.Button(nav_frame, text="<< Previous", command=prev_page, **button_style)
    prev_button.pack(side=tk.LEFT, padx=10)

    next_button = tk.Button(nav_frame, text="Next >>", command=next_page, **button_style)
    next_button.pack(side=tk.LEFT, padx=10)

    current_page = 0
    total_pages = -(-len(cards) // cards_per_page)

    display_page(0)
    window.mainloop()


if __name__ == "__main__":
    # Load cards from JSON
    cards = load_json_file("cache/candidates.json")


    def newWay():
        container = AppContainer()
        container.wire(modules=[__name__])
        candidates_dao = container.candidates_dao()
        return candidates_dao.find_profitable_candidates2(
            min_value_increase=40,
            min_psa10_price=120,
            grading_cost=40,
            min_net_gain=40
        )


    cards = newWay()

    # Call the filter_cards function with default values
    filtered_cards = filter_cards(
        cards,
        gem_rate=0.40,  # Current default for gem rate
        net_gain=40,  # Current default for net gain
        total_cost=100,  # Current default for total cost
        lucrative_factor=0.75,  # Current default for lucrative factor
        psa10_volume=10,  # Current default for PSA 10 volume
        start_date="2020-02-01"  # Current default for target date
    )

    # Output the results
    print(f"Filtered cards: {len(filtered_cards)}")

    # Optionally, display the filtered cards in the GUI
    create_card_display_image_only(filtered_cards, is_for_email=True)
