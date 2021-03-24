#!/usr/bin/env python
# coding: utf-8

# Analysis imports
from bs4 import BeautifulSoup,SoupStrainer
import pandas as pd
import urllib.parse
import requests
import datetime
import numpy
import lxml
import time
import re
import traceback

df = pd.DataFrame()
WP_recipe='([1234]\d{2})\s*[wW]*[pP]*'
WP_recipe='([1234]\d{2})\s*[wW]+[pP]+|([1234]\d{2})\s*![wW]*![pP]*'
filename = 'zonnepanelen.'+datetime.date.today().isoformat()+'.csv.xz'
start=time.time()

def jenm(df):
    shop = "jenm"
    try:
        WP_recipe='([1234]\d{2})\s*[wW]*[pP]*'
        URL='https://www.jenm-zonnepanelen.nl/zonnepanelen/'
        # Get the webpage from the URL
        response = requests.get(URL)
        # Parse the page
        soup = BeautifulSoup(response.text, "lxml")
        # Find the div block we are interested in
        identifier="container catalog"
        div = soup.find("div", {"class":identifier})
        # Grab all sub URLs
        sub_URLs= []
        for sub in div.find_all("a"):
            sub_URL = sub.get('href')
            sub_URLs.append(sub_URL)
        for sub_URL in sub_URLs:
            # Get the webpage from the URL
            response = requests.get(sub_URL)
            # Parse the page
            soup = BeautifulSoup(response.text, "lxml")
            # Find the div block we are interested in
            identifier="container collection"
            div = soup.find("div", {"class":identifier})
            identifier = "product-block"
            for info in div.find_all("div", {"class":identifier}):
                product_URL=info.find("a").get('href')
                # Get the webpage from the URL
                response = requests.get(product_URL)
                # Parse the page
                soup = BeautifulSoup(response.text, "lxml")
                identifier = "offer-holder"
                # Find the div block we are interested in
                innerdiv = soup.find("div", {"class":identifier})
                price = innerdiv.find("span", {"class":"price"}).text
                name  = innerdiv.find("div", {"class":"product-description"}).text
                m = re.search(WP_recipe, name)
                if m:
                    power = m.group(1)
                else:
                    power = 0
                data = {}
                data['Shop'] = shop
                data['Prijs'] = str.join('.',price.strip('€').split(','))
                data['Naam'] = re.sub('\n.*', '', name.strip())
                data['power'] = power
                data['URL'] = product_URL
                df = df.append(data , ignore_index=True)
    except:
        print("Skipped {}".format(shop))
    return df


def kerst_energy(df):
    shop = "kerst-energy"
    URL='https://www.kerst-energy.eu/nederlands/zonnepanelen/losse-zonnepanelen/'
    # Get the webpage from the URL
    response = requests.get(URL)
    # Parse the page
    soup = BeautifulSoup(response.text, "lxml")
    # Find the div block we are interested in
    identifier = "content_area"
    div = soup.find("div", {"id":identifier})
    sub_URLs = []
    # Grab all sub URLs
    for sub in div.find_all("a"):
        sub_URL = sub.get('href')
        if 'http://' not in sub_URL:
            sub_URL = urllib.parse.urljoin(response.url, sub_URL) 
        sub_URLs.append(sub_URL)
    # Make list of URLs unique
    sub_URLs = list(set(sub_URLs))
    for sub_URL in sub_URLs:
        # Get the webpage from the URL
        response = requests.get(sub_URL)
        # Parse the page
        soup = BeautifulSoup(response.text, "lxml")
        # Find the div block we are interested in
        identifier = "content_area"
        div = soup.find("div", {"id":identifier})
        for product in div.find_all(itemtype="http://schema.org/Product"):
            price = product.find(itemprop="price")['content']
            name = product.find(itemprop="name").get_text()
            description = div.find(itemprop="description").get_text()
            m = re.search("([1234]\d{2})\s*[wW]*[pP]*", name)
            if m:
                power = m.group(1)
            else:
                power = 0
            data = {}
            data['Shop'] = shop
            data['Prijs'] = price
            data['Naam'] = name
            data['power'] = power
            #data['Beschrijving:'] = description
            data['URL'] = sub_URL
            df = df.append(data , ignore_index=True)
    return df


