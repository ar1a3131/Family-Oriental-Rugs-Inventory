# ***Oriental Rugs - Data Exploration, Cultural Preservation, and Training Models***

My family business is in oriental rugs and we have such a large inventory that I thought it would be interesting to make a data science project out of it. From pricing of the rugs, to discovering trends in patterns and colors based off of country or region, you can explore my discoveries made through the process.

---------------------------------

## **Data Preprocessing**

##### **Step 1:** 01_scrape.py

Scraping from my family's GoDaddy hosted website (I also plan to scrape our ebay accounts, as well) with the Python playwright package and generating JSON and CSV files of the results (oriental_rugs.csv/.json). The parameters scraped include the id, name, product_url, original_price, sale_price, image_url, and source_page for each rug on our website (when I started this project there were 57 pages in total, each with 16 rugs... since then, more rugs have been uploaded and I'm currently trying to create a system with which I can run a script or two so that I can easily and accurately update the data [as with GoDaddy websites, there is no API to call for live updates, so I plan on keeping everything local] without having to manually fix/ go through preprocess everytime)

### To be continued...
