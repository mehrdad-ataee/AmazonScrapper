import sqlite3
# import ASUtilities as Utility
import ASConfig as Config
from selenium import webdriver
from selenium.webdriver.remote import webelement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from dataclasses import dataclass
from typing import List


@dataclass
class ProductData:
    __slots__ = ['product_id', 'product_name', 'product_url', 'product_location', 'product_var_count', 'product_review_count']
    product_id:             str
    product_name:           str
    product_url:            str
    product_location:       str
    product_var_count:      int
    product_review_count:   int
    def __init__(self, id: str, name: str, url: str, location: str, var_count: int, rev_count: int):
        self.product_id = id
        self.product_name = name
        self.product_url = url
        self.product_location = location
        self.product_var_count = var_count
        self.product_review_count = rev_count

@dataclass
class ReviewData:
    __slots__ = ['product_id', 'review_id', 'review_author', 'review_title', 'review_context', 'review_rate', 'review_score', 'review_var', 'review_type', 'review_date', 'review_loc']
    product_id:     str
    review_id:      str
    review_author:  str
    review_title:   str
    review_context: str
    review_rate:    int
    review_score:   int
    review_var:     str
    review_type:    str
    review_date:    str
    review_loc:     str
    def __init__(self, pid, rid, author, title, context, rate, score, var, typ, date, loc):
        self.product_id = pid
        self.review_id = rid
        self.review_author = author
        self.review_title = title
        self.review_context = context
        self.review_rate = rate
        self.review_score = score
        self.review_var = var
        self.review_type = typ
        self.review_date = date
        self.review_loc = loc


import ASUtilities as Utility