def solar_bouwmarkt(df,URL):
    shop = "solar-bouwmarkt"
    # Get the webpage from the URL
    response = requests.get(URL)
    # Parse the page
    soup = BeautifulSoup(response.text, "lxml")
    
    # Find the div block we are interested in
    identifier = "info"
    for product in soup.find_all("div", {"class":identifier}):
        name = product.find("a").get_text().strip()
        price = product.find("div", {"class":"left"}).get_text().strip()
        m = re.search(WP_recipe, name)
        if m:
            power = m.group(1)
        else:
            power = 0
        data = {}
        data['Shop'] = shop
        data['Prijs'] = str.join('.',price.strip('€').replace('.','').split(','))
        data['Naam'] = name
        data['power'] = power
        data['URL'] = URL
        df = df.append(data , ignore_index=True)
    return df


def solargarant(df,URL):
    shop = "solargarant"
    WP_recipe='([1234]\d{2})\s*[wW]+[pP]+|([1234]\d{2})\s*![wW]*![pP]*'
    try:
        # Get the webpage from the URL
        response = requests.get(URL)
        # Parse the page
        soup = BeautifulSoup(response.text, "lxml")
    
        # Find the div block we are interested in
        div = soup.find("div", {"data-source":"main_loop"})
        # Get all the brand URLs
        sub_URLs = []
        for sub in div.find_all("a"):
            sub_URL = sub.get('href')
            sub_URLs.append(sub_URL)
        # Make list of URLs unique
        sub_URLs = list(set(sub_URLs))
        for sub_URL in sub_URLs:
            # Get the webpage from the URL
            response = requests.get(sub_URL)
            # Parse the page
            soup = BeautifulSoup(response.text, "lxml")
            try:
                for innerdiv in soup.select("div[data-loop]"):
                    price = innerdiv.find_all("span", {"class":"woocommerce-Price-amount amount"})[-1].text.split()[0]
                    name =  innerdiv.find("h3", {"class":"product-title"}).text
                    m = re.search(WP_recipe, name)
                    if m:
                        power = m.group(1)
                    else:
                        WP_recipe='([1234]\d{2})\s*[wW]*[pP]*'
                        m = re.search(WP_recipe, name)
                        if m:
                            power = m.group(1)
                        else:
                            power = 0
                    # Add data to dataframe
                    data = {}
                    data['Shop'] = shop
                    data['Prijs'] = str.join('.',price.strip('€').split(','))
                    data['Naam'] = name
                    data['power'] = power
                    data['URL'] = sub_URL
                    df = df.append(data , ignore_index=True)
            except AttributeError:
                pass
    except:
        print("Skipped {}".format(shop))
    return df


def stralendgroen(df,URL):
    shop = "stralendgroen"
    # Get the webpage from the URL
    response = requests.get(URL)
    # Parse the page
    soup = BeautifulSoup(response.text, "lxml")
    for product in soup.find_all("div", {"class":"col-inner"}):
        name = product.find("p", {"class":"product-title"}).get_text()
        price = product.find("span", {"class":"woocommerce-Price-amount amount"}).text.split()[-1]
        m = re.search(WP_recipe, name)
        if m:
            power = m.group(1)
        else:
            power = 0
            # Add data to dataframe
        data = {}
        data['Shop'] = shop
        data['Prijs'] = str.join('.',price.strip('€').split(','))
        data['Naam'] = name
        data['power'] = power
        data['URL'] = URL
        df = df.append(data , ignore_index=True)
    return df


def sun_solar(df,URL):
    shop = "sun_solar"
    # Get the webpage from the URL
    response = requests.get(URL)
    # Parse the page
    soup = BeautifulSoup(response.text, "lxml")
    for product in soup.find_all("div", {"class":"inner_product_header"}):
        name = product.find("h2", {"class":"woocommerce-loop-product__title"}).get_text()
        price = product.find("span", {"class":"price"}).text
        if ' ' in price:
            price = price.split()[1]
        m = re.search(WP_recipe, name)
        if m:
            power = m.group(1)
        else:
            power = 0
        # Add data to dataframe
        data = {}
        data['Shop'] = shop
        data['Prijs'] = str.join('.',price.strip('€').split(','))
        data['Naam'] = name
        data['power'] = power
        data['URL'] = URL
        df = df.append(data , ignore_index=True)
    return df


