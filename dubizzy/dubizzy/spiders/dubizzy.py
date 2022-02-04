import scrapy
from scrapy.http import request
from selenium import webdriver
from dubizzy.items import DubizzyItem
from scrapy.loader import ItemLoader
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from random import randint

def more_amens(response):

        amens = []
        option = Options()
        option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
        option.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=option)

        driver.get(response)
        time.sleep(randint(10,13))
        driver.find_element_by_xpath('//*[@id="root"]/main/div[4]/div/div[1]/div/section[3]/div/button').click()

        amens_list = driver.find_element_by_xpath('//*[@id="root"]/main/div[4]/div/div[1]/div/section[3]/div/ul')
        amens_items = amens_list.find_elements_by_tag_name('li')
        for item in amens_items:
            amens.append(item.text)
        
        driver.quit()
        return amens

class DubizzySpider(scrapy.Spider):

    
    name = 'dubizzy'
    start_urls = ["https://abudhabi.dubizzle.com/en/property-for-rent/residential/apartmentflat/" + f"?page={str(i)}" if i != 0 else "https://abudhabi.dubizzle.com/en/property-for-rent/residential/apartmentflat/" for i in range(0,3)]
    #start_urls = ["https://dubai.dubizzle.com/property-for-rent/residential/apartmentflat/2021/10/26/chiller-free-for-family-only-higher-floor--2-294/?tracking_info=%7B%22userPath%22%3A%22LPV_Pos_FA_1%22%7D&funnel_subsection=LPV_Pos_FA_1&page=1"]
    

    def parse(self, response):
        products = response.css('div.ListItem__Root-sc-1i3osc0-1.hMPXKC')
        
        for product in products:

            profile_page = product.css('a.list-item-link').attrib['href']
            # print(profile_page)
            yield scrapy.Request("https://dubai.dubizzle.com" + profile_page, callback=self.product_info,dont_filter=True)

            
    
    def product_info(self, response):
   
        l = ItemLoader(item = DubizzyItem(),selector=response)
        l.add_value('link',response.request.url)
        #l.add_xpath('price','//*[@id="root"]/main/div[4]/div/div[1]/div/section[1]/div[2]/h5[1]/div/text()')
        l.add_css('price','//*[@id="root"]/main/div[4]/div/div[1]/div/section[1]/div[2]/h5[1]/div/text()')
        l.add_css('bedrooms','span[data-testid="listing-key-fact-bedrooms"]')
        l.add_css('bathrooms','span[data-testid="listing-key-fact-bathrooms"]')
        l.add_css('area','span[data-testid="listing-key-fact-size"]')
        
        
        l.add_css('location','span[data-ui-id="location"]')

        button_amens = response.css('button[class="ShowMore__Toggler-p5zknf-2 ShowMore___StyledToggler-p5zknf-3 ihixGD"]')
    
        if len(button_amens) < 2:
             l.add_css('amenities','p[class="Text__Root-sc-1q498l3-0 Text___StyledRoot-sc-1q498l3-1 jQBcNQ"]')
        else :
              l.add_value('amenities',more_amens(response.request.url))

        
        label = response.css('span.key-fact__label::text').extract()
        value = response.css('span.key-fact__value::text').extract()
        
        # turn into an iterator object and convert into dict
        details = dict(zip(label,value))
        
        l.add_value('details',details)

        # # if next_page == 'https://dubai.dubizzle.com/en/property-for-rent/residential/apartmentflat/':   
        # #     next_page = response.css('a[data-fnid="pagination-page"]')[1].attrib['href']
        
        # # if next_page is not None:
        # #     yield response.follow(next_page, callback=self.parse)
        
        yield l.load_item()
        
    
    
