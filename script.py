from scraper import start_scrapping
from store_data import load_data
from api import start_sever

start_scrapping(input("Enter Company Name: "))
load_data()
start_sever()
