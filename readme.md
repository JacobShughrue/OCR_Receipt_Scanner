## OCR Receipt Scanner - ReadMe

### Objective:
**Use Optical Content Recognition (OCR) software to read in the content from receipts, cluster and clean the receipt data and, write the results to a Postgres database table**

### File Glossary
**1. excercise_data.xlsx** - this is the source data provided (note the file has two tabs).

**2. data_excel_export** - this shows the manual Excel analysis I completed including some advanced calculations like nested if statements, index/match statements, and unique/filter statements.

**3. Harrys.ipynb** - Note: this file can be viewed in your browser: This is the Python file that replaces the steps done in Excel, or in other words is the automated version of my prior manual work. A ".py" file is also available to view the actual code that was run.

**3. Project_Findings.ppt** - [Here is a live link](https://docs.google.com/presentation/d/1L8aVWmDF_4w19iYOFrK988bqGLc0i6lX/edit?usp=sharing&ouid=102162804501747919451&rtpof=true&sd=true) to the PowerPoint I prepared with findings summarized for stakeholders.

### My Steps
**1.** Observe the data in Excel - I noticed a join could be made between the two tables on the key "viewable_product_id".

**2.** While in Excel, I joined the tables and created several new columns allowing me to ultimately generate a column called "customer_subscription_change_flag".
As the name suggests, this allows me to see which customers modified their subscription of Harry's Razor products. The goal here was to compare customers who did not change their subscription to those who did modify what they received and analyze if subscription modification helped customer retention. 

**3.** I was then able to export this Excel file to Power BI to generate visuals and capture insights. As I put together my dashboard the story I was trying to tell came to life - and in some cases, sent me back to Excel for further data manipulation. [A live link to the Power BI dashboard is available here.](https://app.powerbi.com/view?r=eyJrIjoiYzRmYWE5NDEtMTgzZS00NzAzLWE0MDEtOTlmNDQ4ZjhhNjM4IiwidCI6IjdmZjljNGI5LWU0NWUtNGIyMi1hOTcwLWQ3N2FkMjBhNzk1ZCIsImMiOjZ9)

**4.** Once I finished visualizing the data, I wanted to complete the same data manipulation steps that I had taken in Excel, in Python Pandas. This step eliminates the manual analysis I did in Excel. I did this step at the end because, with this being the first time I had seen or worked with the data, Excel allowed me to explore the data more easily. With the Python code I have written, this data could be processed hundreds of times each day without issue, ultimately adding automation to the project pipeline. 

**5.** Lastly, I summarized my findings into a PowerPoint presentation that could be delivered to stakeholders.  [Link available here.](https://docs.google.com/presentation/d/1L8aVWmDF_4w19iYOFrK988bqGLc0i6lX/edit?usp=sharing&ouid=102162804501747919451&rtpof=true&sd=true)

**With any questions, don't hesitate to reach out.**
