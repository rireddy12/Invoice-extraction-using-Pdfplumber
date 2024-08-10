from collections import defaultdict

# Define a function to combine close x0 values or those that are multiples of 10
def combine_close_x0(x_coords, tolerance=10):
    combined_x_coords = []
    if not x_coords:
        return combined_x_coords

    x_coords = sorted(x_coords)
    combined_x_coords.append(x_coords[0])
    
    for x in x_coords[1:]:
        last_x = combined_x_coords[-1]
        if abs(x - last_x) <= tolerance or (x % 10 == 0 and last_x % 10 == 0):
            # Combine columns
            combined_x_coords[-1] = (x + last_x) / 2
        else:
            combined_x_coords.append(x)
    
    return combined_x_coords

def group_words_into_table2(words, x_tolerance=2, y_tolerance=2, x_combine_tolerance=40):
    rows = defaultdict(list)
    for word in words:
        added_to_row = False
        for y0 in rows.keys():
            if abs(word['top'] - y0) <= y_tolerance and abs(word['bottom'] - rows[y0][0]['bottom']) <= y_tolerance:
                rows[y0].append(word)
                added_to_row = True
                break
        if not added_to_row:
            rows[word['top']].append(word)
    
    table = []
    rounded_x_coords = [round(word['x0']) for word in words]
    combined_x_coords = combine_close_x0(rounded_x_coords, x_combine_tolerance)
    
    item_column_x = None
    for word in words:
        if "Item" in word['text']:
            item_column_x = round(word['x0'])
            break
    
    if item_column_x is not None:
        combined_x_coords.insert(0, "Item")
    
    mfg_code_counter = 1
    
    for y0, row_words in sorted(rows.items()):
        if any("Page" in word['text'] for word in row_words):
            continue
        row = []
        row_dict = {round(word['x0']): word['text'] for word in row_words}
        
        if any("Mfg code" in word['text'] for word in row_words):
            row.append(f"{mfg_code_counter}")
            mfg_code_counter += 1
        else:
            row.append("")
        
        for x in combined_x_coords[1:]:  # Skip the first item if it's the "Item" column header
            # Find the closest x0 value to combine
            closest_x = min(row_dict.keys(), key=lambda k: abs(k - x)) if row_dict else None
            if closest_x is not None and abs(closest_x - x) <= x_combine_tolerance:
                row.append(row_dict.get(closest_x, ''))
            else:
                row.append('')
        
        table.append(row)
    if table:
        table[0][0] = "Item"
    
    return table, combined_x_coords