class RipperCore:
    driver: webdriver
    database: sqlite3
    product_links: List[str] = []
    product_data: ProductData
    review_data: List[ReviewData] = []
    review_counts: int = 0
    review_counts_last_page: int = 0
    reload_count: int = 0

    def initiate(self):
        self.driver = Utility.initiate_driver()
        self.driver.set_page_load_timeout(Config.page_wait)
        self.database = Utility.initiate_database()
        self.product_links = Utility.import_product_links(Config.products_links_source_name)
        for i in range(len(self.product_links)):
            if Utility.product_exists(self.database, Utility.get_product_id(self.product_links[i])):
                print('Product[{0}] all-ready exists in the database'.format(Utility.get_product_id(self.product_links[i])))
            else:
                self.product_data = self.extract_product_page(self.product_links[i])
                self.review_data = self.extract_review_page(self.product_links[i])
                Utility.write_to_database(self.database, self.product_data, self.review_data)
        self.driver.close()
        self.database.close()
        print('Finished scrapping data for all products...')

    def extract_product_page(self, product_url: str):
        # Initiate temporal data holder
        _product_data: ProductData = ProductData("Null", "Null", product_url, "Null", -1, -1)

        print('Extracting product data for Product[{0}]'.format(product_url))
        try:
            # Open product page
            self.driver.get(product_url)
            # Read, extract and write data to the temporal data holder
            WebDriverWait(self.driver, Config.element_wait).until(expected_conditions.presence_of_element_located(
                (By.XPATH, Config.xp_product_name)))

            _product_id = Utility.get_product_id(product_url)
            _product_name = self.driver.find_element_by_xpath(Config.xp_product_name).text
            _product_url = product_url
            _product_var_count = len(self.driver.find_elements_by_xpath(Config.xp_variant_count))
            _product_location = Utility.get_product_loc(self.driver.find_element_by_xpath(Config.xp_product_location).text)
            _product_review_count = -1

            _product_data = ProductData(
                _product_id,
                _product_name,
                _product_url,
                _product_location,
                _product_var_count,
                _product_review_count
            )
        except (expected_conditions.NoSuchElementException, exceptions.TimeoutException) as e:
            print("Couldn't load the page for product [{0}] , check your connection and retry. Error -> ".format(product_url))
            print(e)
            # Retry if encountered a problem
            if self.reload_count < Config.retry_limit:
                self.reload_count += 1
                print('Retrying..., Retry count[{0}]...'.format(self.reload_count))
                self.extract_product_page(product_url)
            else:
                # Skip the record if problem doesn't solve
                print('Reached max number of retries, skipping Product[{0}]...'.format(product_url))
                _product_data = ProductData(
                    Utility.get_product_id(product_url),
                    'Null',
                    product_url,
                    'Null',
                    -1,
                    -1
                )
                self.reload_count = 0

        # Return the temporal data holder to be saved in the DataClass
        return _product_data

    def extract_review_page(self,  product_url: str):
        # Initiate temporal data holder
        _review_data: List[ReviewData] = []
        _review_item: ReviewData = ReviewData("Null", "Null", "Null", "Null", "Null", -1, -1, "Null", "Null", "Null", "Null")
        _review_count: int = -1
        _review_pages: int = -1
        _review_count_limit = min(_review_count, Config.product_review_limit)

        print('Extracting review data for Product[{0}]'.format(product_url))
        # Go to Review Page
        try:
            self.driver.find_element_by_xpath(Config.xpb_show_reviews).click()

            WebDriverWait(self.driver, Config.element_wait).until(
                expected_conditions.presence_of_element_located((By.XPATH, Config.xp_reviews_count)))

            _review_count: int = Utility.get_review_counts(self.driver.find_element_by_xpath(Config.xp_reviews_count).text)
            _review_pages: int = Utility.get_review_pages(_review_count)
            print('Review counts[{0}] and Page counts[{1}] for Product[{2}]'.format(_review_count, _review_pages, product_url))
        except expected_conditions.NoSuchElementException as e:
            print('Couldnt open review pages for Product[{0}], Error->'.format(product_url))
            print(e)
            if self.reload_count < Config.retry_limit:
                self.reload_count += 1
                print('Retrying..., Retry count[{0}]...'.format(self.reload_count))
                self.extract_review_page(product_url)
            else:
                # Skip the record if problem doesn't solve
                print('Reached max number of retries, skipping Product[{0}]...'.format(product_url))
                self.reload_count = 0

        # return default values if there's no review available for the product
        if _review_count <= 0:
            print('Theres no review data for product[{0}]'.format(product_url))
            _review_data.append(_review_item)
            return _review_data

        # loop through review pages to get each page reviews (review page is limited by either the number of reviews or review limit of config file)
        pages_to_process = min(_review_pages, Utility.get_review_pages(Config.product_review_limit))
        for page in range(1, pages_to_process+1):
            page_review_ids: List[str] = []
            page_url: str = Utility.get_review_page_url(page, product_url)
            # c_index: int = 0

            print('Extracting Reviews of Page[{0}]'.format(page))
            # Try loading page of comments
            try:
                # Open proper review page
                self.driver.get(page_url)

                # Wait til first comment loads
                WebDriverWait(self.driver, Config.element_wait).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, Config.xp_review_at_index(1))))

                # Extract all review IDs from this page
                page_review_ids = Utility.get_page_review_ids(self.driver)
                _review_item.product_id = Utility.get_product_id(product_url)

                # Amazon doesnt provide review counts on product page, so this should be handled in review section
                self.product_data.product_review_count = _review_count

            # Retry loading the page again as long as defined in the config file
            except (expected_conditions.NoSuchElementException, exceptions.TimeoutException) as e:
                print('Couldnt load Page[{0}] of comments for the Product[{1}], Error->'.format(page, product_url))
                print(e)
                if self.reload_count < Config.retry_limit:
                    self.reload_count += 1
                    print('Retrying..., Retry count[{0}]...'.format(self.reload_count))
                    self.extract_review_page(product_url)
                else:
                    # Skip the record if problem doesn't solve
                    print('Reached max number of retries, skipping Product[{0}]...'.format(product_url))
                    self.reload_count = 0

            # loop through available comments on page
            print('page_review_ids length is [{0}]'.format(len(page_review_ids)))
            for review in range(len(page_review_ids)):
                print('Extracting Review[{0}] of Page[{1}]'.format(review+1, page))

                # Try extracting each comment on selected page
                try:
                    # Obey review limit
                    if (page >= pages_to_process) and ((review+1) > Utility.get_review_count_on_last_page(_review_count_limit)):
                        break
                    _rid: str = page_review_ids[review]
                    print('Review ID is [{0}] for Product ID [{1}]'.format(_rid, _review_item.product_id))
                    _review_id = _rid
                    _product_id = _review_item.product_id
                    _review_author = self.driver.find_element_by_xpath(Config.xp_review_author_by_id(_rid)).text
                    _review_title = self.driver.find_element_by_xpath(Config.xp_review_title_by_id(_rid)).text
                    _review_context = self.driver.find_element_by_xpath(Config.xp_review_context_by_id(_rid)).text
                    _review_rate = Utility.get_review_rate(self.driver.find_element_by_xpath(Config.xp_review_rate_by_id(_rid)).get_attribute('title'))
                    _review_score = Utility.get_review_score(self.driver.find_element_by_xpath(Config.xp_review_score_by_id(_rid)).text)
                    _review_var = self.driver.find_element_by_xpath(Config.xp_review_variant_concatenated_by_id(_rid)).text
                    _review_date = Utility.get_review_date(self.driver.find_element_by_xpath(Config.xp_review_loc_dat_info_by_id(_rid)).text)
                    _review_loc = Utility.get_review_loc(self.driver.find_element_by_xpath(Config.xp_review_loc_dat_info_by_id(_rid)).text)
                    _review_type = Utility.get_review_type(self.driver, _rid)

                    _review_item = ReviewData(
                        _product_id,
                        _review_id,
                        _review_author,
                        _review_title,
                        _review_context,
                        _review_rate,
                        _review_score,
                        _review_var,
                        _review_type,
                        _review_date,
                        _review_loc
                    )
                    _review_data.append(_review_item)
                except expected_conditions.NoSuchElementException as e:
                    # Record RID and PID in the form of 'Failed Operation' review item (to know which review failed)
                    _rid = page_review_ids[review]
                    _pid = _review_item.product_id
                    _review_item = ReviewData(_pid, _rid, "Null", "Null", "Null", -1, -1, "Null", "Null", "Null", "Null")
                    _review_data.append(_review_item)
                    print('Couldnt extract Review[{0}] on Page[{1}] for Product[{2}], Error->'.format(review, page, page_url))
                    print(e)

        # Return review either if it was successful or not
        return _review_data

    def extract_review_single(self, product_id: str, review_id: str):
        review_specific_url = 'https://www.amazon.com/gp/customer-reviews/{0}/ref=cm_cr_arp_d_rvw_ttl?ie=UTF8&ASIN={1}'.format(review_id, product_id)
        _review_item: ReviewData = ReviewData(product_id, review_id, "Null", "Null", "Null", -1, -1, "Null", "Null", "Null", "Null")

        print('Extracting single Review with ID of [{0}] and Product ID of [{1}]'.format(review_id, product_id))
        try:
            self.driver.get(review_specific_url)

            WebDriverWait(self.driver, Config.element_wait).until(expected_conditions.presence_of_element_located(
                (By.XPATH, Config.xp_review_s_author(review_id))))

            _review_item.review_author = self.driver.find_element_by_xpath(Config.xp_review_s_author(review_id)).text
            _review_item.review_title = self.driver.find_element_by_xpath(Config.xp_review_s_title(review_id)).text
            _review_item.review_context = self.driver.find_element_by_xpath(Config.xp_review_s_context(review_id)).text
            _review_item.review_rate = Utility.get_review_rate(self.driver.find_element_by_xpath(Config.xp_review_s_rate(review_id)).get_attribute('title'))
            _review_item.review_score = Utility.get_review_score(self.driver.find_element_by_xpath(Config.xp_review_s_score(review_id)).text)
            _review_item.review_var = self.driver.find_element_by_xpath(Config.xp_review_s_variant_concatenated(review_id)).text
            _review_item.review_date = Utility.get_review_date(self.driver.find_element_by_xpath(Config.xp_review_s_loc_dat(review_id)).text)
            _review_item.review_loc = Utility.get_review_loc(self.driver.find_element_by_xpath(Config.xp_review_s_loc_dat(review_id)).text)
            _review_item.review_type = Utility.get_review_type(self.driver, review_id)
        except Exception as e:
            print('Couldnt extract data for Review[{0}] of Product[{1}], Error->'.format(review_id, product_id))
            print(e)
            if self.reload_count < Config.retry_limit:
                self.reload_count += 1
                print('Retrying..., Retry count[{0}]...'.format(self.reload_count))
                self.extract_review_single(product_id, review_id)
            else:
                # Skip the record if problem doesn't solve
                print('Reached max number of retries, skipping Review[{0}] of Product[{1}]...'.format(review_id, product_id))
                self.reload_count = 0

        return _review_item



    def fix_faulty_reviews(self):
        _review_data: List[ReviewData] = []
        _review_item: ReviewData = ReviewData("Null", "Null", "Null", "Null", "Null", -1, -1, "Null", "Null", "Null", "Null")

        print('Fixing faulty review records...')
        # Read and Import from Database
        c = self.database.cursor()
        c.execute('''SELECT * FROM Reviews WHERE Author = ? AND Title = ? AND Context = ?''', ['Null', 'Null', 'Null'])
        results = c.fetchall()
        print('There are [{0}] faulty records!'.format(len(results)))

        # Cache all faulty records into a DataClass list
        for result in results:
            print('Faulty record -> [{0}]'.format(result))
            _review_data.append(ReviewData(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10]))

        # Extract selected review Individually
        for review in range(len(_review_data)):
            # Keep PID and RID if data gathering failed again
            _review_item.product_id = _review_data[review].product_id
            _review_item.review_id = _review_data[review].review_id
            # Scrap Data
            _review_item = self.extract_review_single(_review_data[review].product_id, _review_data[review].review_id)

            print('Writing back revised review record [{0}]'.format(review))
            # Write back fixed records to Database via UPDATE
            c.execute(
                '''UPDATE Reviews SET ID_Product = ?, ID_Review = ?, Author = ?, Title = ?, Context = ?, Rate = ?,Score = ?, Variation = ?, Type = ?, Date = ?, Location = ? WHERE ID_Product = ? AND ID_Review = ?''',
                [_review_item.product_id, _review_item.review_id, _review_item.review_author, _review_item.review_title,
                 _review_item.review_context, _review_item.review_rate, _review_item.review_score,
                 _review_item.review_var, _review_item.review_type, _review_item.review_date, _review_item.review_loc,
                 _review_item.product_id, _review_item.review_id])

        self.database.commit()

    def export_database_to_csv(self):
        self.database = Utility.initiate_database()
        Utility.convert_sql_to_cvs(self.database)
        self.database.close()


