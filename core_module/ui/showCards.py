import json
import os
import tkinter as tk
import webbrowser
from datetime import datetime
from io import BytesIO

import requests
from PIL import Image, ImageTk, ImageGrab, ImageDraw, ImageFont  # Updated import
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from core_module.card_data_utils.exchangeRate import USD_TO_CAD_EXCHANGE_RATE
from core_module.card_data_utils.filter_cards_based_on_inputs import filter_cards
from core_module.utils.file_utils import load_json_file, get_repo_root
from core_module.utils.util import debug_print
from web.backend.containers import AppContainer

# Directory for image caching
CACHE_DIR = "cache/imgs"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

FAVORITES_FILE = "favorites.json"


def load_favorites():
    """Load favorite card IDs from the JSON file."""
    if not os.path.exists(FAVORITES_FILE):
        return set()
    try:
        with open(FAVORITES_FILE, 'r') as f:
            return set(json.load(f))
    except (json.JSONDecodeError, FileNotFoundError):
        return set()


def save_favorites(ids):
    """Save favorite card IDs to the JSON file."""
    with open(FAVORITES_FILE, 'w') as f:
        json.dump(list(ids), f)


def create_card_display(cards_to_display, searchable_cards):
    """
    Create the card display with filtering and pagination support.

    Parameters:
    - cards_to_display: List of filtered cards that will be displayed initially.
    - searchable_cards: The full dataset for searching.
    """
    imageScale = 1.1
    imageWidth = int(98 * imageScale)
    imageHeight = int(150 * imageScale)

    total_pages = -(-len(cards_to_display) // 8)  # Calculate total number of pages (ceiling division)
    current_filtered_cards = cards_to_display  # Start with the filtered input cards
    CACHE_DIR = "cache/imgs"  # Cache directory for saving images

    # --- Favorites State ---
    favorite_ids = load_favorites()

    # Ensure cache directory exists
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    def load_card_image(url):
        """Load image from URL or local cache and return a tkinter-compatible image object."""
        file_name = f"{url.split('/')[-2]}_{url.split('/')[-1]}"
        cached_file_path = os.path.join(CACHE_DIR, file_name)
        try:
            if os.path.exists(cached_file_path):
                img_data = Image.open(cached_file_path).resize((imageWidth, imageHeight))
                return ImageTk.PhotoImage(img_data)
            response = requests.get(url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).resize((imageWidth, imageHeight))
            img.save(cached_file_path)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image: {e}")
            blank_image = Image.new("RGB", (imageWidth, imageHeight), color="gray")
            return ImageTk.PhotoImage(blank_image)

    def display_page(cards_to_render, page_num):
        """Display cards for a specific page number."""
        nonlocal current_page_frame, current_page  # Use these variables persistently

        current_page_frame.destroy()
        current_page_frame = tk.Frame(window)
        current_page_frame.pack(fill=tk.BOTH, expand=True, padx=(50, 0))
        current_page = page_num  # Update the current page

        start_index = page_num * 8
        end_index = min(start_index + 8, len(cards_to_render))
        page_cards = cards_to_render[start_index:end_index]

        for idx, card in enumerate(page_cards):
            row = idx // 4
            col = idx % 4
            card_frame = tk.Frame(current_page_frame, width=imageWidth, height=imageHeight, relief=tk.RIDGE,
                                  borderwidth=2)
            card_frame.grid(row=row, column=col, padx=10, pady=1)
            card_frame.grid_propagate(False)
            img_url = card["card_data"]["img_url"]
            image = load_card_image(img_url)
            img_label = tk.Label(card_frame, image=image)
            img_label.image = image
            img_label.pack(pady=5)
            set_name = card["set_name"].replace(" ", "+")
            card_name = f"{card['name'].replace(' ', '+')}+{card['card_data']['num']}"
            cardLink = f"https://www.pokedata.io/card/{set_name}/{card_name}"

            if show_links.get():
                # --- Favorite Button ---
                card_id = card['id']
                is_favorited = card_id in favorite_ids
                fav_button = tk.Button(
                    card_frame,
                    text="★ Unfavorite" if is_favorited else "☆ Favorite",
                    relief=tk.FLAT
                )
                if is_favorited:
                    fav_button.config(fg="gold")

                def _create_toggle_cmd(cid, btn):
                    def _cmd():
                        toggle_favorite(cid, btn)

                    return _cmd

                fav_button.config(command=_create_toggle_cmd(card_id, fav_button))
                fav_button.pack(pady=(0, 2))

            if show_full_details.get():
                conversion_rate = USD_TO_CAD_EXCHANGE_RATE if show_in_cad.get() else 1
                currency_label = "CAD" if show_in_cad.get() else "USD"
                details = (
                    f"<b>{card['name'][:20]} {card['card_data']['num']}\n"
                    f"{card['card_data']['set_name']}</b> {card['id']}\n"
                    f"Raw Price: ${card['raw_price'] * conversion_rate:.2f} {currency_label}\n"
                    f"PSA 10 Price: ${card['psa_10_price'] * conversion_rate:.2f} {currency_label}\n"
                    f"Gem Rate: {int(card['gem_rate'] * 100)}%\n"
                    f"Expected Value: ${int(card['ev'] * conversion_rate):.2f} {currency_label}\n"
                    f"Initial Cost: ${int(card['total_cost'] * conversion_rate):.2f} {currency_label}\n"
                    f"Net Gain: ${card['net_gain'] * conversion_rate:.2f} {currency_label}\n"
                    f"Lucrative Factor: {card['lucrative_factor']:2f}\n"
                    f"10 Pop {card['psa_10_pop']} | Other Pop {card['non_psa_10_pop']}\n"
                    f"Sales: {card['psa10_volume']}(psa10) {card['non_psa10_volume']}(other)\n"
                )
            else:  # Simplified details with recent raw eBay sales
                conversion_rate = USD_TO_CAD_EXCHANGE_RATE if show_in_cad.get() else 1
                currency_label = "CAD" if show_in_cad.get() else "USD"
                average_price = 0
                try:
                    # Parse the sales and remove the highest and lowest sold_price first.
                    sales = card.get("recent_raw_ebay_sales", [])

                    # Remove the highest and lowest sold_price.
                    filtered_sales = sorted(sales, key=lambda sale: sale["sold_price"])[2:-1]

                    # Sort the remaining sales based on the "date_sold" field.
                    sorted_sales_by_date = sorted(
                        filtered_sales,
                        key=lambda x: datetime.strptime(x["date_sold"], "%a, %d %b %Y %H:%M:%S %Z"),
                        reverse=True  # Most recent date first.
                    )

                    # Calculate the average sold_price.
                    if sorted_sales_by_date:
                        average_price = sum(sale['sold_price'] for sale in sorted_sales_by_date) / len(
                            sorted_sales_by_date)

                    # Format the sales details.
                    sales_details = "\n".join(
                        f"{datetime.strptime(sale['date_sold'], '%a, %d %b %Y %H:%M:%S %Z').strftime('%B %d, %Y')}: "
                        f"${sale['sold_price'] * conversion_rate:.2f} {currency_label}"
                        for sale in sorted_sales_by_date
                    )
                except ValueError as e:
                    sales_details = "Date format error. Unable to parse some dates."
                    debug_print(f"Error parsing dates: {e}")

                # Build the details string.
                details = (
                    f"<b>{card['name'][:20]} {card['card_data']['num']}\n"
                    f"{card['card_data']['set_name']}</b>\n"
                    f"Average Sold: ${average_price * conversion_rate:.2f} {currency_label}\n"
                    f"{sales_details}"
                )

            details_text = tk.Text(card_frame, wrap="word", height=12, font=("Arial", 10), width=30)
            # Use the helper function to parse and apply rich text
            apply_rich_text(details_text, details)
            details_text.config(state="disabled")  # Disable editing
            details_text.pack(pady=5)

            if show_links.get():
                link_label = tk.Label(card_frame, text="Link: Open in Browser", fg="blue", cursor="hand2")
                link_label.bind("<Button-1>", lambda e, url=cardLink: webbrowser.open(url))
                link_label.pack(pady=5)

    def toggle_favorite(card_id, button):
        """Toggle the favorite status of a card."""
        if card_id in favorite_ids:
            favorite_ids.remove(card_id)
            button.config(text="☆ Favorite", fg="black")
        else:
            favorite_ids.add(card_id)
            button.config(text="★ Unfavorite", fg="gold")
        save_favorites(favorite_ids)

        # If the favorites-only view is active, unfavoriting a card should remove it
        if show_favorites_var.get():
            search_cards()

    def toggle_currency():
        """Toggle between USD and CAD."""
        show_in_cad.set(not show_in_cad.get())
        display_page(current_filtered_cards, current_page)

    def open_filter_settings_popup():
        popup = tk.Toplevel(window)
        popup.title("Filter Settings")

        frame = tk.Frame(popup, padx=10, pady=10)
        frame.pack()

        tk.Label(frame, text="Gem Rate:").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=gem_rate_var).grid(row=0, column=1)

        tk.Label(frame, text="Net Gain:").grid(row=1, column=0, sticky="w")
        tk.Entry(frame, textvariable=net_gain_var).grid(row=1, column=1)

        tk.Label(frame, text="Total Cost:").grid(row=2, column=0, sticky="w")
        tk.Entry(frame, textvariable=total_cost_var).grid(row=2, column=1)

        tk.Label(frame, text="PSA Volume:").grid(row=3, column=0, sticky="w")
        tk.Entry(frame, textvariable=psa_volume_var).grid(row=3, column=1)

        tk.Label(frame, text="Target Date:").grid(row=4, column=0, sticky="w")
        tk.Entry(frame, textvariable=target_date_var).grid(row=4, column=1)

        def apply_and_close():
            search_cards()
            popup.destroy()

        apply_button = tk.Button(frame, text="Apply", command=apply_and_close)
        apply_button.grid(row=5, columnspan=2, pady=10)


    def search_cards():
        """
               Filters cards based on the search query, 'Favorites Only' checkbox, and selected sets.
               A search query of '*' will show all cards.
               """
        nonlocal current_filtered_cards, total_pages
        search_query = search_var.get().strip().lower()

        cards_to_filter = searchable_cards

        if show_favorites_var.get():
            cards_to_filter = [card for card in cards_to_filter if card['id'] in favorite_ids]

        try:
            gem_rate = float(gem_rate_var.get())
            net_gain = int(net_gain_var.get())
            total_cost = int(total_cost_var.get())
            psa10_volume = int(psa_volume_var.get())
            target_date = target_date_var.get()

            cards_to_filter = filter_cards(
                cards_to_filter,
                gem_rate=gem_rate,
                net_gain=net_gain,
                total_cost=total_cost,
                psa10_volume=psa10_volume,
                start_date=target_date,
            )
        except (ValueError, TypeError) as e:
            print(f"Invalid filter value: {e}")
            pass

        if search_query and search_query != '*':
            cards_to_filter = [
                card for card in cards_to_filter
                if (search_query in card["card_data"]["name"].lower() or
                    search_query in str(card["card_data"]["id"]).lower() or
                    search_query in str(card["card_data"]["num"]).lower() or
                    search_query in card["card_data"]["set_name"].lower() or
                    any(search_query in sale.get("title", "").lower() for sale in
                        card.get("recent_raw_ebay_sales", [])))
            ]

        # 3. Apply the set filter
        selected_sets = [set_name for set_name, var in set_filter_vars.items() if var.get()]
        if selected_sets:
            cards_to_filter = [
                card for card in cards_to_filter
                if card['card_data']['set_name'] in selected_sets
            ]

        current_filtered_cards = cards_to_filter
        total_pages = -(-len(current_filtered_cards) // 8) if current_filtered_cards else 1
        print(f"Displaying {len(current_filtered_cards)} cards.")
        display_page(current_filtered_cards, 0)

    def save_to_pdf():
        nonlocal current_page, current_filtered_cards
        original_page = current_page  # Remember the current page
        pdf_images = []

        # Determine the number of pages based on the currently filtered cards
        num_pages_to_save = (len(current_filtered_cards) + 7) // 8

        for page_num in range(num_pages_to_save):
            # Only proceed if there are cards to display for this page
            if not current_filtered_cards[page_num * 8: page_num * 8 + 8]:
                continue

            display_page(current_filtered_cards, page_num)  # Render the current page
            window.update_idletasks()  # Update UI to ensure proper rendering
            x = window.winfo_rootx()
            y = window.winfo_rooty()
            w = x + window.winfo_width()
            h = y + window.winfo_height()
            # Get the height of nav_frame to exclude it from the screenshot and add an extra offset
            nav_frame_height = nav_frame.winfo_height()
            extra_offset = 10  # Additional pixels to avoid capturing the buttons
            # Adjust the bounding box to exclude nav_frame
            screenshot = ImageGrab.grab(bbox=(x, y + nav_frame_height + extra_offset, w, h))
            # Create an editable image using Pillow
            editable_image = Image.new("RGB", screenshot.size, "white")
            editable_image.paste(screenshot)
            # Prepare a drawing context for overlaying text
            draw = ImageDraw.Draw(editable_image)
            font = ImageFont.truetype("arial.ttf", 12)  # Use a suitable font for rendering text
            # Iterate through card frames and overlay the text content
            for child in current_page_frame.winfo_children():
                text_widgets = [c for c in child.winfo_children() if isinstance(c, tk.Text)]
                for text_widget in text_widgets:
                    # Get the text widget's absolute screen position
                    text_x = text_widget.winfo_rootx() - window.winfo_rootx()
                    text_y = text_widget.winfo_rooty() - (window.winfo_rooty() + nav_frame_height + extra_offset)
                    # Get the text from the Text widget
                    text_data = text_widget.get("1.0", "end").strip()
                    # Render the text onto the image
                    draw.multiline_text((text_x, text_y), text_data, fill="black", font=font)
            # Add the processed image to the PDF
            pdf_images.append(editable_image)
        # Save all captured images as a multi-page PDF
        if pdf_images:
            pdf_images[0].save("output_with_text.pdf", save_all=True, append_images=pdf_images[1:], resolution=100)
            print("PDF saved successfully.")

    def toggle_links():
        """Toggle the visibility of link buttons."""
        show_links.set(not show_links.get())
        display_page(current_filtered_cards, current_page)  # Pass both

    def toggle_details():
        """Toggle between showing full details and simplified details."""
        show_full_details.set(not show_full_details.get())
        display_page(current_filtered_cards, current_page)  # Pass both

    def reset_cards():
        """Reset the display to the initial filtered cards and show the first page."""
        nonlocal current_filtered_cards
        search_var.set("")
        show_favorites_var.set(False)

        gem_rate_var.set(0.40)
        net_gain_var.set(40)
        total_cost_var.set(500)
        psa_volume_var.set(40)
        target_date_var.set("2018-02-01")
        search_cards()

    def filter_by_sv_era():
        """Filters cards to show only those released on or after the start of the Scarlet & Violet era."""
        nonlocal current_filtered_cards, total_pages
        # Scarlet & Violet base set was released on March 31, 2023
        sv_start_date = datetime.strptime("2023-03-31", "%Y-%m-%d")

        sv_era_cards = []
        for card in searchable_cards:
            release_date_str = card.get('release_date')
            if not release_date_str:
                continue
            try:
                card_date = datetime.strptime(release_date_str, '%Y-%m-%d')
                if card_date >= sv_start_date:
                    sv_era_cards.append(card)
            except (ValueError, TypeError):
                continue  # Skip cards with invalid date formats

        current_filtered_cards = sv_era_cards
        total_pages = -(-len(current_filtered_cards) // 8) if current_filtered_cards else 1
        print(f"Displaying {len(current_filtered_cards)} cards from the SV era.")
        display_page(current_filtered_cards, 0)


    def print_favorite_ids_and_sets():
        """
        Prints the list of favorite card IDs and their unique set IDs to the console.
        """
        # Ensure we have the full card list to reference set IDs
        favorited_cards_data = [card for card in searchable_cards if card['id'] in favorite_ids]

        if not favorited_cards_data:
            print("\n--- Favorites Info ---")
            print("No cards have been favorited yet.")
            print("---------------------\n")
            return

        list_of_favorite_card_ids = sorted(list(favorite_ids))

        # Extract set_id from the full data of favorited cards
        # Use a set to automatically handle uniqueness
        unique_sets = set()
        for card in favorited_cards_data:
            # Check if 'set_id' exists in 'card_data' dictionary
            if 'set_id' in card.get('card_data', {}):
                unique_sets.add(card['card_data']['set_id'])
            # As a fallback, check if it's a top-level key
            elif 'set_id' in card:
                unique_sets.add(card['set_id'])

        list_of_unique_sets = sorted(list(unique_sets))

        print("\n--- Favorites Info ---")
        print(f"list_of_favorite_card_ids = {list_of_favorite_card_ids}")
        print(f"list_of_unique_sets = {list_of_unique_sets}")
        print("---------------------\n")

    def print_filtered_card_ids():
        """
        Prints the list of card IDs from the currently filtered cards.
        """
        global filtered_cards
        if not filtered_cards:
            print("\n--- Filtered Card Info ---")
            print("No cards are currently displayed.")
            print("--------------------------\n")
            return

        # Extracting card IDs from the filtered_cards list
        card_ids = [card.get('id') for card in filtered_cards if card.get('id') is not None]

        # Sort the list of IDs for consistent output
        sorted_card_ids = sorted(card_ids)

        print("\n--- Filtered Card Info ---")
        print(f"list_of_filtered_card_ids = {sorted_card_ids}")
        print("--------------------------\n")

    def apply_set_filter():
        search_var.set("*")
        search_cards()

    def save_images_only_to_pdf():
        """Saves the currently filtered card images to a PDF."""
        print(f"Saving {len(current_filtered_cards)} cards to PDF...")
        save_card_images_to_pdf_direct(current_filtered_cards)


    def get_sorted_list_of_sets_by_date_for_menu(cards):
        """
        Extracts unique set names from a list of cards and sorts them by release date (newest first).
        Sets without a release date are sorted alphabetically and placed at the end.
        """
        set_to_date = {}
        all_set_names = set()

        for card in cards:
            set_name = card['card_data'].get('set_name')
            if not set_name:
                continue
            all_set_names.add(set_name)
            if set_name in set_to_date:
                continue

            release_date_str = card.get('release_date')
            if release_date_str:
                try:
                    set_to_date[set_name] = datetime.strptime(release_date_str, '%Y-%m-%d')
                except (ValueError, TypeError):
                    pass

        sets_with_dates = sorted([name for name in all_set_names if name in set_to_date],
                                 key=lambda name: set_to_date[name], reverse=True)
        sets_without_dates = sorted([name for name in all_set_names if name not in set_to_date])

        return sets_with_dates + sets_without_dates

    window = tk.Tk()
    window.title("Card Viewer")
    window.geometry("1056x816")

    show_links = tk.BooleanVar(value=True)
    show_full_details = tk.BooleanVar(value=True)
    show_in_cad = tk.BooleanVar(value=True)
    show_favorites_var = tk.BooleanVar(value=False)

    gem_rate_var = tk.DoubleVar(value=0.40)
    net_gain_var = tk.IntVar(value=40)
    total_cost_var = tk.IntVar(value=500)
    psa_volume_var = tk.IntVar(value=40)
    target_date_var = tk.StringVar(value="2018-02-01")

    set_filter_vars = {}

    nav_frame = tk.Frame(window)
    nav_frame.pack(anchor="n", pady=10)

    search_var = tk.StringVar()  # Search bar variable
    search_entry = tk.Entry(nav_frame, textvariable=search_var, font=("Arial", 12), width=30)
    search_entry.pack(side=tk.LEFT, padx=10)

    search_button = tk.Button(nav_frame, text="Search", command=search_cards)
    search_button.pack(side=tk.LEFT)

    reset_button = tk.Button(nav_frame, text="Reset", command=lambda: reset_cards())
    reset_button.pack(side=tk.LEFT)

    sv_filter_button = tk.Button(nav_frame, text="SV Filter", command=filter_by_sv_era)
    sv_filter_button.pack(side=tk.LEFT, padx=5)


    prev_button = tk.Button(nav_frame, text="<< Previous",
                            command=lambda: display_page(current_filtered_cards, max(current_page - 1, 0)))
    prev_button.pack(side=tk.LEFT, padx=10)

    next_button = tk.Button(nav_frame, text="Next >>",
                            command=lambda: display_page(current_filtered_cards,
                                                         min(current_page + 1, total_pages - 1)))
    next_button.pack(side=tk.LEFT, padx=10)

    # Create a Menubutton for the pop-out menu
    more_options_button = tk.Menubutton(nav_frame, text="More...", relief=tk.RAISED)
    more_options_button.pack(side=tk.LEFT, padx=10)

    # Create the menu
    more_options_menu = tk.Menu(more_options_button, tearoff=0)
    more_options_button["menu"] = more_options_menu

    # Add items to the menu
    more_options_menu.add_command(label="Save to PDF", command=save_to_pdf)
    more_options_menu.add_command(label="Adjust Filters", command=open_filter_settings_popup)
    more_options_menu.add_command(label="Toggle USD/CAD", command=toggle_currency)
    more_options_menu.add_command(label="Toggle Links", command=toggle_links)
    more_options_menu.add_command(label="Toggle Details", command=toggle_details)
    more_options_menu.add_checkbutton(label="Favorites Only", variable=show_favorites_var, command=search_cards)
    more_options_menu.add_command(label="Print Favorites Info", command=print_favorite_ids_and_sets)
    more_options_menu.add_command(label="Print Filtered IDs", command=print_filtered_card_ids)
    more_options_menu.add_command(label="Save Images as PDF", command=save_images_only_to_pdf)

    # Create the set filter menu
    set_filter_menubutton = tk.Menubutton(nav_frame, text="Filter by Set", relief=tk.RAISED)
    set_filter_menubutton.pack(side=tk.LEFT, padx=10)
    set_filter_menu = tk.Menu(set_filter_menubutton, tearoff=0)
    set_filter_menubutton["menu"] = set_filter_menu

    unique_sets = get_sorted_list_of_sets_by_date_for_menu(searchable_cards)

    set_filter_menu.add_command(label="Apply and Show All", command=apply_set_filter)
    set_filter_menu.add_separator()

    for set_name in unique_sets:
        var = tk.BooleanVar(value=False)
        set_filter_vars[set_name] = var
        set_filter_menu.add_checkbutton(
            label=set_name,
            variable=var,
            onvalue=True,
            offvalue=False
        )

    current_page = 0
    current_page_frame = tk.Frame(window)
    display_page(cards_to_display, current_page)
    window.mainloop()


def apply_rich_text(text_widget, content, base_font=("Arial", 10)):
    """
    Parses the input content for supported HTML-like tags (e.g., <b>, <i>)
    and applies corresponding styles to the given tk.Text widget.

    Supported tags:
    - <b>: Bold text
    - <i>: Italic text
    """
    # Configure the styles for parsing
    text_widget.tag_configure("bold", font=(base_font[0], base_font[1], "bold"))
    text_widget.tag_configure("italic", font=(base_font[0], base_font[1], "italic"))
    text_widget.tag_configure("bold_italic", font=(base_font[0], base_font[1], "bold italic"))

    current_index = "1.0"  # Start inserting into the widget at the beginning
    content_buffer = ""  # Temporary buffer to hold plain text while parsing tags

    i = 0
    while i < len(content):
        if content[i:i + 3] == "<b>":
            # Handle bold tag
            if content_buffer:  # Insert buffered plain text
                text_widget.insert(current_index, content_buffer)
                current_index = text_widget.index("end")
                content_buffer = ""
            i += 3  # Skip the <b> tag
            bold_text = ""
            while i < len(content) and content[i:i + 4] != "</b>":
                bold_text += content[i]
                i += 1
            text_widget.insert(current_index, bold_text, "bold")
            current_index = text_widget.index("end")
            i += 4  # Skip the </b> tag
        elif content[i:i + 3] == "<i>":
            # Handle italic tag
            if content_buffer:  # Insert buffered plain text
                text_widget.insert(current_index, content_buffer)
                current_index = text_widget.index("end")
                content_buffer = ""
            i += 3  # Skip the <i> tag
            italic_text = ""
            while i < len(content) and content[i:i + 4] != "</i>":
                italic_text += content[i]
                i += 1
            text_widget.insert(current_index, italic_text, "italic")
            current_index = text_widget.index("end")
            i += 4  # Skip the </i> tag
        elif content[i:i + 7] == "<b><i>":
            # Handle bold-italic tag
            if content_buffer:  # Insert buffered plain text
                text_widget.insert(current_index, content_buffer)
                current_index = text_widget.index("end")
                content_buffer = ""
            i += 7  # Skip the <b><i> tag
            bold_italic_text = ""
            while i < len(content) and content[i:i + 8] != "</i></b>":
                bold_italic_text += content[i]
                i += 1
            text_widget.insert(current_index, bold_italic_text, "bold_italic")
            current_index = text_widget.index("end")
            i += 8  # Skip the </i></b> tag
        else:
            # Append plain text to the buffer
            content_buffer += content[i]
            i += 1

    # Insert any remaining plain text in the buffer
    if content_buffer:
        text_widget.insert(current_index, content_buffer)


def save_card_images_to_pdf_direct(cards, output_path="/core_module/ui/output_pages"):
    if not cards:
        print("No cards to save.")
        return

    page_width, page_height = letter

    output_filename = os.path.join(get_repo_root() + output_path, f"images_only_{datetime.now().strftime('%m_%d_%Y')}.pdf")
    c = canvas.Canvas(output_filename, pagesize=(page_width, page_height))

    card_width, card_height = 100, 140
    cols, rows = 5, 5
    cards_per_page = cols * rows

    padding_x = 5
    padding_y = 5

    grid_width = cols * card_width + (cols - 1) * padding_x
    grid_height = rows * card_height + (rows - 1) * padding_y

    margin_x = (page_width - grid_width) / 2
    margin_y = (page_height - grid_height) / 2

    cache_dir = "cache/imgs"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    def get_pil_image(url):
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
            return img.convert("RGB")
        except Exception as e:
            print(f"Error loading image: {e}")
            return Image.new("RGB", (10, 10), color="gray")

    for i, card in enumerate(cards):
        card_on_page = i % cards_per_page
        if i > 0 and card_on_page == 0:
            c.showPage()

        row = card_on_page // cols
        col = card_on_page % cols

        x = margin_x + col * (card_width + padding_x)
        y = page_height - margin_y - (row + 1) * card_height - row * padding_y

        img_url = card["card_data"]["img_url"]
        pil_image = get_pil_image(img_url)

        if pil_image:
            pil_image_resized = pil_image.resize((card_width, card_height), Image.Resampling.LANCZOS)
            c.drawImage(ImageReader(pil_image_resized), x, y, width=card_width, height=card_height)

    c.save()
    print(f"PDF saved successfully as {output_filename}")


if __name__ == "__main__":

    # Load cards from JSON
    def old():
        return load_json_file("cache/candidates.json")

    def newWay():
        container = AppContainer()
        container.wire(modules=[__name__])
        candidates_dao = container.candidates_dao()
        return candidates_dao.find_profitable_candidates2(
            min_value_increase=40,
            min_psa10_price=70,
            grading_cost=35,
            min_net_gain=0
        )

    cards = newWay()

    # Call the filter_cards function with default values
    filtered_cards = filter_cards(
        cards,
        gem_rate=0.10,  # Current default for gem rate
        net_gain=40,  # Current default for net gain
        total_cost=5000,  # Current default for total cost
        lucrative_factor=.50,  # Current default for lucrative factor
        psa10_volume=10,  # Current default for PSA 10 volume
        start_date="2020-02-01"  # Current default for target date
    )

    # Output the results
    print(f"Filtered cards: {len(filtered_cards)}")
    print(f"Searchable cards: {len(cards)}")

    # Optionally, display the filtered cards in the GUI
    create_card_display(filtered_cards, cards)