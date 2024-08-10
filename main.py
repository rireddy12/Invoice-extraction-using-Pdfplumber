import pdfplumber
import pandas as pd
from utilities import Utilities

class PDFExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.utilities = Utilities()

    def find_pages_with_horizontal_lines(self):
        pages_with_lines = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                lines = page.lines
                horizontal_lines = [line for line in lines if line['y0'] == line['y1']]
                
                if horizontal_lines:
                    pages_with_lines.append(page_num)
        
        return pages_with_lines

    def find_word_and_below(self, page, target_word, stop_word=None):
        words = page.extract_words(keep_blank_chars=True)
        found = False
        coordinates = []
        for word in words:
            if found:
                if stop_word and stop_word in word['text']:
                    break
                coordinates.append({
                    'text': word['text'],
                    'x0': word['x0'],
                    'top': word['top'],
                    'x1': word['x1'],
                    'bottom': word['bottom']
                })
            if target_word in word['text']:
                found = True
        return coordinates if coordinates else None

    def find_enclosing_bbox(self, coordinates):
        if not coordinates:
            return None
        min_x0 = min(coord['x0'] for coord in coordinates)
        min_top = min(coord['top'] for coord in coordinates)
        max_x1 = max(coord['x1'] for coord in coordinates)
        max_bottom = max(coord['bottom'] for coord in coordinates)
        return (min_x0, min_top, max_x1, max_bottom)

    def clean_final_df(self, df):
        phrases = [
            'Import/Export Information:',
            'Consigned Value Per Die:',
            'Country of Origin:',
            'Special Instructions:'
        ]
        
        for phrase in phrases:
            if any(phrase in str(val) for val in df.values.flatten()):
                index = df[df.apply(lambda row: row.astype(str).str.contains(phrase).any(), axis=1)].index
                if not index.empty:
                    index = index[0]
                    df = df.iloc[:index]
                break
        
        return df

    def update_item_column(self, df):
        mfg_code_counter = 1
        item_counter = 1
        
        df['Item'] = ""

        for index, row in df.iterrows():
            if any("Mfg code" in str(val) for val in row):
                df.at[index, 'Item'] = f"{mfg_code_counter}"
                mfg_code_counter += 1
            elif any("EA" in str(val) for val in row):
                df.at[index, 'Item'] = f"{item_counter}"
                item_counter += 1
            else:
                df.at[index, 'Item'] = ""
        df['Item'] = df['Item'].replace("", pd.NA).astype('Int64')
        return df.ffill()

    def extract_and_save_table(self, word_pairs):
        dfs = []
        current_table = None
        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                for i, (target_word, stop_word) in enumerate(word_pairs):
                    result = self.find_word_and_below(page, target_word, stop_word)
                    if result:
                        bbox = self.find_enclosing_bbox(result)
                        if bbox:
                            df = self.utilities.extract_words_to_csv(page, bbox, item_counter=1)
                            if current_table is None:
                                current_table = df
                                print(current_table)
                            else:
                                if len(current_table.columns) == len(df.columns) and all(current_table.columns == df.columns):
                                    current_table = pd.concat([current_table, df], ignore_index=True)
                                    print(current_table)
                                else:
                                    if current_table is not None and not current_table.empty:
                                        dfs.append(current_table)
                                    current_table = df
                                    print(current_table)
            if current_table is not None and not current_table.empty:
                dfs.append(current_table)
        
        cleaned_dfs = [self.clean_final_df(df) for df in dfs]
        cleaned_dfs = [self.update_item_column(df) for df in cleaned_dfs]

        for idx, df in enumerate(cleaned_dfs):
            csv_filename = f"output_table_{idx+1}.csv"
            df.to_csv(csv_filename, index=False)
            print(f"Saved: {csv_filename}")
        return cleaned_dfs





