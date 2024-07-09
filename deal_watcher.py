import requests
from bs4 import BeautifulSoup
import time
import random
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import json
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("deal_watcher.log"),
        logging.StreamHandler()
    ]
)

# AWS SNS setup
sns = boto3.client('sns', region_name='us-west-2')
sns_topic_arn = 'arn:aws:sns:us-west-2:885053922788:email-buying-group-new-deal'

# URL of the login page and dashboard
login_url = 'https://app.buyinggroup.ca/login'
dashboard_url = 'https://app.buyinggroup.ca/dashboard'

# File to store seen deals
seen_deals_file = 'seen_deals.json'

# Store the latest deals
seen_deals = set()

def load_seen_deals():
    global seen_deals
    if os.path.exists(seen_deals_file):
        with open(seen_deals_file, 'r') as f:
            seen_deals = set(json.load(f))
    logging.info(f"Loaded {len(seen_deals)} seen deals.")

def save_seen_deals():
    with open(seen_deals_file, 'w') as f:
        json.dump(list(seen_deals), f)
    logging.info(f"Saved {len(seen_deals)} seen deals.")

def login(session):
    logging.info("Fetching login page...")
    login_page = session.get(login_url)
    logging.info(f"Login page status code: {login_page.status_code}")
    
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': '_token'})['value']
    logging.info(f"CSRF Token: {csrf_token}")
    
    payload = {
        'email': username,
        'password': password,
        '_token': csrf_token
    }
    logging.info("Attempting to log in...")
    response = session.post(login_url, data=payload)
    logging.info(f"Login response status code: {response.status_code}")
    logging.info(f"Login response URL: {response.url}")
    
    return response.status_code == 200

def get_latest_deals(session):
    logging.info("Fetching dashboard...")
    response = session.get(dashboard_url)
    logging.info(f"Dashboard status code: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all deal divs and print their contents
    deal_divs = soup.find_all('div', class_='group relative flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white')
    deals = []
    for deal_div in deal_divs:
        deal_title = deal_div.find('h3').get_text(strip=True)
        price = deal_div.find('p', class_='text-base font-medium text-gray-900').get_text(strip=True).replace('Price:', '')
        deal_id = f"{deal_title}-{price}"
        deals.append((deal_id, deal_title, price))
        logging.info(f"Found deal: {deal_title} at {price}")
    
    return deals

def send_alert(deal):
    deal_id, title, price = deal
    message = f"New deal available: {title} at {price}"
    try:
        sns.publish(TopicArn=sns_topic_arn, Message=message, Subject='New Deal Alert')
        logging.info(f"Alert sent successfully for deal: {title} at {price}")
    except NoCredentialsError:
        logging.error("Error: No AWS credentials found.")
    except PartialCredentialsError:
        logging.error("Error: Incomplete AWS credentials.")

def main():
    global seen_deals
    load_seen_deals()
    with requests.Session() as session:
        if not login(session):
            logging.error("Login failed")
            return
        
        while True:
            current_deals = get_latest_deals(session)
            new_deals = [deal for deal in current_deals if deal[0] not in seen_deals]
            
            for deal in new_deals:
                send_alert(deal)
                seen_deals.add(deal[0])
            
            save_seen_deals()
            
            sleep_time = random.randint(60, 120)  # Random time between 1 and 2 minutes
            logging.info(f"Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)

if __name__ == "__main__":
    main()
