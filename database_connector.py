import mysql.connector
import pandas as pd
import logging

def connect_to_database(host, user, password, database):
    """
    Connects to the MySQL database.

    Args:
        host (str): Database host.
        user (str): Database user.
        password (str): Database password.
        database (str): Database name.

    Returns:
        tuple: Connection and cursor objects.
    """
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = connection.cursor()
        logging.info("Successfully connected to the database.")
        return connection, cursor
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to the database: {err}")
        return None, None

def disconnect_from_database(connection, cursor):
    """
    Closes the database connection.

    Args:
        connection: Database connection object.
        cursor: Database cursor object.
    """
    if cursor:
        cursor.close()
    if connection:
        connection.close()
    logging.info("Database connection closed.")

def create_table(cursor, table_name, columns):
    """
    Creates a table in the database.

    Args:
        cursor: Database cursor object.
        table_name (str): The name of the table to create.
        columns (str): Column definitions for the table.
    """
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
    try:
        cursor.execute(create_table_query)
        logging.info(f"Table {table_name} created successfully.")
    except mysql.connector.Error as err:
        logging.error(f"Error creating table: {err}")

def insert_data(cursor, connection, table_name, final_df):
    """
    Inserts data from a DataFrame into the database table.

    Args:
        cursor: Database cursor object.
        connection: Database connection object.
        table_name (str): The name of the table to insert data into.
        dataframe (pd.DataFrame): The DataFrame containing data to insert.
    """
    columns = ", ".join(final_df.columns)
    placeholders = ", ".join(["%s"] * len(final_df.columns))
    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    for _, row in final_df.iterrows():
        try:
            cursor.execute(insert_query, tuple(row))
            connection.commit()
            logging.info(f"Inserted data into {table_name} successfully.")
        except mysql.connector.Error as err:
            logging.error(f"Error inserting data: {err}")
            connection.rollback()
