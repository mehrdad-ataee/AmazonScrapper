# =============================== I/O ======================================
output_database_name = 'Laptops'
products_links_source_name = 'LaptopsLinks.txt'
# ============================ Addresses =================================== xp:XPath, xpb:XPath Button
# == Product Page
xp_product_name = '//*[@id="productTitle"]'
xp_product_location = '//*[@id="cm-cr-local-reviews-title"]/h3'
xp_variant_parent = '//*[@id="twister"]'
xp_variant_count = '//*[@id="twister"]/div'
def xp_variant_of(v_index: int): return xp_variant_count + '[{0}]'.format(str(v_index))
def xp_variant_item_count_of(v_index: int): return str(xp_variant_of(v_index)) + '/ul/li'
def xp_variant_item_of(v_index: int, i_index: int): return xp_variant_item_count_of(v_index) + '[{0}]'.format(str(i_index))

xpb_show_reviews = '//*[@id="cr-pagination-footer-0"]/a'

# == Reviews Page
xp_reviews_count = '//*[@id="filter-info-section"]/div/span'
xp_reviews_location = '//*[@id="cm_cr-review_list"]/h3'
xp_reviews_list = '//*[@id="cm_cr-review_list"]//*[@data-hook="review"]'
def xp_review_at_index(index: int): return xp_reviews_list + '[{0}]'.format(str(index))
def xp_review_root_by_id(id: str): return '//*[@id="{0}"]'.format(id)
def xp_review_author_by_id(id: str): return xp_review_root_by_id(id) + '//*[@data-hook="genome-widget"]//*[@class="a-profile-name"]'
def xp_review_rate_by_id(id: str): return xp_review_root_by_id(id) + '//*[@class="a-row"]//*[@class="a-link-normal"]'
def xp_review_title_by_id(id: str): return xp_review_root_by_id(id) + '//*[@class="a-row"]//*[@data-hook="review-title"]/span'
def xp_review_loc_dat_info_by_id(id: str): return xp_review_root_by_id(id) + '//*[@data-hook="review-date"]'
def xp_review_misc_info_by_id(id: str): return xp_review_root_by_id(id) + '//*[@class="a-row a-spacing-mini review-data review-format-strip"]'
def xp_review_variant_individual_by_id(id: str, v_index: int): return xp_review_misc_info_by_id(id) + '/a/text()' + '[{0}]'.format(str(v_index))
def xp_review_variant_concatenated_by_id(id: str): return xp_review_misc_info_by_id(id) + '/a'
def xp_review_context_by_id(id: str): return xp_review_root_by_id(id) + '//*[@class="a-row a-spacing-small review-data"]/span/span'
def xp_review_score_by_id(id: str): return '//*[@class="a-row review-comments comments-for-{0}"]'.format(str(id))

# == Review Item Page
def xp_review_s_author(id: str): return '//*[@id="customer_review-{0}"]/div[1]/a/div[2]/span'.format(id)
def xp_review_s_title(id: str): return '//*[@id="customer_review-{0}"]/div[2]/a[2]/span'.format(id)
def xp_review_s_rate(id: str): return '//*[@id="customer_review-{0}"]/div[2]/a[1]'.format(id)
def xp_review_s_loc_dat(id: str): return ''
def xp_review_s_variant_concatenated(id: str): return ''
def xp_review_s_misc_info(id: str): return ''
def xp_review_s_context(id: str): return '//*[@id="customer_review-{0}"]/div[4]/span/span'.format(id)
def xp_review_s_score(id: str): return ''
# ============================ Settings ===================================
# which driver to use: 'Chrome' | 'Firefox'
driver_name = 'Chrome'
# Lunch driver in headless mode? (default: 1)
driver_is_headless = 1
# Page loading strategy -> ('normal' wait till the entire page is loaded | 'eager' only loads initial HTML | 'none' wait until the initial page is downloaded)
page_load_strategy = 'normal'
# How many reviews get extracted from each provided product? (default: 100)
product_review_limit = 200
# How Many Seconds to Wait for a Page to Load? [1,...,n] default(240/30)
page_wait = 60
# How Many Seconds to Wait for an Element to Load? [1,...,n] default(10)
element_wait = 20
# How Many Times to Reload the Page Before Skipping it? [0,...,n] default(3)
retry_limit = 3
