import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from main import PDFExtractor  # Ensure this import matches your module structure

# Define your MySQL connection details
mysql_user = 'haritha'
mysql_password = 'spsoft'
mysql_host = '192.168.5.46'
mysql_database = 'test_del'

# Establish a connection using SQLAlchemy
engine = create_engine(f'mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}')

st.set_page_config(
    page_title="PDF Table Extraction App",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for background color, padding, and other styling
custom_css = """
    <style>
        body {
            background-color: #f7f9fc; /* Light blue-gray background */
            color: #333333; /* Dark gray text color */
            font-family: 'Arial', sans-serif; /* Font family */
        }
        .stApp {
            background-color: #ffffff; /* White background for main container */
            padding: 2rem; /* Padding around main container */
            border-radius: 10px; /* Rounded corners for main container */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow for main container */
        }
        .st-ba {
            background-color: #f0f0f0; /* Light gray background for headers */
        }
        .stButton>button {
            background-color: #007bff; /* Blue background for buttons */
            color: white; /* White text for buttons */
            border-radius: 5px; /* Rounded corners for buttons */
            padding: 0.5rem 1rem; /* Padding for buttons */
            font-weight: bold; /* Bold text for buttons */
        }
        .stButton>button:hover {
            background-color: #0056b3; /* Darker blue on hover for buttons */
            color: #ffffff; /* White text on hover */
        }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

def save_to_mysql(df, table_name):
    """
    Saves a DataFrame to the MySQL database.

    Args:
        df (pd.DataFrame): DataFrame to save.
        table_name (str): Name of the table in the MySQL database.
    
    Returns:
        None
    """
    df.to_sql(name=table_name, con=engine, if_exists='replace', index=True)
    st.success(f'DataFrame saved to MySQL table `{table_name}` successfully.')

def display_release_details(pdf_path, word_pairs):
    """
    Extracts and displays the release details from the provided PDF file.
    
    Args:
        pdf_path (str): The path to the PDF file.
        word_pairs (list of tuple): List of word pairs used for extracting tables from the PDF.
    
    Returns:
        None
    """
    extractor = PDFExtractor(pdf_path)
    dfs = extractor.extract_and_save_table(word_pairs)
    if dfs:
        for i, df in enumerate(dfs):
            if "Net Value" in df.columns:
                st.subheader(f"Release Details {i + 1}")
                st.write(df)
                # Save the DataFrame to MySQL
                save_to_mysql(df, 'Release_details')
    else:
        st.warning("No 'Release Details' found in the PDF.")

def display_component_details(pdf_path, word_pairs):
    """
    Extracts and displays the component details from the provided PDF file.
    
    Args:
        pdf_path (str): The path to the PDF file.
        word_pairs (list of tuple): List of word pairs used for extracting tables from the PDF.
    
    Returns:
        None
    """
    extractor = PDFExtractor(pdf_path)
    dfs = extractor.extract_and_save_table(word_pairs)
    if dfs:
        for i, df in enumerate(dfs):
            if "Markings" in df.columns:
                st.subheader(f"Component Details {i + 1}")
                st.write(df)
                # Save the DataFrame to MySQL
                save_to_mysql(df, 'Component_details')
    else:
        st.warning("No 'Component Details' found in the PDF.")

def main():
    """
    Main function to run the Streamlit app for PDF table extraction.
    
    Sets up the layout and functionality of the app, including file upload and button interactions.
    
    Returns:
        None
    """
    st.title("PDF Table Extraction App")
    
    col1, col2, col3 = st.columns([1, 1, 1])  # Three equal-width columns

    # Button to upload PDF file
    pdf_file = st.file_uploader("Upload PDF file", type=["pdf"])
    
    if pdf_file:
        # Convert the uploaded PDF file to a BytesIO object
        pdf_path = pdf_file.name
        
        # Save the uploaded file to a temporary file
        with open(pdf_path, "wb") as f:
            f.write(pdf_file.getvalue())
        
        # Define word pairs for extraction
        word_pairs = [
            ("Details", "Order Subtotal:"),
            ("Component Details:", "Import/Export Information:")
        ]

        # Button to display Release Details data frame
        col1.button(
            label='Release Details',
            key="release_details_button",
            on_click=display_release_details,
            args=(pdf_path, word_pairs),  # Arguments for the callback function
            disabled=False,
            use_container_width=True,
            type="primary"
        )

        # Button to display Component Details data frame
        col2.button(
            label="Component Details",
            key="component_details_button",
            on_click=display_component_details,
            args=(pdf_path, word_pairs),  # Arguments for the callback function
            disabled=False,
            use_container_width=True,
            type="primary"
        )

        # Button to clear session state
        col3.button(
            label="Clear",
            key="clear_button",
            help="Click to clear the session state",
            on_click=st.session_state.clear,
            disabled=False,
            use_container_width=True,
            type="primary"
        )

if __name__ == "__main__":
    main()
