#!/usr/bin/env python

import random
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from app import ApartmentObject
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

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
    # TO DO: Search for markets via state map
    # https://www.apartments.com/sitemap/

    # Currently limiting by https://www.apartments.com/sitemap/new-york/neighborhoods-by-city/new-york/
    site_map = request_page_content('https://www.apartments.com/sitemap/new-york/neighborhoods-by-city/new-york/')
    soup = BeautifulSoup(site_map.content, 'html.parser') if site_map is not None else None
    if soup == None:
        print('Issue finding pages of interest')
        exit(0)

    pages_of_interest = [ link.a['href'] for link in soup.find('div', class_= "linkGrid").find_all('li') ]

    return pages_of_interest

def scrape():
    search_urls = find_pages_of_interest_from_link_grid()

    for search_url in search_urls:
        listings_page = request_page_content(search_url)
        soup = BeautifulSoup(listings_page.content, 'html.parser')
        listings = soup.find_all('article', {'data-listingid':True})

        # Page pattern is https://www.apartments.com/new-york-ny/2
        # TO DO: Loop through each page
        num_of_available_pages = soup.find(class_="pageRange").string.split()[-1]

        listing_info_list = []
        for listing in listings:
            #   if already done, move on to the next listing
            #   if prop_collections.count_documents({'Prop_id':uid})!=0:
            #     print('Already scraped')
            #     continue

            listing_info = {}

            # Property name
            listing_name = listing.find(class_="property-title").string
            listing_info['name'] = listing_name

            # Address
            listing_address = listing.find(class_="property-address").string
            listing_info['address'] = listing_address

            # Listing Url
            listing_url = listing.a['href']
            listing_info['url'] = listing_url

            # Get more info from each apartment listing page
            listing_page  = request_page_content(listing_url)
            soup = BeautifulSoup(listing_page.content, 'html.parser')

            # profile_content = soup.find('div', 'profileContent')

            # Phone number
            phone = soup.find('div', 'phoneNumber').span.string
            listing_info['phone'] = phone

            # Neighborhood
            neighborhood = soup.find('a', 'neighborhood').string
            listing_info['neighborhood'] = neighborhood

            # Determine if multi unit listing or single unit listing
            # Multi unit listing has this document.getElementById('pricingView')
            # Multi unit listing example: https://www.apartments.com/the-greenpoint-brooklyn-ny/pnhp7hs/
            # Single unit listing example: https://www.apartments.com/99-varet-st-brooklyn-ny-unit-3b/hfrsz13/

            # Rent
            # Bedroom count
            # Bathroom count

            listing_info_list.append(listing_info)
            print(listing_info_list)
            exit(0)

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
    print(f'Scraped {len(apartments)} apartment rentals')
    store_apartments(apartments)

run()
