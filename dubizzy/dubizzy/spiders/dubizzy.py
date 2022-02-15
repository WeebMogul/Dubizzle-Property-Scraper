import scrapy
from scrapy.http import request
from selenium import webdriver
from dubizzy.items import DubizzyItem
from scrapy.loader import ItemLoader
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from random import randint

# use selenium if there is a 'see more' button in the amenities section
def more_amens(response):

        # activate the driver
        amens = []
        option = Options()
        option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
        option.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=option)

        driver.get(response)

        # wait for the site to load
        time.sleep(randint(10,13))

        # click the "see more" button
        driver.find_element_by_xpath('//*[@id="root"]/main/div[4]/div/div[1]/div/section[3]/div/button').click()

        # extract all the amenities available
        amens_list = driver.find_element_by_xpath('//*[@id="root"]/main/div[4]/div/div[1]/div/section[3]/div/ul')
        amens_items = amens_list.find_elements_by_tag_name('li')
        for item in amens_items:
            amens.append(item.text)
        
        # tell driver to quit and return the amenities collection
        driver.quit()
        return amens

class DubizzySpider(scrapy.Spider):

    
    name = 'dubizzy'
    
    # accept user input for number of pages to extract
    def __init__(self,page_no,url = "https://abudhabi.dubizzle.com/en/property-for-rent/residential/apartmentflat/"):
        self.page_no = int(page_no)
        self.start_urls = [url + f"?page={str(i)}" if i != 0 else url for i in range(0,self.page_no)]

    # Gather all the list of properties available 
    def parse(self, response):
        products = response.css('div.ListItem__Root-sc-1i3osc0-1.hMPXKC')
        
        # get link to the property page
        for product in products:
            profile_page = product.css('a.list-item-link').attrib['href']

            # request callback to product_info to get data of all features of the property.
            yield scrapy.Request("https://dubai.dubizzle.com" + profile_page, callback=self.product_info,dont_filter=True)

            
    
    # function to get all the features of the properties like price, bathrooms etc.
    def product_info(self, response):

        # Use itemloader for cleaner extraction of data for the features.
        l = ItemLoader(item = DubizzyItem(),selector=response)

        # link to the profile of the apartment
        l.add_value('link',response.request.url)

        # price of the apartment
        l.add_xpath('price','//*[@id="root"]/main/div[4]/div/div[1]/div/section[1]/div[2]/h5[1]/div/text()')

        # number of bedrooms
        l.add_css('bedrooms','span[data-testid="listing-key-fact-bedrooms"]')

        # number of bathrooms
        l.add_css('bathrooms','span[data-testid="listing-key-fact-bathrooms"]')

        # area of the property
        l.add_css('area','span[data-testid="listing-key-fact-size"]')
        
        # location of the property
        l.add_css('location','span[data-ui-id="location"]')

        # see more buttion in the amenities section
        button_amens = response.css('button[class="ShowMore__Toggler-p5zknf-2 ShowMore___StyledToggler-p5zknf-3 ihixGD"]')

        # if there is no button, get the amenities present. If there is the "see more" button, send it to the more_amens function
        if len(button_amens) < 2:
             l.add_css('amenities','p[class="Text__Root-sc-1q498l3-0 Text___StyledRoot-sc-1q498l3-1 jQBcNQ"]')
        else :
              l.add_value('amenities',more_amens(response.request.url))

        # extract all the property info from the property info section
        label = response.css('span.key-fact__label::text').extract()
        value = response.css('span.key-fact__value::text').extract()
        
        # turn into an iterator object and convert into dict
        details = dict(zip(label,value))
        
        # send it to the itemloader
        for key,value in details.items():
            l.add_value(key.replace(' ','_').lower(),value)
        
        # output all the list of items to the .csv file
        yield l.load_item()
        
    
    
