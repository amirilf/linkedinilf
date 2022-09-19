# linkedin links
LINKEDIN = 'https://www.linkedin.com'
NORMAL_SEARCH_URL = LINKEDIN + '/search/results/'
SALES_SEARCH_URL   = LINKEDIN + '/sales/search/'

# search types
NORMAL_SEARCH = 5
SALES_SEARCH  = 6

# types of search results
PEOPLE_RESULTS    = 7
COMPANIES_RESULTS = 8
SCHOOLS_RESULTS   = 9
CONTENT_RESULTS   = 10
EVENTS_RESULTS    = 11
COURSES_RESULTS   = 12

SEARCH_TYPES = {
    'people':   PEOPLE_RESULTS,
    'companies':COMPANIES_RESULTS,
    'schools':  SCHOOLS_RESULTS,
    'content':  CONTENT_RESULTS,
    'events':   EVENTS_RESULTS,
    'learning': COURSES_RESULTS,
}


# browser types
FIREFOX_BROWSER = 3
CHROME_BROWSER = 4

# output types
CSV_OUTPUT = 1
TXT_OUTPUT = 2

FILE_FORMATS = {
    TXT_OUTPUT:'.txt',
    CSV_OUTPUT:'.csv'
}