def winkelman(df,URL):
    shop = "winkelman"
    WP_recipe='([1234]\d{2})\s*[wW]+[pP]+|([1234]\d{2})\s*![wW]*![pP]*'
    try:
        # Get the webpage from the URL
        response = requests.get(URL)
        # Parse the page
        soup = BeautifulSoup(response.text, "lxml")
        for product in soup.select('[class^="product d-flex"]'):
            # Find the div block we are interested in
            innerdiv = product.find("div", {"class":"data"})
            name = innerdiv.find("div", {"class":"meta"}).get_text().strip()
            price = product.find("div", {"class":"current"}).get_text().strip()
            price = re.sub(',-','',price)
            m = re.search(WP_recipe, name)
            if m:
                power = m.group(1)
            else:
                WP_recipe='([1234]\d{2})\s*[wW]*[pP]*'
                m = re.search(WP_recipe, name)
                if m:
                    power = m.group(1)
                else:
                    power = 0
            # Add data to dataframe
            data = {}
            data['Shop'] = shop
            data['Prijs'] = str.join('.',price.strip('€').split(','))
            data['Naam'] = name
            data['power'] = power
            data['URL'] = URL
            df = df.append(data , ignore_index=True)
    except:
        print("Skipped {}".format(shop))
    return df


def euro_electronics(df,URL):
    shop = "euro-electronics.nl"
    # Get the webpage from the URL
    response = requests.get(URL)
    # Parse the page
    soup = BeautifulSoup(response.text, "lxml")
    div = soup.find("div", {"id":"ProductContainer"})
    table = div.find("table")
    for row in table.find_all('tr'):
        try:
            price = row.find("div", {"class":'incl-price'}).text.strip()
            price = re.sub('[\s*]','',price)
            price = str.join('.',price.strip('€').split(','))
            if '€' in price:
                price = price.split('€')[1]
            name = row.find("span", {"class":"Titleblock ListWithPhoto_TitleBlock"}).text.strip()
            m = re.search(WP_recipe, name)
            if m:
                power = m.group(1)
            else:
                power = 0
            data = {}
            data['Shop'] = shop
            data['Prijs'] = price
            data['Naam'] = name
            data['power'] = power
            data['URL'] = URL
            df = df.append(data , ignore_index=True)
        except:
            pass
    return df


def solar_outlet(df,URL):
    shop = "solar-outlet.nl"
    # Get the webpage from the URL
    response = requests.get(URL)
    # Parse the page
    soup = BeautifulSoup(response.text, "lxml")
    for product in soup.find_all("div", {"class":"product-block-holder"}):
        try:
            name = product.find("img")['title'].strip()
            price = product.find("div", {"class":"product-block-price"}).get_text().strip().split()[0]
            m = re.search(WP_recipe, name)
            if m:
                power = m.group(1)
            else:
                power = 0
            data = {}
            data['Shop'] = shop
            data['Prijs'] = data['Prijs'] = str.join('.',price.strip('€').split(','))
            data['Naam'] = name
            data['power'] = power
            data['URL'] = URL
            df = df.append(data , ignore_index=True)
        except:
            pass
    return df


def blijmetzonnepanelen(df,URL):
    shop = "blijmetzonnepanelen.nl"
    # Get the webpage from the URL
    response = requests.get(URL)
    # Parse the page
    soup = BeautifulSoup(response.text, "lxml")
    for product in soup.find_all("div", {"class":"product-information"}):
        try:
            name = product.find("a").get_text().strip()
            price = product.find("span", {"class":"woocommerce-Price-amount amount"}).text
            m = re.search(WP_recipe, name)
            if m:
                power = m.group(1)
            else:
                power = 0
            data = {}
            data['Shop'] = shop
            data['Prijs'] = str.join('.',price.strip('€').split(','))
            data['Naam'] = name
            data['power'] = power
            data['URL'] = URL
            df = df.append(data , ignore_index=True)
        except:
            pass
    return df


def abczonnepanelen(df,URL):
    shop = "abczonnepanelen"
    # Get the webpage from the URL
    response = requests.get(URL)
    # Parse the page
    soup = BeautifulSoup(response.text, "lxml")
    for product in soup.find_all("div", {"class":"product-card"}):
        try:
            name = product.find("h3").get_text().strip()
            price = product.find("span", {"class":"price"}).text
            if '€' in price:
                    price = price.split('€')[2]
            m = re.search(WP_recipe, name)
            if m:
                power = m.group(1)
            else:
                power = 0
            data = {}
            data['Shop'] = shop
            data['Prijs'] = str.join('.',price.strip('€').split(','))
            data['Naam'] = name
            data['power'] = power
            data['URL'] = URL
            df = df.append(data , ignore_index=True)
        except:
            pass
    return df


