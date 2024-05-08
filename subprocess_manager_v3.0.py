import os
import pandas as pd
import sys
import subprocess
import json
import re
import psycopg2
from psycopg2 import extras
import pandas as pd

pd.set_option('display.max_columns', None)
total_records_written = 0

# Configurations
database_file_path = r"C:\Users\Jacob Shughrue\Dropbox\Coding\Python\grocery_scanner\purchased_items_database.csv"
images_folder = r"C:\Users\Jacob Shughrue\Dropbox\Coding\Python\grocery_scanner\images\unprocessed"
column_order = ['write_date', 'img_name', 'store_name', 'item', 'price']
database_name = 'grocery_image_database'

# run the heif converter subprocess
script_path = r"C:\Users\Jacob Shughrue\Dropbox\Coding\Python\grocery_scanner\heic_converter\hiec_converter_grocery_scanner.py"
hiec_result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)

# Check if the subprocess ran successfully
if hiec_result.returncode == 0:
    print("HEIC converter executed successfully - " + hiec_result.stdout)
else:
    print("subprocess execution failed.")
    print("Error:", hiec_result.stderr)


def read_database(database_name):
    """Read the database and return the list of images that have been processed previously"""
    try:
        # Read database credentials from JSON file
        with open(r'C:\Users\Jacob Shughrue\Dropbox\Coding\Python\grocery_scanner\postgres_database_credentials.json',
                  'r') as file:
            db_credentials = json.load(file)

        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=db_credentials["database_name"],
            user=db_credentials["user"],
            password=db_credentials["password"],
            host=db_credentials["host"],
            port=db_credentials["port"]
        )
        # Create a cursor object
        cur = conn.cursor()

        # Define the SQL query to fetch previously processed images
        sql_query = f"SELECT img_name FROM {database_name}"

        # Execute the SQL query
        cur.execute(sql_query)

        # Fetch all rows from the result set
        rows = cur.fetchall()

        # Extract the image names from the result set
        previously_processed_images = list(set([row[0].replace('processed_', '') for row in rows]))

        # Close the cursor and connection
        cur.close()
        conn.close()

    except FileNotFoundError:
        print("Error: Database credentials file not found.")
        previously_processed_images = []
    except Exception as e:
        print(f"An error occurred while reading from the database: {e}")
        previously_processed_images = []

    return previously_processed_images


# Call the function to read previously processed images from the database
previously_processed_images = read_database(database_name)


def find_unscanned_images(images_folder, previously_processed_images):
    """ Find images in the specified folder that are not in the provided list of images from the database
    and returns a list of filenames of unscanned images"""
    # List all files in the images_folder
    all_images = os.listdir(images_folder)

    # Filter out images that are not in the previously_processed_images list
    unscanned_images = [img for img in all_images if img not in previously_processed_images]

    return unscanned_images


# call unscanned images function
unscanned_images = find_unscanned_images(images_folder, previously_processed_images)

# set configuration for ocr_scanner script
venv_path = r"C:\Users\Jacob Shughrue\Dropbox\Coding\Python\grocery_scanner\venv"
activate_path = os.path.join(venv_path, 'Scripts', 'activate')
ocr_scanner_path = r"C:\Users\Jacob Shughrue\Dropbox\Coding\Python\grocery_scanner\grocery_scanner_v6.3.py"


def ocr_scan(image_name):
    print(f"Starting OCR scan of {image_name}")
    subprocess.run([activate_path], shell=True, text=True)
    result = subprocess.run([sys.executable, ocr_scanner_path, image_name], capture_output=True, text=True)

    # Check if the script ran successfully
    if result.returncode == 0:
        print(f"Processing of {image_name} succeeded.")

        # Extract the JSON data using a regular expression
        match = re.search(r'\{.*\}', result.stdout)

        if match:
            json_data = match.group()

            # Parse the JSON data
            try:
                output_data = json.loads(json_data)

                # Extract metadata_dict and json_dict
                metadata_json_str = output_data.get("metadata_json", "{}")
                metadata_json = json.loads(metadata_json_str)
                prompt = output_data.get("prompt", "{}")
                response = output_data.get("response", "{}")


            except json.JSONDecodeError:
                print(f"Failed to parse JSON output for {image_name}:")
                print("Output:", result.stdout)
        else:
            print(f"No valid JSON found in the output for {image_name}")
    else:
        print(f"Processing of {image_name} failed.")
        # Print the standard error output from the script
        print("Error:", result.stderr)
    return prompt, response, metadata_json  # , item_json


