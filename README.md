# AmazonScrapper
An Amazon Scrapper Written In Python For Personal Educational Purposes

This program is written in python using selenium to rip below fields out of Amazon webstore into two Tables.

**Table1: Products Data**
        ID, Title, URL, Location, Variations Count, Review Count

**Table2: Reviews Data:**
        Product ID, Review ID, Author, Title, Context, User Rate, Review Score, Variation Purchased, Purchase Type, Date, Location
        
All scrapped data is getting saved into a sqlite3 database file,
You may convert the database to a csv file later on using this code.

**please note that Amazon doesnt have a unique structure for all categories, so I can't say if this code works on other categories than Laptops**

There are plenty of options in ASConfig.py to play around, Take a look!

Requirements -> A .txt file with product links you want to scrap (Please note that this app is only guaranteed to work properly for the Laptop category)
You need to synchronize your file name with ASConfig.py settings

Execute ASFront.py and follow instructions.


Further analysis of Amazon shows the structure in which the web page is built upon,

HTML structure and required XPaths for the product page is as follow:
![Amazon Product Variations](/Images/Product_Variations.png)

HTML structure and required XPaths for the reviews page is as follow:
![Amazon Product Reviews](/Images/Comments_Gathering.png)

HTML structure and required XPaths for the review cumulation pre-processing is as follow:
![Amazon Product Reviews Pre-Processing](/Images/Pre-Processings.png)

Live link to the Analysis Board is:
[Analysis Board by Miro](https://miro.com/app/board/o9J_lTy4h6k=/)