def zonnepanelenvoordelig(df,URL):
    shop = "zonnepanelen-voordelig"
    base_URL='https://www.zonnepanelen-voordelig.nl/contents/nl/'
    # Get the webpage from the URL
    response = requests.get(URL)
    # Parse the page
    soup = BeautifulSoup(response.text, "lxml")
    # Grab all sub URLs
    sub_URLs= []
    for sub in soup.find_all("a"):
        sub_URL = sub.get('href')
        if sub_URL and 'html' in sub_URL:
            sub_URLs.append(urllib.parse.urljoin(base_URL, sub_URL))
    sub_URLs = list(set(sub_URLs))
    for sub_URL in sub_URLs:
        try:
            # Get the webpage from the URL
            response = requests.get(sub_URL)
            # Parse the page
            soup = BeautifulSoup(response.text, "lxml")
            # Extract data from page parts
            name = soup.find('h1', {'itemprop':'name'}).text
            innerdiv = soup.find('div', {'class':'ProductPurchaseContainerInner'})
            price = innerdiv.find('meta', {'itemprop':'price'})['content']
            m = re.search(WP_recipe, name)
            if m:
                power = m.group(1)
            else:
                power = 0
            data = {}
            data['Shop'] = shop
            data['Prijs'] = price
            data['Naam'] = name
            data['power'] = power
            data['URL'] = URL
            df = df.append(data , ignore_index=True)
        except:
            print("Skipped {}".format(shop))
    return df


# Run functions that get and parse each site
df = jenm(df)

df = kerst_energy(df)

for URL in ['https://www.solar-bouwmarkt.nl/zonnepanelen/alle-zonnepanelen/','https://www.solar-bouwmarkt.nl/zonnepanelen/alle-zonnepanelen/page2.html']:
    df = solar_bouwmarkt(df,URL)

for URL in ['https://solargarant.nl/monokristallijn/','https://solargarant.nl/polykristallijn/','https://solargarant.nl/zwart-fullblack-zonnepanelen/']:
    df = solargarant(df,URL)

URL="https://stralendgroen.nl/categorie/zonnepanelen/"
df = stralendgroen(df,URL)

URL='https://www.sun-solar.nl/index.php/product-categorie/zonnepanelen/?avia_extended_shop_select=yes&product_count=45'
df = sun_solar(df,URL)

for URL in ['https://www.winkelman-zonnepanelen.nl/zonnepanelen/','https://www.winkelman-zonnepanelen.nl/zonnepanelen/page2.html']:
    df = winkelman(df,URL)

URL='https://www.euro-electronics.nl/zonnepanelen#filter:426d84a59a48254414a822135700a860'
df = euro_electronics(df,URL)

URL='https://www.solar-outlet.nl/zonnepanelen/alle-zonnepanelen/'
df = solar_outlet(df,URL)

URL='https://www.blijmetzonnepanelen.nl/product-categorie/zonnepanelen/'
df = blijmetzonnepanelen(df,URL)

for URL in ['https://www.abczonnepanelen.nl/zonnepanelen/losse-zonnepanelen/sunpower/','https://www.abczonnepanelen.nl/zonnepanelen/losse-zonnepanelen/lg-electronic/']:
    df = abczonnepanelen(df,URL)

URL='https://www.zonnepanelen-voordelig.nl/contents/phpsearch/search.php?=undefined&filterproc=filtersearch&fmt=html&pgid=d361&sub=1&searchFormSortBy=P-A&searchFormDisplayStyle=T&design=sfx-126_1&lang=nl&limitResultsPerPage=100'
df = zonnepanelenvoordelig(df,URL)

print(df)
# Clean up dataframe
df['power'] = df['power'].astype(float)
df['Prijs'] = df['Prijs'].astype(float)
df['Shop'] = df['Shop'].astype('category')
df['URL'] = df['URL'].astype('category')

#print(df.info())
# Export to file

df.to_csv(filename)
