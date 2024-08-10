import pandas as pd
from collections import defaultdict
import logging

from Release_details import group_words_into_table1
from Component_details import group_words_into_table2

class Utilities:
    """
    A utility class for PDF data extraction and processing.

    Attributes:
        x_tolerance (int): Tolerance for x-axis alignment when grouping words.
        y_tolerance (int): Tolerance for y-axis alignment when grouping words.
        x_combine_tolerance (int): Tolerance for combining x-coordinates.
    """
    def __init__(self, x_tolerance=2, y_tolerance=2, x_combine_tolerance=30):
        """
        Initializes the Utilities class with tolerance settings.

        Args:
            x_tolerance (int): Tolerance for x-axis alignment.
            y_tolerance (int): Tolerance for y-axis alignment.
            x_combine_tolerance (int): Tolerance for combining x-coordinates.
        """
        self._x_tolerance = x_tolerance  # Protected
        self._y_tolerance = y_tolerance  # Protected
        self._x_combine_tolerance = x_combine_tolerance  # Protected
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def extract_words_to_csv(self, page, bbox, item_counter=1):
        """
        Extracts words from a PDF page within a bounding box and creates a DataFrame.

        Args:
            page (pdfplumber.page.Page): The PDF page to extract words from.
            bbox (tuple): Bounding box coordinates (x0, top, x1, bottom).
            item_counter (int): Counter for assigning item numbers.

        Returns:
            pd.DataFrame: DataFrame containing the extracted words in a tabular format.
        """
        self.logger.info("Extracting words from page within bbox: %s", bbox)
        words = page.extract_words(keep_blank_chars=True)
        filtered_words = [
            word for word in words
            if bbox[0] <= word['x0'] <= bbox[2] and bbox[1] <= word['top'] <= bbox[3]
        ]
        content_dict = defaultdict(list)

        if any("Net Value" in word['text'] for word in filtered_words):
            main_table, headers_table, content_dict, x_coords = group_words_into_table1(
                filtered_words, 
                x_tolerance=self._x_tolerance, 
                y_tolerance=self._y_tolerance, 
                x_combine_tolerance=self._x_combine_tolerance
            )
        elif any("Mfg code" in word['text'] for word in filtered_words):
            table, x_coords = group_words_into_table2(
                filtered_words, 
                x_tolerance=self._x_tolerance, 
                y_tolerance=self._y_tolerance, 
                x_combine_tolerance=self._x_combine_tolerance
            )
            main_table = table
        else:
            main_table = []

        main_df = pd.DataFrame(main_table[1:], columns=main_table[0]) if main_table else pd.DataFrame()

        if content_dict:
            max_length = max(len(contents) for contents in content_dict.values())
            for key, value in content_dict.items():
                content_dict[key] += [''] * (max_length - len(value))
            content_df = pd.DataFrame(content_dict)
            combined_df = pd.concat([main_df, content_df], axis=1)
        else:
            combined_df = main_df

        combined_df.dropna(how='all', inplace=True)

        # Add Item Counter
        if not combined_df.empty and 'Mfg code' in combined_df.columns:
            combined_df['Item'] = range(item_counter, item_counter + len(combined_df))

        self.logger.info("Extracted DataFrame: %s", combined_df.head())
        return combined_df
