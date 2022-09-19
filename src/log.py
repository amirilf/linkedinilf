import logging

class Log:

    def __init__(self,filename) -> None:
        logging.basicConfig(filename=filename, filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

    def record(self,content):
        logging.info(content)

