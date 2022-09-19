# =====
import varriables as v


# =====
class URL:

    def __init__(self,url:str) -> None:

        '''
        Check and define a search URL
        '''

        # check url
        assert url not in [None,''], "URL cannot be empty /:"
        assert v.LINKEDIN in url, "Seems URL is not related to Linkedin /:"
        assert 'page=' not in url, "Send the link without the page parameter buddy [0_0]"

        if url.startswith(v.NORMAL_SEARCH_URL):
            self.search_type = v.NORMAL_SEARCH
        elif url.startswith(v.SALES_SEARCH_URL):
            self.search_type = v.SALES_SEARCH
        else:
            raise AssertionError('This is not a search link on linkedin /:')
        
        self.url = url

        # set search type
        self.set_search_result_type()


    def set_search_result_type(self):

        '''
        * Check type of results like people or company etc.

        some samples:          
        -----
        sample_normal_people_url = https://www.linkedin.com/search/results/people/?keywords=developer
        difference with NORMAL_SEARCH_URL is = 'people/?keywords=developer'
        * for this case search type is "people"
        -----
        sample_normal_company_url = https://www.linkedin.com/search/results/companies/?keywords=IT
        difference with NORMAL_SEARCH_URL is = 'companies/?keywords=IT'
        * for this case search type is "companies"
        -----
        sample_sales_people_url   = https://www.linkedin.com/sales/search/people?query=(keywords:developer)
        difference with SALES_SEARCH_URL is = 'people?query=(keywords:developer)'
        * for this case the first item is "p" so search type is "people"
        -----
        sample_sales_company_url   = https://www.linkedin.com/sales/search/company?query=(keywords:IT)
        difference with SALES_SEARCH_URL is = 'company?query=(keywords:IT)'
        * for this case the first item is "c" so search type is "company"
        '''

        if self.search_type == v.NORMAL_SEARCH:
            # would be one of people,companies,schools,content or events
            result_type = self.url.rsplit(v.NORMAL_SEARCH_URL)[1].split('/')[0]
        
        elif self.search_type == v.SALES_SEARCH:
            difference = self.url.rsplit(v.SALES_SEARCH_URL)[1]
            
            if difference[:7] == 'people?':
                # means search result type is people
                result_type = 'people'

            elif difference[:8] == 'company?':
                # means search result type is company
                
                '''
                we return companies instead of company because 
                in the sales panel, it is seen as company, 
                but in the normal search, it is companies
                and to avoid additional complexity, 
                we do this so that they are all recognized as companies (:
                '''

                result_type = 'companies'
            else:
                # it's something else, so we set it 'unknown' to raise error is the next step, big brain time (:::
                result_type = difference
        
        try:
            self.result_type = v.SEARCH_TYPES[result_type]
        except KeyError:
            raise AssertionError(f"{result_type} is not a supported result type in the URL /:")