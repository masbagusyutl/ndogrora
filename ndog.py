import requests
import time
import datetime
import json
import os
import sys

# Constants
BASE_URL = "https://eggo-quest.eu/api/encrypted/dmeay"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "eggo-quest.eu",
    "Origin": "https://oyster-app-4mimt.ondigitalocean.app",
    "Pragma": "no-cache",
    "Referer": "https://oyster-app-4mimt.ondigitalocean.app/",
    "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Microsoft Edge\";v=\"126\", \"Microsoft Edge WebView2\";v=\"126\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
}

# Helper functions
def login(account_id):
    url = f"{BASE_URL}/users/data/{account_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Login failed for account {account_id}. Response: {response.text}")
        return None

def claim_daily_reward(account_id):
    url = f"{BASE_URL}/dailyRewards/collect/{account_id}"
    response = requests.put(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Daily reward claim failed for account {account_id}. Response: {response.text}")
        return None

def claim_points(account_id):
    url = f"{BASE_URL}/barrel/expectation/{account_id}"
    response = requests.put(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Point claim failed for account {account_id}. Response: {response.text}")
        return None

def read_accounts(file_path):
    with open(file_path, 'r') as file:
        accounts = file.readlines()
    return [account.strip() for account in accounts]

def print_account_info(account_info):
    user = account_info['user']
    print(f"Username: {user['username']}")
    print(f"Score: {user['score']}")
    print(f"Overall Score: {user['overallScore']}")

def print_claim_info(claim_info):
    last_entrance = datetime.datetime.fromisoformat(claim_info['lastEntrance'][:-1])
    collection_time = datetime.datetime.fromisoformat(claim_info['collectionTime'][:-1])
    print(f"Last Entrance: {last_entrance.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Collection Time: {collection_time.strftime('%Y-%m-%d %H:%M:%S')}")

def print_daily_reward_info(daily_reward_info):
    print(f"Score: {daily_reward_info['score']}")
    print(f"Overall Score: {daily_reward_info['overallScore']}")
    print(f"Daily Reward: {daily_reward_info['dailyReward']}")
    print(f"Is Reward Taken: {daily_reward_info['dailyReward'][0]['isRewardTaken']}")

def countdown_timer(seconds):
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\rNext round in {remaining // 3600:02}:{(remaining % 3600) // 60:02}:{remaining % 60:02}")
        sys.stdout.flush()
        time.sleep(1)
    print("\n")

# Main function
def main():
    accounts = read_accounts('data.txt')
    total_accounts = len(accounts)
    
    while True:
        for idx, account_id in enumerate(accounts):
            print(f"Processing account {idx + 1} of {total_accounts}: {account_id}")
            
            # Login
            account_info = login(account_id)
            if not account_info:
                continue
            print_account_info(account_info)
            
            # Claim Daily Reward
            now = datetime.datetime.utcnow()
            last_claim_time = datetime.datetime.fromisoformat(account_info['user']['dailyReward'][0]['dateOfAward'][:-1])
            if (now - last_claim_time).days >= 1:
                daily_reward_info = claim_daily_reward(account_id)
                if daily_reward_info:
                    print_daily_reward_info(daily_reward_info)
                else:
                    print("Daily reward already claimed or not available yet.")
            else:
                print("Daily reward already claimed or not available yet.")
            
            # Claim Points every 2 hours
            last_entrance = datetime.datetime.fromisoformat(account_info['user']['barrel']['lastEntrance'][:-1])
            if (now - last_entrance).seconds >= 7200:
                claim_info = claim_points(account_id)
                if claim_info:
                    print_claim_info(claim_info)
                else:
                    print("Points claim not available yet or already claimed.")
            else:
                print("Points claim not available yet or already claimed.")
            
            # Wait 5 seconds before processing the next account
            time.sleep(5)
        
        # Wait 2 hours before starting the next round
        countdown_timer(7200)

if __name__ == "__main__":
    main()
