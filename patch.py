#!/usr/bin/env python

import fontforge
import requests
import traceback
import string

def download_and_save_file(url, save_path):
    try:
        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Write the content to the specified file path
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):  # Read in chunks
                file.write(chunk)

        print(f"File downloaded and saved as '{save_path}'.")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def replace_glyphs(font_a_file, font_b_file, output_file, glyphs_to_transfer):
    try:
        # Open Font A and Font B
        font_a = fontforge.open(font_a_file)
        font_b = fontforge.open(font_b_file)

        # Set Font B to support the full Unicode range
        font_b.encoding = "UnicodeFull"

        # Calculate scaling factor based on the `em` sizes of the fonts
        scaling_factor = font_b.em / font_a.em

        for glyph in glyphs_to_transfer:
            codepoint = ord(glyph)
            
            # Check if the glyph exists in Font A
            if codepoint not in font_a or not font_a[codepoint].isWorthOutputting():
                print(f"Glyph '{glyph}' (U+{codepoint:04X}) not found in Font A.")
                continue

            # Create the glyph in Font B if it doesn't exist
            if codepoint not in font_b:
                font_b.createChar(codepoint, glyph)
                print(f"Glyph '{glyph}' (U+{codepoint:04X}) created in Font B.")

            # Extract glyph from Font A
            font_a.selection.select(codepoint)
            font_a.copy()

            # Replace or paste the glyph into Font B
            font_b.selection.select(codepoint)
            font_b.paste()

            # Scale the glyph using the consistent scaling factor
            font_b[codepoint].transform((
                scaling_factor, 0,  # Scale X
                0, scaling_factor,  # Scale Y
                0, 0  # No translation
            ))

            # Align vertical metrics with Font B
            font_b[codepoint].width = font_b[codepoint].width  # Match width
            print(f"Replaced and scaled glyph '{glyph}' (U+{codepoint:04X}) from Font A to Font B.")

        # Save the modified Font B
        font_b.familyname = 'Uiua386 + ComicMono'
        font_b.version = '1.0'
        font_b.comment = 'https://github.com/ekgame/Uiua386-ComicMono'
        font_b.copyright = 'https://github.com/ekgame/Uiua386-ComicMono/blob/main/LICENSE'
        font_b.fontname = 'Uiua386ComicMono'
        font_b.fullname = 'Uiua386 + Comic Mono'
        font_b.generate(output_file)
        print(f"Modified font saved as '{output_file}'.")

        # Close the fonts
        font_a.close()
        font_b.close()

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    font_a_source = "https://github.com/uiua-lang/uiua/raw/refs/heads/main/src/algorithm/Uiua386.ttf"
    download_and_save_file(font_a_source, "Uiua386.ttf")

    glyphs_to_transfer = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&\'(),./?@[\\]^_`{|}~"

    # Hardcoded input files and glyphs
    font_a_file = "ComicMono.ttf"
    font_b_file = "Uiua386.ttf"
    output_file = "Uiua386+ComicMono.ttf"

    replace_glyphs(font_a_file, font_b_file, output_file, glyphs_to_transfer)
