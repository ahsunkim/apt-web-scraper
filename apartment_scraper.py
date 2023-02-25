#!/usr/bin/env python

import random
import requests
import time
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from app import ApartmentObject
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from utils import rent_sanitizer

def request_page_content(url):
    # Needs user agent in order to access link
    # TO-DO: Make this part more robust
    user_agent_list = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    ]

    user_agent = random.choice(user_agent_list)
    headers  = {'User-Agent':user_agent}
    try:
        response = requests.get(url, timeout = 10, headers = headers)
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error making request to {url}: {e}")
        return None

def find_pages_of_interest_from_link_grid():
    # TO-DO: Search for markets via state map
    # https://www.apartments.com/sitemap/

    # Currently limiting by https://www.apartments.com/sitemap/new-york/neighborhoods-by-city/new-york/
    site_map = request_page_content('https://www.apartments.com/sitemap/new-york/neighborhoods-by-city/new-york/')
    soup = BeautifulSoup(site_map.content, 'html.parser') if site_map is not None else None
    if soup == None:
        print('Issue finding pages of interest')
        exit(0)

    pages_of_interest = [ link.a['href'] for link in soup.find('div', class_= "linkGrid").find_all('li') ]

    # return pages_of_interest
    return ['https://www.apartments.com/greenpoint-brooklyn-ny/']

def scrape():
    search_urls = find_pages_of_interest_from_link_grid()

    for search_url in search_urls:
        listings_page = request_page_content(search_url)
        soup = BeautifulSoup(listings_page.content, 'html.parser')
        listings = soup.select('article:not(.reinforcement)[data-listingid]')

        # Page pattern is https://www.apartments.com/new-york-ny/2
        # TO-DO: Loop through each page
        num_of_available_pages = soup.find(class_="pageRange").string.split()[-1]

        listing_info_list = []

        for listing in listings:
            # TO-DO: Add logic to dedupe listings (if already done, move on to the next listing)

            # Property name
            listing_name = listing.find(class_="property-title").string if listing.find(class_="property-title") is not None else ''

            # Address
            listing_address = listing.find(class_="property-address").string

            # Listing Url
            listing_url = listing.find(class_='property-link')['href']
            print(listing_url)

            # Get more info from each apartment listing page
            listing_page  = request_page_content(listing_url)
            soup = BeautifulSoup(listing_page.content, 'html.parser')

            # Phone number
            phone = soup.find('div', 'phoneNumber').span.string if soup.find('div', 'phoneNumber') else ''

            # Neighborhood
            neighborhood = soup.find('a', 'neighborhood').string

            # Determine if multi unit listing or single unit listing
            # Multi unit listing has this document.getElementById('pricingView')
            # Multi unit listing example: https://www.apartments.com/the-greenpoint-brooklyn-ny/pnhp7hs/
            # Single unit listing example: https://www.apartments.com/99-varet-st-brooklyn-ny-unit-3b/hfrsz13/

            if soup.find(id='pricingView') is None:
                # Single unit listing
                listing_info = {}
                single_unit_info = soup.find_all('p', 'rentInfoDetail')

                # Sanitize values
                rent = rent_sanitizer(single_unit_info[0].string)
                bedroom = 0 if single_unit_info[1].string.split()[0] == 'Studio' else float(single_unit_info[1].string.split()[0])
                bathroom = float(single_unit_info[2].string.split()[0])
                size = 0 if single_unit_info[3].string is None else int(single_unit_info[3].string.split()[0].replace(',', ''))

                listing_info['name'] = listing_name
                listing_info['address'] = listing_address
                listing_info['url'] = listing_url
                listing_info['phone'] = phone
                listing_info['neighborhood'] = neighborhood
                listing_info['rent'] = rent
                listing_info['bedroom'] = bedroom
                listing_info['bathroom'] = bathroom
                listing_info['size'] = size

                listing_info_list.append(listing_info)
            else:
                # Multi unit listing - 2 page formats found
                if soup.find_all('li', 'unitContainer'):
                    all_units_tab_only = soup.find(attrs={'data-tab-content-id':'all'})
                    for unit in all_units_tab_only.find_all('li', 'unitContainer'):
                        listing_info = {}
                        listing_info['name'] = listing_name

                        details = unit.select('span:not(.screenReaderOnly)')
                        # details = list(unit.find_all('span'))
                        print(details)
                        exit(0)

                        unit_model = details[7].text
                        listing_info['address'] = listing_address + ' ' + unit_model

                        rent = rent_sanitizer(details[2].text)
                        listing_info['rent'] = rent

                        # bedroom = 0
                        # bathroom = 0
                        # listing_info['bedroom'] = bedroom
                        # listing_info['bathroom'] = bathroom
                        size = 0 if details[4].text is None else int(details[4].text.split()[0].replace(',', ''))
                        listing_info['size'] = size

                        listing_info['url'] = listing_url
                        listing_info['phone'] = phone
                        listing_info['neighborhood'] = neighborhood
                        listing_info_list.append(listing_info)
                elif soup.find_all('div', 'priceBedRangeInfo'):
                    price_bed_range_info_divs = soup.find_all('div', 'priceBedRangeInfo')
                    for unit in price_bed_range_info_divs:
                        listing_info = {}
                        listing_info['name'] = listing_name

                        unit_model = unit.find('span', 'modelName').string
                        listing_info['address'] = listing_address + ' ' + unit_model

                        rent = rent_sanitizer(unit.find('span', 'rentLabel').string)
                        listing_info['rent'] = rent

                        details = list(unit.find('h4', 'detailsLabel').span.children)

                        bedroom = 0 if details[1].text.split()[0] == 'Studio' else float(details[1].text.split()[0])
                        bathroom = float(details[3].text.split()[0])
                        size = 0 if details[5].text is None else int(details[5].text.split()[0].replace(',', ''))

                        listing_info['bedroom'] = bedroom
                        listing_info['bathroom'] = bathroom
                        listing_info['size'] = size

                        listing_info['url'] = listing_url
                        listing_info['phone'] = phone
                        listing_info['neighborhood'] = neighborhood
                        listing_info_list.append(listing_info)

                # print(listing_info_list)
                # exit(0)

            # controlling the request rate
            time.sleep(1)

        return listing_info_list



def store_apartments(apartments_list):
    engine = create_engine('postgresql+psycopg2://username:password@localhost/apartments')
    Session = sessionmaker(bind=engine, client_encoding='utf8')
    session = Session()

    for apartment_data in apartments_list:
        apartment = ApartmentObject(**apartment_data)
        session.add(apartment)


def run():
    apartments = scrape()
    print(apartments)
    print(f'Scraped {len(apartments)} apartment rentals')
    # store_apartments(apartments)

run()
