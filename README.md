# Invoice table-extraction-using-Pdfplumber
PDF PLUMBER is a Python library for extracting data from PDF files.
# Introduction to pdf plumber

1. Plumb a PDF for data extraction:
pdfplumber is a Python library that allows to extraction of detailed information about each text character, rectangle, and line in a PDF document. It also provides tools for table extraction and visual debugging.

2. Extract Text, Tables, and Metadata:
pdfplumber gives you the ability to extract text, tables, and metadata from PDF files, making it a powerful tool for automating data extraction and processing from PDFs in various formats.

3. Leverage the PDFMiner Library:
pdfplumber uses the PDFMiner library, a Python library that provides a low-level interface to PDF files, to extract data from PDFs.

# Key Features of pdfplumber:
1. Text extraction
2. Table extraction
3. Image Extraction
4. Page analysis

# Overview of the Project:
1. Project Goal: The goal of this project is to use Python library-pdfplumber that can be used to extract data from PDF files.
2. Project Scope: The project will focus on a pdfplumber that can extract text, tables, images, and other information from PDFs.
3. Project Deliverables: The project will deliver a streamlit app that displays extracted data in tables from PDF files.

# Approach
## Bounding Box Method
The library also leverages bounding box analysis to identify and extract elements within the PDF based on their spatial coordinates. This enables precise layout and formatting extraction.
1. Release_details.py and Component_details.py-Handle specific data extraction logic for release and component details.
2. Utilities. py-Provide utility functions for extracting and processing PDF data.
3. Main. py-Extract and process tables from PDF documents.
4. Protected Attributes and Methods: Indicated by a single underscore (_).

# Output
Used the streamlit interface to display "Release Details" and "Component Details" by clicking the buttons and using "mysql connector" to display them in mysql workbench.

# Conclusion
pdfplumber, a versatile Python library for automating PDF data extraction. By leveraging pdfplumber's methods and functions, you can now efficiently parse PDF documents, extract structured data, and integrate these capabilities into our own applications.
