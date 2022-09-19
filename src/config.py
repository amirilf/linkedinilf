# =====
from selenium.webdriver.chrome.options import Options as chrome_option
from selenium.webdriver.firefox.service import Service as firefox_service
from selenium.webdriver.firefox.options import Options as firefox_option
from selenium import webdriver
from os.path import exists
from requests import get as req
import varriables as v


# =====
class Config():
        
    def __init__(self, driver_name:int, driver_path:str, li_at:str) -> None:

        '''
        * driver_name => type of browser [FIREFOX_BROWSER or CHROME_BROWSER]
        * driver_path => web driver path
        * li_at is your unique cookie in linkedin
        '''

        # check configs
        assert driver_name in [v.FIREFOX_BROWSER,v.CHROME_BROWSER], "Driver name must be Firefox or Chrome (:"
        assert self.check_driver(driver_path), "The driver is not found in this path, where is it dude /:"
        assert li_at not in [None,''], "li_at can not be empty /:"
        assert self.check_li_at(li_at), "The entered li_at doesn't work /:::"

        # set configs
        self.driver_name = driver_name
        self.driver_path = driver_path
        self.li_at = li_at
        self.driver_obj = None

    def check_driver(self,path:str) -> bool:
        '''
        Check if the driver file exist
        '''
        return exists(path)

    def check_li_at(self,li_at) -> bool:
        '''
        Check the correctness of li_at
        '''

        cookies = {
        'li_at':li_at,
        }

        res = req('https://linkedin.com/signup', cookies=cookies)
        
        # if li_at is correct, linkedin will redirect us to /feed url
        if 'feed' in res:
            return True
        return True

    @property
    def driver(self):

        '''
        Return the webdriver object with its preferences

        Preferences are for increasing page loading speed, 
        we add some preferences such as not downloading fonts, photos and css files
        '''

        if self.driver_obj is None:

            # define sevice
            service = firefox_service(self.driver_path)

            if self.driver_name == v.FIREFOX_BROWSER:

                # preferences
                options = firefox_option()
                options.set_preference("browser.display.use_document_fonts", 0)
                options.set_preference('permissions.default.stylesheet', 2)
                options.set_preference('permissions.default.image', 2)
                
                # driver
                self.driver_obj =  webdriver.Firefox(service=service, options=options)

            else:
                # self.driver_name is equal v.CHROME_BROWSER

                # preferences
                options = chrome_option()
                prefs = {
                    "browser.display.use_document_fonts" : 0, 
                    'permissions.default.stylesheet': 2,
                    'permissions.default.image': 2,
                    }
                options.add_experimental_option('prefs',prefs)
                
                # driver
                self.driver_obj = webdriver.Chrome(service=service,options=options)
        
        return self.driver_obj