import math
import sqlite3
import csv
import ASConfig as Config
from selenium import webdriver
from ASCore import ProductData
from ASCore import ReviewData
from typing import List
from selenium.webdriver.support import expected_conditions

def get_review_counts(text: str):
    count: [str] = text.split()
    return int(count[4])

def get_review_count_on_last_page(review_counts: int):
    mod = review_counts % 10
    if review_counts > 0 and mod == 0:
        return 10
    else:
        return mod

def get_review_pages(review_counts: int):
    return math.ceil(review_counts / 10)

def get_review_page_url(page: int, product_url: str):
    chars = product_url.split('/')
    chars[4] = 'product-reviews'
    chars[6] = 'ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews&pageNumber={0}'.format(str(page))
    url = '/'.join(chars)
    return url

def get_review_rate(text: str):
    rate = text.split()
    return rate[0]

def get_review_score(text: str):
    count: [str] = text.split()
    return count[0]

def get_review_loc(text: str):
    array = text.split()
    array = array[:len(array)-4]
    array = array[3:]
    location = ' '.join(array)
    return location

def get_review_date(text: str):
    array = text.split()
    array = array[-3:]
    date = ' '.join(array)
    return date

def get_product_id(url: str):
    address = url.split(sep='/')
    return address[5]

def get_product_loc(text: str):
    array = text.split()
    array = array[4:]
    location = ' '.join(array)
    return location

def initiate_driver():
    #options = webdriver.ChromeOptions() if Config.driver_name == 'Chrome' else webdriver.FirefoxOptions()
    if Config.driver_name == 'Chrome':
        options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("detach", True)
    else:
        options = webdriver.FirefoxOptions()

    if Config.driver_is_headless >= 1:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

    options.page_load_strategy = Config.page_load_strategy

    if Config.driver_name == 'Chrome':
        driver = webdriver.Chrome(chrome_options=options)
    else:
        driver = webdriver.Firefox(firefox_options=options)
    return driver

def initiate_database():
    database = sqlite3.connect(Config.output_database_name + '.db')
    c = database.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS Products
    (ID_Product TEXT, Name TEXT, Url TEXT, Location TEXT, VariationCount INTEGER, ReviewCount INTEGER)''')

    c.execute('''CREATE TABLE IF NOT EXISTS Reviews
    (ID_Product TEXT, ID_Review TEXT, Author TEXT, Title TEXT, Context TEXT, Rate INTEGER,Score INTEGER, Variation TEXT, Type TEXT, Date TEXT, Location TEXT)''')
    return database

def get_saved_review_count_for_product_on_database(database: sqlite3, product_id: str):
    c = database.cursor()
    try:
        c.execute('''SELECT COUNT(*) FROM Reviews WHERE ID_Product = ?''', [product_id])
        occurrences = c.fetchone()
        return occurrences
    except Exception as e:
        print("Could not count all occurrences for product_id of {0}, Error->...".format(product_id))
        print(e)
        return -1

def product_exists(database: sqlite3, product_id: str):
    c = database.cursor()
    try:
        c.execute('''SELECT EXISTS(SELECT 1 FROM Products WHERE ID_Product = ?);''', [product_id])
        record = c.fetchone()
        return record[0] > 0
    except Exception as e:
        print("Could not check record for product_id of {0}, Error->...".format(product_id))
        print(e)
        return False

def review_exists(database: sqlite3, review_id: str):
    c = database.cursor()
    try:
        c.execute('''SELECT EXISTS(SELECT 1 FROM Reviews WHERE ID_Review = ? AND Date = ?);''', [review_id])
        record = c.fetchone()
        return record[0] > 0
    except Exception as e:
        print("Could not check record for review_id of {0}, Error->...".format(review_id))
        print(e)
        return False

def write_to_database(database: sqlite3, product_data: ProductData = None, review_data: List[ReviewData] = None):
    c = database.cursor()
    if product_data is not None:
        print('Product data with ID[{0}] is being added'.format(product_data.product_id))
        # -------------------------------------------------------------------------------
        c.execute(
            '''INSERT INTO Products (ID_Product, Name, Url, Location, VariationCount, ReviewCount) VALUES (?, ?, ?, ?, ?, ?)''',
            (
            product_data.product_id, product_data.product_name, product_data.product_url, product_data.product_location,
            product_data.product_var_count, product_data.product_review_count))
        # -------------------------------------------------------------------------------
    if review_data is not None:
        for i in range(len(review_data)):
            print('Review data with RID[{0}] and PID[{1}] is being added'.format(review_data[i].review_id,review_data[i].product_id))
            # -------------------------------------------------------------------------------
            c.execute(
                '''INSERT INTO Reviews (ID_Product, ID_Review, Author, Title, Context, Rate, Score, Variation, Type, Date, Location) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    review_data[i].product_id, review_data[i].review_id, review_data[i].review_author,
                    review_data[i].review_title, review_data[i].review_context, review_data[i].review_rate,
                    review_data[i].review_score, review_data[i].review_var, review_data[i].review_type,
                    review_data[i].review_date, review_data[i].review_loc))
            # -------------------------------------------------------------------------------
    database.commit()

def import_product_links(file_name: str):
    links: List[str] = []
    with open(file_name, "r") as f:
        for x in f:
            x = x.replace("\r", "").replace("\n", "")
            if len(str(x)) > 0 and (str(x)[0] != '#' or ''):
                links.append(str(x))
    return links

def get_page_review_ids(driver: webdriver):
    ids: List[str] = []
    review_count_on_page: int = len(driver.find_elements_by_xpath(Config.xp_reviews_list))
    for i in range(review_count_on_page):
        review_id = driver.find_element_by_xpath(Config.xp_review_at_index(i+1)).get_attribute('id')
        ids.append(review_id)
    return ids

def get_review_type(driver: webdriver, rid: str):
    base_xp = Config.xp_review_misc_info_by_id(rid)
    try:
        driver.find_element_by_xpath(base_xp + '/span[1]/a/span')
        return 'Verified Purchase'
    except expected_conditions.NoSuchElementException as e:
        try:
            driver.find_element_by_xpath(base_xp + '/span[1]')
            return 'Vine Customer Review of Free Product'
        except expected_conditions.NoSuchElementException as e:
            return 'Unverified Purchase'

def convert_sql_to_cvs(database: sqlite3):
    with open(Config.output_database_name + '_Products.csv', 'w', newline='', encoding='utf_8') as f:
        c = database.cursor()
        c.execute('''SELECT * FROM Products''')
        results = c.fetchall()
        print('Results length for Products is : ' + str(len(results)))
        writer = csv.writer(f)
        writer.writerow(['Product ID', 'Product Name', 'Product URL', 'Location', 'Variations Count', 'Reviews Count'])
        for result in results:
            print('Result is ' + str(result))
            writer.writerow([result[0], result[1], result[2], result[3], result[4], result[5]])
        f.close()
        print('Conversion Completed for Products!')

    with open(Config.output_database_name + '_Reviews.csv', 'w', newline='', encoding='utf_8') as f:
        c = database.cursor()
        c.execute('''SELECT * FROM Reviews''')
        results = c.fetchall()
        print('Results length for Reviews is : ' + str(len(results)))
        writer = csv.writer(f)
        writer.writerow(['Product ID', 'Review ID', 'Author', 'Title', 'Context', 'Rate', 'Score', 'Variation', 'Type', 'Date', 'Location'])
        for result in results:
            print('Result is ' + str(result))
            writer.writerow([result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10]])
        f.close()
        print('Conversion Completed for Reviews!')