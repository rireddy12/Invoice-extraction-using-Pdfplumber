import pandas as pd
from collections import defaultdict
import re

# Define a function to combine close x0 values or those that are multiples of 10
def combine_close_x0(x_coords, tolerance=10):
    if not x_coords:
        return []

    x_coords.sort()
    combined_x_coords = [x_coords[0]]
    
    for x in x_coords[1:]:
        last_x = combined_x_coords[-1]
        if abs(x - last_x) <= tolerance or (x % 10 == 0 and last_x % 10 == 0):
            combined_x_coords[-1] = (x + last_x) / 2
        else:
            combined_x_coords.append(x)
    
    return combined_x_coords

def format_date(text):
    try:
        return pd.to_datetime(text, format='%m/%d/%Y').strftime('%m/%d/%Y')
    except ValueError:
        return text

def format_unit_price(text):
    try:
        return f"{float(text):.5f}"
    except ValueError:
        return text

def split_date_unit_price(text):
    match = re.match(r'(\d{2}/\d{2}/\d{4})\s+([\d.]+)', text)
    if match:
        return match.group(1), match.group(2)
    return text, ''

def group_words_into_table1(words, x_tolerance=2, y_tolerance=2, x_combine_tolerance=30):
    rows = defaultdict(list)
    for word in words:
        for y0 in rows.keys():
            if abs(word['top'] - y0) <= y_tolerance and abs(word['bottom'] - rows[y0][0]['bottom']) <= y_tolerance:
                rows[y0].append(word)
                break
        else:
            rows[word['top']].append(word)
    
    main_table, headers_table, content_dict = [], [], defaultdict(list)
    rounded_x_coords = [round(word['x0'], 2) for word in words]
    combined_x_coords = combine_close_x0(rounded_x_coords, x_combine_tolerance)
    combined_x_coords.insert(0, "Item")
    
    sorted_rows = sorted(rows.items(), key=lambda item: item[0])
    item_counter = 1

    for y0, row_words in sorted_rows:
        row = [''] * (len(combined_x_coords) + 1)  # +1 for U/M column
        row_dict = {round(word['x0'], 2): word['text'] for word in row_words}
        row_dict_updated = {k: False for k in row_dict}

        for key in sorted(row_dict):
            if row_dict[key] in ["U/M", "EA"]:
                previous_key = max((k for k in row_dict if k < key), default=None)
                if previous_key is not None:
                    row_dict[previous_key] += f" {row_dict[key]}"
                    del row_dict[key]
                    del row_dict_updated[key]

        row[0] = str(item_counter) if any("EA" in word['text'] for word in row_words) else ""
        if row[0]:
            item_counter += 1
        
        new_price_column = [''] * len(combined_x_coords)  # New column for prices

        for idx, x in enumerate(combined_x_coords[1:], start=1):
            closest_x = min(row_dict, key=lambda k: abs(k - x)) if row_dict else None

            if closest_x is not None and abs(closest_x - x) <= x_combine_tolerance:
                text = row_dict.get(closest_x, '')

                if re.search(r'\d{2}/\d{2}/\d{4}', text) and re.search(r'\d+\.\d+', text):
                    date, number = split_date_unit_price(text)
                    if date:
                        row[idx] = format_date(date)
                        row_dict_updated[closest_x] = True
                    if number:
                        new_price_column[idx] = format_unit_price(number)
                        row_dict_updated[closest_x] = True
                else:
                    if ':' in text:
                        header, content = map(str.strip, text.split(':', 1))
                        headers_table.append(header)
                        content_dict[header].append(content)
                    else:
                        split_text = text.split()
                        if len(split_text) == 2 and re.match(r'\d{2}/\d{2}/\d{4}', split_text[0]) and re.match(r'\d+\.\d+', split_text[1]):
                            row[idx] = format_date(split_text[0])
                            if idx + 1 < len(row):
                                row[idx + 1] = format_unit_price(split_text[1])
                            row_dict_updated[closest_x] = True
                        else:
                            row[idx] = text
                            row_dict_updated[closest_x] = True

                if "U/M" in text:
                    row[idx] = text.replace("U/M", "").strip()
                if "EA" in text:
                    row[idx] = text.replace("EA", "").strip()
                    row[-1] = "EA"  # Last column for U/M

        for idx, price in enumerate(new_price_column):
            if price:
                row[idx + 1] = price if not row[idx + 1] else f"{row[idx + 1]}, {price}"

        main_table.append(row)
    
    main_table = [row for row in main_table if any(cell.strip() for cell in row)]
    if main_table:
        main_table[0][0] = "Item"
        main_table[0][-1] = "U/M"

    return main_table, headers_table, content_dict, combined_x_coords











