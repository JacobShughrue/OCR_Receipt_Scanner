## OCR Receipt Scanner - ReadMe
### Objective:
**Use Optical Content Recognition (OCR) software to read in the content from receipts, cluster and clean the receipt data and, write the results to a Postgres database table**

### File Glossary
**1. subprocess_manager_v3.0.py** - this file is the orchestration script that will call all other subprocesses listed below.

**2. hiec_converter_grocery_scanner.py** - This subprocess simply converts iPhone photos in the .HEIC format to PNGs for readability.

**3. grocery_scanner_v6.3.py** - this is the primary subprocess script. It carries the code to read in the data from the receipt via EasyOCR, cluster together the price and item data via horizontal and vertical pixel cluster groups. This subprocess also sends the OCR results into ChatGPT 3.5 model 1106 to clean any data that does not belong in a grocery item database.

**4. chat_gpt_token_cost_script.py** - this script will calculate the associated cost of the ChatGPT API call in US dollars.

**5. database_result.jpg** - this screenshot shows a Postgres table in DBeaver with the extracted values from the receipts. These values will be archived and for example, could be analyzed to calculate inflation in item prices quarter over quarter.

### Methodology:
**OCR Scan - Choosing an OCR Library** - Data is imported into this series of scripts via OCR allowing a user to digitize the printed data on a receipt. I tested a number of different OCR libraries such as Tesseract OCR, Donut OCR, Easy OCR and ultimately found Paddle OCR to deliver the best results consistently when uploading receipts from a variety of different stores. After rigorous testing, I found that preprocessing the image (e.g. denoising or changing the gamma levels) did very little to improve OCR results and in some cases, made the receipts less legible.

**OCR Scan - Data Clustering** - As the data was read in via Paddle OCR, every word came with X and Y coordinates based on the pixels of the image. Within scikit-learn, I used DBSCAN, a clustering function that analyzes how close these words were to each other (word density) to assign the words to groups. On a normal receipt, there would be two horizontal groups, the item on the left and the price on the right. For the vertical groups, every new line is assigned as a new vertical group. The sensitivity of these groups is modified by the EPS (epsilon) parameter seen in the grocery_scanner_v6.3.py script.

**ChatGPT API Call - Data Manipulation** - Once the data was read in from the OCR Scanner the data was clustered, analyzed, and placed into key/value pairs for the item/price. These key/value pairs were fed into the ChatGPT 3.5 v1106 API model. This model is specifically designed to return only JSON formatted data back. The prompt requested ChatGPT to trim any data that is not item or price data. For example, store name, store address, serial numbers, subtotals are removed from the data returning clean key/value pairs with relevant data only.

**ChatGPT API Call - Cost Calculator** - Once the API call is finished the prompt and response are also fed to the chat_gpt_token_cost_script.py script which uses a pre-built function to calculate exactly how many tokens were used and what the USD cost is associated with that. Because I am using the ChatGPT 3.5 model and not ChatGPT 4.0, the cost per image is less than a penny to feed the data to the API.

**Data Load - Upload to Postgres DB** - Once the API call is finished the clean key/value pairs of data are sent to a Postgres DB that I am maintaining. The script will run in a loop to see if there are any other photos that have not been scanned yet and need to be uploaded to Postgres as well.
