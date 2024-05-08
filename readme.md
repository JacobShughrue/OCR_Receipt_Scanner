## OCR Receipt Scanner - ReadMe

### Objective:
**Use Optical Content Recognition (OCR) software to read in the content from receipts, cluster and clean the receipt data and, write the results to a Postgres database table**

### File Glossary
**1. subprocess_manager_v3.0.py** - this file is the orchestration script that will call all other subprocesses listed below.

**2. hiec_converter_grocery_scanner.py** - This subprocess simply converts iphone photos in the .HEIC format to PNGs for readability.

**3. grocery_scanner_v6.3.py** - this is the primary subprocess script. It carries the code to read in the data from the receipt via EasyOCR, cluster together the price and item data via horizontal and vertical pixel cluster groups. This subprocess also sends the OCR results into ChatGPT 3.5 model 1106 to clean any data that does not belong in a grocey item database. 

**4. chat_gpt_token_cost_script.pyt** - this script with calculate the associated cost of the ChatGPT API call in US dollars.
