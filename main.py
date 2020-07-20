from bs4 import BeautifulSoup as bs
import requests
import boto3
import os, json, re


session = boto3.Session(profile_name="default")
client = boto3.client('s3')
listbucket = client.list_buckets()

CONFIG = {
    'client_id' : os.environ.get('CLIENT_ID'),
    'client_secret' : os.environ.get('CLIENT_SECRET'),
    'access_token' : os.environ.get('ACCESS_TOKEN'),
    'token_url' : 'https://id.twitch.tv/oauth2/token',
    'grant_type' : 'client_credentials',
    'validate_token' : 'https://id.twitch.tv/oauth2/validate',
    'scopes' : []
}

base_url = 'https://api.twitch.tv/helix/'
user_list= 'aws'

def get_twitch_token():
    response = requests.post(f"https://id.twitch.tv/oauth2/token?client_id={CONFIG['client_id']}&client_secret={CONFIG['client_secret']}&grant_type=client_credentials").json()['access_token']
    print(f"export ACCESS_TOKEN='{response}'") # add this to your .env file and run source
    
def validate_token():
    headers = {'Authorization': f"OAuth {CONFIG['access_token']}"}
    response = requests.get(CONFIG['validate_token'], headers=headers)
    print(response.json())


def get_user_id():
    url = base_url + "users?login=" + user_list
    headers = {
        'Client-ID' : CONFIG['client_id'],
        'Authorization' : f"Bearer {CONFIG['access_token']}"
    }
    r = requests.get(url, headers=headers)
    user_id = r.json()['data'][0]['id']
    
    return user_id

def get_top_daily_clips():
    user_id = get_user_id()
    limit = 2
    start_date = str("2020-07-11T00:00:01Z")
    end_date = str("2020-07-11T23:59:59Z")
    clips = []
    url = f"{base_url}clips?broadcaster_id={user_id}&first={limit}&started_at={start_date}&ended_at={end_date}"
    print()
    headers = {
        'Client-ID' : CONFIG['client_id'],
        'Authorization' : f"Bearer {CONFIG['access_token']}"
    }
    r = requests.get(url, headers=headers).json()['data']
    for i in r:
        clips.append(i['url'])
    
    print(clips)
    return clips

def web_scrape_clips():
    # clips = get_top_daily_clips()
    url = 'https://clips.twitch.tv/KnottyBlightedKangarooNerfRedBlaster'
    res = requests.get(url)
    soup = bs(res.text)
    print(soup.prettify())
    

def post_to_bucket():
    bucketname = listbucket['Buckets'][0]['Name']
    response = client.put_object(
        Body = '/Users/johnbaltazar/Desktop/Test.png',
        Bucket = bucketname,
        Key = 'tmp/output/Test.png',
        StorageClass = 'STANDARD_IA'
    )
    print(response)

def main():
    print(os.environ)

if __name__ == '__main__':
    
    if os.environ.get('ACCESS_TOKEN') is None:
        get_twitch_token()
    web_scrape_clips()
    # get_top_daily_clips()