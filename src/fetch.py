# =====
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from os.path import exists
from time import sleep
from bs4 import BeautifulSoup

import varriables as v
from url import URL
from config import Config
from log import Log



# =====
class FetchData:

    def __init__(self,config_obj:Config,url:str,page:int,how_many_pages:int=1, output:int=v.TXT_OUTPUT, output_name:str='output',separator:str='^^^',log:bool=True,log_file:str='logs.log') -> str:
        
        '''
        By using this class, we can pull out the desired page information
        
        * config_obj     => a Config object to use selenium
        * url            => rquested url address
        * page           => the number of the page you want to check
        * how_many_pages => determine how many pages you want to load
        * output         => type of output [TXT or CSV]
        * output_name    => output file name
        * separator      => if output=TXT, items will be seprated by this
        * log            => True means there will be a log file to check procces
        * log_file       => log file name
        
        ---
        
        Note:
        - If log file already exist, it will be replaced!
        - Just specify the file name, its format will be set automatically
        - If you wanna define the seprator, choose something unique 
        and special so that you can easily process the information later (:
        '''

        # validation
        assert page >= 1, "The page can only be 1 or more (0_0)"
        assert how_many_pages >= 1, "The number of pages you want to load must be 1 or more!"
        assert type(config_obj) == Config, "the config u passed is not a Config object ):"
        assert not exists(output_name + v.FILE_FORMATS[output]), f"{output_name + v.FILE_FORMATS[output]} already exists, do something buddy /: "


        if log:
            self.log = Log(log_file).record
        else:
            self.log = None

        self.url_obj     = URL(url)
        self.config_obj  = config_obj
        self.output_path = output_name + v.FILE_FORMATS[output]
        self.page        = page
        self.separator    = separator

        '''
        self.page_until is one more than the requested number of pages, but since we will use it in the range, it is useful for us
        and we just write: 
            range(self.page,self.page_until)
        '''
        self.page_until = page + how_many_pages


        '''        
        - We store these values in this way so that when we reach the
        stage of checking and retrieving information from the pages,
        we can call the certain func only by having the dictionary key
        and do not use 1000 if and else to call the functions /:

        - At least for now, this method is simpler and more logical
        for me than checking all situations (:
        '''

        self.FETCH_FUNCS = {
        f'{v.NORMAL_SEARCH}{v.PEOPLE_RESULTS}'   : self.fetch_data_people_normal,
        f'{v.NORMAL_SEARCH}{v.COMPANIES_RESULTS}': self.fetch_data_companies_normal,
        f'{v.NORMAL_SEARCH}{v.SCHOOLS_RESULTS}'  : 1,
        f'{v.NORMAL_SEARCH}{v.CONTENT_RESULTS}'  : 1,
        f'{v.NORMAL_SEARCH}{v.EVENTS_RESULTS}'   : 1,
        f'{v.NORMAL_SEARCH}{v.COURSES_RESULTS}'  : 1,

        f'{v.SALES_SEARCH}{v.PEOPLE_RESULTS}'    : self.fetch_data_people_sales,
        f'{v.SALES_SEARCH}{v.COMPANIES_RESULTS}' : 1,
        }

    def save_data(self,data:list) -> None:

        '''
        It takes the final data and saves it in the file
        '''

        with open(self.output_path,'a') as file:
            for item in data:
                file.write(self.separator.join(filter(None,list(item.values())))+'\n')

    def main(self):

        '''
        The whole process starts and ends in this function with this order:
        
        1. load index linkedin page and add li_at cookie 
        2. get sources
        3. pass sources and fetch information
        4. save all information
        5. do logging
        '''

        # 1
        self.config_obj.driver.get('https://linkedin.com')
        self.config_obj.driver.add_cookie({'name':'li_at','value':self.config_obj.li_at})

        # for each page
        for page_number in range(self.page,self.page_until):
            
            # 2
            source = self.get_source(page_number)
            
            # 3
            data  = self.connector(source)

            # 4
            self.save_data(data)

            # 5
            if self.log != None:
                self.log(f'{len(data)} items from page : {page_number} saved successfully')

    def get_source(self,page_number) -> str:

        '''
        Extract page source
        '''
        
        # add the page number to the end of the url string       
        requested_url = self.url_obj.url + f'&page={page_number}'

        self.config_obj.driver.get(requested_url)

        # The methods of loading all the data on each page that LinkedIn works with Ajax are different
        if self.url_obj.search_type == v.NORMAL_SEARCH:

            total_height = int(self.config_obj.driver.execute_script("return document.body.scrollHeight"))
            # scroll down to load all 10 data which linkedin shows with Ajax
            # 1/3 2/3 3/3 scroll in window
            for ii in range(1,4):
                self.config_obj.driver.execute_script("window.scrollTo(0, {});".format(total_height / 3 * ii))
                sleep(0.5)
        
        elif self.url_obj.search_type == v.SALES_SEARCH:
            WebDriverWait(self.config_obj.driver, 15).until(
                EC.presence_of_element_located((By.ID, "search-results-container"))
            )
            # scroll down the scrollbar
            # 1/10 2/10 ...
            for ii in range(1,11):
                self.config_obj.driver.execute_script(f"var element = document.getElementById('search-results-container');element.scrollTop = element.scrollHeight / 10 * {ii};")
                sleep(0.5)

        # with open('r.html','w') as file:
        #     file.write(self.config_obj.driver.page_source)
        return self.config_obj.driver.page_source

    def connector(self,source) -> list:

        '''
        This is just a connector function that sends the page source
        to the related function according to result_type and search_type of the URL
        and returns the fetched data
        '''
        
        return self.FETCH_FUNCS[f'{self.url_obj.search_type}{self.url_obj.result_type}'](source)

    def fetch_data_people_sales(self,source) -> list:

        '''
        Receive، fetch and return the items of page source in
        a list contains the dictionaries of each item

        sample output => [ { 'name' : 'example', 'title': 'example', }, ... ]

        including this information:
            - name
            - title
            - location
            - connection
            - about (short version)
            - experience
            - time in role
            - time in company
            - account link
            - company link

        * to see a sample result from linkedin just search this:
        * https://www.linkedin.com/sales/search/people?query=(keywords:developer)
        '''

        items = []

        soup = BeautifulSoup(source,'lxml')

        box = soup.find_all('div',class_='flex flex-column')
        
        for item in box:
            top_section = item.find('div',class_='artdeco-entity-lockup__content ember-view')
            down_section = item.find('div',class_='ml8 pl1').dl.find_all('div',class_='inline-flex align-items-baseline')

            name = top_section.div.div.a.text.strip().title()
            account_link = v.LINKEDIN + top_section.div.div.a['href'].split('?')[0]
            connection = top_section.find('span',class_='artdeco-entity-lockup__degree').text.strip().replace(u'\xa0', u' ').split(' ')[1]
            title = ' '.join(list(filter(None, [i.text.strip() for i in top_section.find("div",{"class":"artdeco-entity-lockup__subtitle ember-view t-14"})])))

            try:
                company_link = (v.LINKEDIN + top_section.find("div",{"class":"artdeco-entity-lockup__subtitle ember-view t-14"}).a['href']).split('?')[0]
            except:
                company_link = None

            time_role,time_company = list(filter(None, [i.text.strip() for i in top_section.find("div",{"class":"artdeco-entity-lockup__metadata ember-view"})]))
            location = top_section.find("div",{"class":"artdeco-entity-lockup__caption ember-view"}).span.text

            about = None
            experience = None

            for i in down_section:
                if i.dt.text.strip()[:-1] == 'About':
                    text = i.dd.div.text.strip().replace(u'\n', u' ').replace(u'\t', u' ')
                    if 'see more' in text:
                        text = text[:-8]
                    about = text
                elif i.dt.text.strip()[:-1] == 'Experience':
                    experience = ' '.join(list(filter(None,i.dd.text.strip().replace(u'\n', u' ').replace(u'\t', u' ').split(' '))))

            items.append({
                'name'        :name,
                'title'       :title,
                'location'    :location,
                'connection'  :connection,
                'about'       :about,
                'experience'  :experience,
                'time_role'   :time_role,
                'time_company':time_company,
                'account_link':account_link,
                'company_link':company_link
            })
        
        return items

    def fetch_data_people_normal(self,source) -> list:

        '''
        Receive، fetch and return the items of page source

        sample output => [ { 'name' : 'example', 'title': 'example', }, ... ]

        including this information:
            - name
            - title
            - location
            - connection
            - account link

        * to see a sample result from Linkedin just search this:
        * https://www.linkedin.com/search/results/people/?keywords=developer
        '''

        items = []

        soup = BeautifulSoup(source,'lxml')
        
        box = soup.find_all('div',class_='mb1')

        for item in box:

            top_section = item.find('span',class_='entity-result__title-text t-16')
            down_section = item.find('div',class_='linked-area flex-1 cursor-pointer').find_all("div")

            name = top_section.a.span.span.text.strip()
            connection = top_section.div.span.span.text.strip().split(' ')[1]
            account_link = top_section.a['href'].strip().split('?')[0]
            title = down_section[0].text.strip()
            location = down_section[1].text.strip()
            
            items.append({
                'name'        :name,
                'title'       :title,
                'location'    :location,
                'connection'  :connection,
                'account_link':account_link,
            })

        return items

    def fetch_data_companies_normal(self,source) -> list:

        '''
        Receive، fetch and return the items of page source

        sample output => [ { 'name' : 'example', 'title': 'example', }, ... ]

        including this information:
            - company name
            - title
            - about
            - location
            - followers
            - jobs
            - company link

        * to see a sample result from Linkedin just search this:
        * https://www.linkedin.com/search/results/companies/?keywords=IT
        '''

        items = []

        soup = BeautifulSoup(source,'lxml')
        
        box = soup.find_all('div',class_='entity-result__content entity-result__divider pt3 pb3 t-12 t-black--light')
        
        for item in box:

            title_section = item.div.find('div',class_='entity-result__primary-subtitle t-14 t-black t-normal').text.strip()
            
            if '•' in title_section:
                title,location = title_section.replace(u'• ',u' ').split('  ')
            else:
                title = title_section
                location = None

            company_name = item.div.div.text.strip()        
            followers = item.div.find('div',class_='entity-result__secondary-subtitle t-14 t-normal').text.strip()
            jobs = item.find_all('div',class_='entity-result__simple-insight-text-container')[-1].text.replace(u'\n',u'').strip()
            company_link = item.a['href']
            
            try:
                about = item.find('p',class_='entity-result__summary entity-result__summary--2-lines t-12 t-black--light mb1').text.replace(u'\n',u'').strip()
            except:
                about = None

            items.append({
                'company_name':company_name,
                'title'       :title,
                'about'       :about,
                'location'    :location,
                'followers'   :followers,
                'jobs'        :jobs,
                'company_link':company_link
            })
        
        return items