def write_data_to_postgres(df, column_order, previously_processed_images, image_name):
    """Append the given DataFrame to the PostgreSQL database if the image name is not in previously_processed_images."""
    records_written = 0  # Initialize count of records written

    image_name = "processed_" + image_name
    # Check if the DataFrame is not empty
    if not df.empty:
        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="jakeshug72",
                host="localhost",
                port="5432"
            )
            # Create a cursor object
            cur = conn.cursor()

            # Define the SQL statement for inserting data
            insert_query = f"INSERT INTO {database_name} ({', '.join(column_order)}) VALUES %s"

            # Convert DataFrame to list of tuples
            rows = [tuple(row) for row in df.values]

            # Execute the SQL statement with execute_values
            extras.execute_values(cur, insert_query, rows)

            # Commit the transaction
            conn.commit()

            # Update records_written with the count of records written
            iteration_records_written = len(df)
            records_written += iteration_records_written
            print(f"{iteration_records_written} records written for this image")

            # Close the cursor and connection
            cur.close()
            conn.close()
        except Exception as e:
            print(f"An error occurred while writing to PostgreSQL: {e}")
    else:
        print("An error occurred while writing to PostgreSQL, the DataFrame is empty")
    return iteration_records_written


def calculate_cost(prompt, response):
    # Specify the path to the separate script
    script_path = r"C:\Users\Jacob Shughrue\Dropbox\Coding\Python\grocery_scanner\chat_gpt_token_cost_script\chat_gpt_token_cost_script.py"

    # Run the separate script and capture its standard output
    completed_process = subprocess.run(
        [sys.executable, script_path, "--prompt", prompt, "--response", response],
        capture_output=True, text=True)

    if completed_process.returncode == 0:
        gpt_run_cost = 0
        for line in completed_process.stdout.split("\n"):
            if line.startswith("gpt_run_cost:"):
                gpt_iteration_run_cost = float(line.split(':')[1].strip())
                break
        return gpt_run_cost
    else:
        # Print error details if the subprocess failed
        print("Error: Could not process API cost calculation subprocess")
        print(f"Error Output: {completed_process.stderr}")
        return None


# Create a list of dictionaries for each item with metadata
total_cost = 0  # Initialize the variable to store the total cost
for image_name in unscanned_images:
    # prompt, response, metadata_json, item_json = ocr_scan(image_name)
    prompt, response, metadata_json = ocr_scan(image_name)
    # Handle JSON string response
    response_dict = json.loads(response)

    # Create an empty DataFrame
    combined_df = pd.DataFrame(columns=['write_date', 'img_name', 'store_name', 'item', 'price'])

    # Create an empty list to store DataFrames
    dfs = []

    # Create DataFrames for each item with metadata
    for key, value in response_dict.items():
        items = value.get('items', [])
        prices = value.get('prices', [])
        if items and prices:  # Check if both 'items' and 'prices' are present
            item = items[0]
            price = prices[0]
            df = pd.DataFrame({'write_date': metadata_json['write_date'],
                               'img_name': metadata_json['img_name'],
                               'store_name': metadata_json['store_name'],
                               'item': item, 'price': price}, index=[0])
            dfs.append(df)

        else:
            if not items:
                print(f"No items found for key '{key}'")
            if not prices:
                print(f"No prices found for key '{key}'")
                print('printing prices', prices)

    # Concatenate the DataFrames in the list
    combined_df = pd.concat(dfs, ignore_index=True)

    iteration_records_written = write_data_to_postgres(combined_df, column_order,
                                                       previously_processed_images, image_name)
    total_records_written += iteration_records_written

    # calculate cost
    gpt_run_cost = calculate_cost(prompt, response)
    total_cost += gpt_run_cost

print('All scripts complete - total records written: ' + str(total_records_written))
print(f"Total API Cost: ${total_cost:.8f}")
print('All processes complete')
