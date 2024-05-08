import cv2
import os
from paddleocr import PaddleOCR, draw_ocr
from sklearn.cluster import DBSCAN
from PIL import Image
from openai import OpenAI
import pandas as pd
import sys
import json
from datetime import datetime
import logging

# Disable all logging messages from 'ppocr' module
logging.getLogger('ppocr').setLevel(logging.WARNING)


def process_image(image_name):
    # Path to the image
    # image_name = "IMG_6566.png"
    folder_path = r"C:\Users\Jacob Shughrue\Dropbox\Coding\Python\grocery_scanner\images"
    unprocessed_image_path = os.path.join(folder_path, "unprocessed", image_name)
    processed_image_path = os.path.join(folder_path, "processed", image_name)

    today_date = datetime.now().strftime("%m/%d/%Y")

    # Function to preprocess the image
    def preprocess_image(image_path):
        # Read the image
        image = cv2.imread(image_path)

        # Convert to grayscale
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # # Increase contrast by darkening the blacks
        # black_point = 25
        # _, image = cv2.threshold(image, black_point, 255, cv2.THRESH_TOZERO)
        #
        # # Resize the image to twice its size
        # image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        #
        # # Apply denoising
        # image = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
        #
        # # Apply gamma adjustment
        # gamma = 0.5  # Gamma value greater than 1 darkens the image
        # invGamma = 1.0 / gamma
        # table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        # image = cv2.LUT(image, table)

        return image

    # Preprocess the image
    preprocessed_image = preprocess_image(unprocessed_image_path)

    # Save the processed image
    processed_image_filename = 'processed_' + os.path.basename(processed_image_path)
    processed_image_path = os.path.join(os.path.dirname(processed_image_path), processed_image_filename)
    cv2.imwrite(processed_image_path, preprocessed_image)

    # PaddleOCR to read the receipt
    ocr = PaddleOCR(use_angle_cls=True, lang='en')

    # Perform OCR on the preprocessed image
    print('Scanning: ' + image_name)
    ocr_results = ocr.ocr(preprocessed_image, cls=True)
    data = []

    for word in ocr_results:
        for box, text_data in word:
            # Calculate the x-coordinate of the center-left point (average of the x-coordinates of the left points)
            left_x_coords = [box[0][0], box[3][0]]  # box[0] and box[3] are the top-left and bottom-left points
            center_left_x = sum(left_x_coords) / 2

            # Calculate the y-coordinate of the mid-point (average of all y-coordinates)
            y_coords = [point[1] for point in box]
            mid_y = sum(y_coords) / 4

            data.append({'horizontal_location': center_left_x, 'vertical_location': mid_y, 'word': text_data[0]})

    df_detail = pd.DataFrame(data)

    def estimate_eps_from_image(processed_image_path, horizontal_fraction=0.01, vertical_fraction=0.0085):
        # Open the image
        with Image.open(processed_image_path) as img:
            # Extract image dimensions in pixels
            width_pixels, height_pixels = img.size

            # Calculate EPS for horizontal and vertical dimensions separately
            horizontal_eps_factor = width_pixels * horizontal_fraction
            vertical_eps_factor = height_pixels * vertical_fraction

            return horizontal_eps_factor, vertical_eps_factor

    # Estimate horizontal and vertical EPS with default fractions
    horizontal_eps_factor, vertical_eps_factor = estimate_eps_from_image(processed_image_path)
    print("Estimated Horizontal EPS:", horizontal_eps_factor)
    print("Estimated Vertical EPS:", vertical_eps_factor)

    # Create horizontal grouping via horizontal clustering
    horizontal_clustering = DBSCAN(eps=horizontal_eps_factor, min_samples=1).fit(
        df_detail[['horizontal_location']])  # 90
    df_detail['horizontal_group'] = horizontal_clustering.labels_

    # Create height grouping via vertical clustering
    vertical_clustering = DBSCAN(eps=vertical_eps_factor, min_samples=2).fit(df_detail[['vertical_location']])
    df_detail['height_group'] = vertical_clustering.labels_

    group_counts = df_detail['horizontal_group'].value_counts()

    # Step 2: Identify the two groups with the highest occurrence
    top_two_groups = group_counts.nlargest(2).index

    # Step 3: Filter the DataFrame to only include rows from these two groups
    df_ocr_feed = df_detail[df_detail['horizontal_group'].isin(top_two_groups)]

    # The group with the highest count will be 'price' and the second highest 'item'
    rename_mapping = {top_two_groups[0]: 'item', top_two_groups[1]: 'price'}
    df_ocr_feed['word_type'] = df_ocr_feed['horizontal_group'].map(rename_mapping)

    height_groups = {}
    for _, row in df_ocr_feed.iterrows():
        group = height_groups.setdefault(row['height_group'], {'items': [], 'prices': []})
        group[row['word_type'] + 's'].append(row['word'])

    # Filter out groups that don't have exactly one item and one price
    height_groups = {k: v for k, v in height_groups.items() if len(v['items']) == 1 and len(v['prices']) == 1}

    # Function to read the secret key from JSON file
    def read_secret_key_from_json(filename):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                return data.get("api_key", None)
        except FileNotFoundError:
            print("Error: File not found at specified path.")

    # Path to your JSON file
    file_path = r'C:\Users\Jacob Shughrue\Dropbox\Coding\Python\grocery_scanner\open_ai_api_key.JSON'

    # Your API key
    api_key = read_secret_key_from_json(file_path)
    client = OpenAI(api_key=api_key)

    # Send the OCR results to OpenAI API
    prompt = (
            "Interpret the receipt data being fed and clean the data to  "
            "ensure that the 'item' field contains only actual store grocery values not irrelevant data such as '2 @'$0.75' or '17745', "
            "tax lines, discounts, bottle deposits or item numbers. For the price field ensure only numbers(floats) are written. "
            "Never produce blank dictionaries or leave a key / value blank. Do not fabricate data"
            + str(height_groups)
    )
    # Sending the prompt to the OpenAI API with a request for JSON formatted response
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "provide output in valid JSON format"},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the JSON response
    response = chat_completion.choices[0].message.content
    # Convert the response to a dictionary
    response_dict = json.loads(response)

    # # Initialize lists to store items and prices
    # items_list = []
    # prices_list = []
    #
    # # Extract items and prices from the response dictionary
    # for height_group, values in response_dict.items():
    #     items_list.extend(values['items'])
    #     prices_list.extend(values['prices'])
    #
    # # Create DataFrame with 'Items' and 'Prices' columns
    # df = pd.DataFrame({'Items': items_list, 'Prices': prices_list})

    metadata_dict = {
        "write_date": today_date,
        "img_name": processed_image_filename,
        "store_name": "trader_joes"
    }

    # Serialize the needed dictionaries to a JSON string
    # item_json = json.dumps(response_dict)
    metadata_json = json.dumps(metadata_dict)

    output = {
        "metadata_json": metadata_json,
        # "item_json": item_json,
        "prompt": prompt,
        "response": response
    }
    print(json.dumps(output))


if __name__ == "__main__":
    # Check if both image path and image name are provided as command-line arguments
    if len(sys.argv) == 2:
        image_name = sys.argv[1]
        process_image(image_name)
    else:
        print("Usage: python grocery_scanner_v6.py <image_name>")
