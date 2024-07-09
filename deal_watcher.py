import requests
from bs4 import BeautifulSoup
import time
import random
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# AWS SNS setup
sns = boto3.client('sns', region_name='us-west-2')
sns_topic_arn = 'arn:aws:sns:us-west-2:885053922788:email-buying-group-new-deal'

# URL of the login page and dashboard
login_url = 'https://app.buyinggroup.ca/login'
dashboard_url = 'https://app.buyinggroup.ca/'

# Login credentials
username = 'iyad_okal@yahoo.com'
password = 'TJwCi68@e2yWdG@E'

# Store the latest deals
seen_deals = set()

def login(session):
    print("Fetching login page...")
    login_page = session.get(login_url)
    print(f"Login page status code: {login_page.status_code}")
    
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': '_token'})['value']
    print(f"CSRF Token: {csrf_token}")
    
    payload = {
        'email': username,
        'password': password,
        '_token': csrf_token
    }
    print("Attempting to log in...")
    response = session.post(login_url, data=payload)
    print(f"Login response status code: {response.status_code}")
    print(f"Login response URL: {response.url}")
    
    return response.status_code == 200

def get_latest_deals(session):
    print("Fetching dashboard...")
    response = session.get(dashboard_url)
    print(f"Dashboard status code: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all deal divs and print their contents
    deal_divs = soup.find_all('div', class_='group relative flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white')
    deals = []
    for deal_div in deal_divs:
        deal_title = deal_div.find('h3').get_text(strip=True)
        price = deal_div.find('p', class_='text-base font-medium text-gray-900').get_text(strip=True).replace('Price:', '')
        deals.append((deal_title, price))
    
    return deals

def send_alert(deal):
    title, price = deal
    message = f"New deal available: {title} at {price}"
    try:
        sns.publish(TopicArn=sns_topic_arn, Message=message, Subject='New Deal Alert')
        print(f"Alert sent successfully for deal: {title} at {price}")
    except NoCredentialsError:
        print("Error: No AWS credentials found.")
    except PartialCredentialsError:
        print("Error: Incomplete AWS credentials.")

def main():
    global seen_deals
    with requests.Session() as session:
        if not login(session):
            print("Login failed")
            return
        
        while True:
            current_deals = get_latest_deals(session)
            new_deals = [deal for deal in current_deals if deal not in seen_deals]
            
            for deal in new_deals:
                send_alert(deal)
                seen_deals.add(deal)
            
            sleep_time = random.randint(60, 120)  # Random time between 1 and 2 minutes
            print(f"Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)

if __name__ == "__main__":
    main()
