from bs4 import BeautifulSoup
import requests
import re #regular expression
import pandas as pd
from datetime import datetime

Keyword = "bleach" #Write the Keyword you want to search for here.

URL = "https://www.amazon.co.jp/s?k="+Keyword.replace(" ", "+")+"&rh=n%3A466280&ref=nb_sb_noss" #k="Keyword" rh="denotes the factors of query." ref="The method to get this url"
""" 
rh denotes the factors of query.
k = keyword,
n = category (Comics in this case)
p_n_condition-type = new/used
p_72 = 4 or more stars
p_85 = prime eligible
page = pagination offset(page nos).
qid = the timestamp when the query result was generated.
bbn = browse node numbers.Amazon uses a hierarchy of nodes with a number to the hierarchy to represent collections of items. Each number given is a browse node number.
rnid = random id  for browsing the node.
ie=utf8 = UTF-8 page encoding format.
"""
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
            "Accept-Encoding": "gzip, deflate, br", 
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"} #Get these from: https://httpbin.org/get



#Creating lists to hold the items information
Titles = list()
URLs = list()
Asins = list()



####################################################### Functions ############################################################################
def get_page(url):
    webpage = requests.get(url, headers=HEADERS)
    return BeautifulSoup(webpage.content, "lxml")
    


def get_page_body_articles(soup):
    return soup.find_all(class_="s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16")



def Extract_data_from_articles(page_body_articles): #pass through part of the page where items information exist
    for article in page_body_articles: #for each item (article)
        title = article.h2.text  
        url_item = "https://www.amazon.co.jp"+article.a['href'] #URL that take you to the item page
        asin = re.search(r'/[dg]p/([^/]+)', url_item, flags=re.IGNORECASE) #Reads the url_item and gets the content between ***/dp/[ASIN]/*** or ***/gp/[ASIN]/***
        if asin:
            ASIN = asin.group(1)
            print(ASIN)
            Asins.append(ASIN)
        else:
            Asins.append(None)
        print(title)
        Titles.append(title)
        print(url_item)
        URLs.append(url_item)
        



def Getnextpage(page):
    global page_num #this brings page_num as a global variable
    Num_nav_bar = page.find(class_="s-pagination-strip") #get the navigation bar at the bottom of the screen with numbers and Next btm.
    if Num_nav_bar.find(class_="s-pagination-item s-pagination-next s-pagination-disabled") is None: #if we can click on the next btn the code below executes, otherwise it goes to else
        url_next_page = 'https://www.amazon.co.jp' + str(Num_nav_bar.find(class_ = "s-pagination-item s-pagination-next s-pagination-button s-pagination-separator")['href']) #gets the link for the next page if it exists.
        page_num += 1 
        print("There is a page ", page_num) 
        print("URL is: ", url_next_page)
        return url_next_page
    else:
        print("There are no more pages.")
        return None

##################################################################### Main #########################################################################
#1st gets the webpage content from the first URL
#2nd extracts the part of the page where the items information exists
#3rd extracts the information about each item and out them in the corresponding list
#4th gets the URL of the next page, if it does not exist, then the code breaks from the loop and continues

page_num = 1
while True:
    soup = get_page(URL)
    Articles=get_page_body_articles(soup)
    Extract_data_from_articles(Articles)
    URL = Getnextpage(soup)    
    if URL is None:
        break
        
#################################################################### OUTPUT ############################################################################    
#create a dict to put data in a dataframe that become a CSV file.
Item_dict = {'Title': Titles,'ASIN': Asins, 'URL': URLs}    
df = pd.DataFrame(Item_dict)

#The name and the path of the file is defined here 
Today_Date_time = datetime.now()
Output_path = "./Output/"+Keyword+"_"+Today_Date_time.strftime("%d%m%Y_%H%M%S")+".csv"

#saves the data
df.to_csv(Output_path,index=False)