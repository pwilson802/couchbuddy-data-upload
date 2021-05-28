import requests
import boto3
import json
from collections import defaultdict
from boto3.dynamodb.conditions import Key, Attr
import requests
import gzip
import json
import datetime
import boto3
import os
from tests import test_genre_file, test_watchon_file, test_certification_file, test_provider_data, test_movie_data
from report import run_report
report = False

def send_email(message, subject = "Alert from CouchBuddy"):
    SENDER = "Couch Buddy Alert <alert@couchbuddy.info>"
    RECIPIENT = "pwilson802@gmail.com"
    AWS_REGION = "us-east-1"
    BODY_TEXT = message
    CHARSET = "UTF-8"
    client = boto3.client('ses',region_name=AWS_REGION)
    client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=SENDER,
        )


### Create the JSON File and movie_data ###
minimum_popularity = 4
temp_zip = "movie-export.gz"
json_file = "movie-export.json"
movie_data = []
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
day = yesterday.day
month = yesterday.month
year = yesterday.year
if month < 10:
    month = f"0{month}"

if day < 10:
    day = f"0{day}"

try:
    url = f'http://files.tmdb.org/p/exports/movie_ids_{month}_{day}_{year}.json.gz'
    myfile = requests.get(url)
    open(temp_zip , 'wb').write(myfile.content)
    with gzip.open(temp_zip, 'rb') as f:
        all_movie_data = f.readlines()
    for l in all_movie_data:
        adult, movie_id, original_title, popularity, video = json.loads(l).values()
        movie_details = json.loads(l)
        if (float(popularity) > minimum_popularity) and (adult is False):
            print(original_title, popularity)
            movie_data.append({'id': movie_id, 'original_title': original_title})
except:
    send_email("Error loading the zip file")
    # exit script

### Finished creating the JSON file ###

import datetime
dateString = datetime.datetime.now().isoformat()

movie_api = "https://api.themoviedb.org/3/movie/"
api_key = os.getenv("TMB_KEY")

all_countries = ["AR","AT","AU","BE","BR","CA","CH","CL","CO","CZ","DE","DK","EC","EE","ES","FI","FR","GB","GR","HU","ID","IE","IN","IT","JP","LT","LV","MX","MY","NL","NO","NZ","PE","PH","PL","PT","RO","RU","SE","SG","TH","TR","US","VE","ZA","KR"]

genres = defaultdict(list)
watch_on = {x: defaultdict(list) for x in all_countries}
certifications = {x: defaultdict(list) for x in all_countries}

def check_movie_details(overview, image, title, release_date, tagline, runtime, vote_average, vote_count, movie_genres):
    f_args = [overview, image, title, release_date, tagline, runtime, vote_average, vote_count, movie_genres]
    if None in f_args:
        print(f"{title} - NoneType found in movie arguments")
        return "not valid"
    if type(overview) != str:
        print(f"{title} - overview is not a string")
        return "not valid"
    if len(overview) < 10:
        print(f"{title} - overview is too short")
        return "not valid"
    if not image.startswith("/"):
        print(f"{title} - image is not valid")
        return "not valid"
    if type(title) != str:
        print(f"{title} - title is not a string")
        return "not valid"
    if len(title) < 1:
        print(f"{title} - title is too short")
        return "not valid"
    if type(tagline) != str:
        print(f"{title} - tagline is not a string")
        return "not valid"
    if type(runtime) != int:
        print(f"{title} - runtime is not an integer")
        return "not valid"
    if runtime < 25:
        print(f"{title} - runtime is too short")
        return "not valid"
    if (type(vote_average) != int) and (type(vote_average) != float):
        print(f"{title} - vote_average is not a valid number")
        return "not valid"
    if type(vote_count) != int:
        print(f"{title} - vote_count is not an integer")
        return "not valid"
    if vote_count < 14:
        print(f"{title} - vote count is too low")
        return "not valid"
    if type(movie_genres) != list:
        print(f"{title} - movie_genres is not a list")
        return "not valid"
    if len(movie_genres) < 1:
        print(f"{title} - movie_genres is empty")
        return "not valid"
    if len(release_date.split("-")) != 3:
        print(f"{title} - The release data is not valie")
        return "not valid"
    return 'valid'
    

count = 0

providers = []
movie_data_list = []

def request_data(url):
    count = 0
    while count < 10:
        try:
            response = requests.get(url)
            return url
        except:
            count = count + 1
    send_email(f"Error connecting to TMD API {url}")
    #TODO - shitdown the Server

for movie in movie_data:
    try:
        if count % 50 == 0:
            print('count:', count)
        count = count + 1
        movie_id = movie['id']
        url = f"{movie_api}{movie_id}?api_key={api_key}"
        watch_url = f"{movie_api}{movie_id}/watch/providers?api_key={api_key}"
        age_rating_url = f"{movie_api}{movie_id}/release_dates?api_key={api_key}"
        # TODO update the below to use the request_data function
        movie_info_request = requests.get(url)
        watch_info_request = requests.get(watch_url)
        age_rating_request = requests.get(age_rating_url)
        movie_info = json.loads(movie_info_request.text)
        watch_info = json.loads(watch_info_request.text)
        age_rating_info = json.loads(age_rating_request.text)['results']
        overview = movie_info['overview']
        image = movie_info['poster_path']
        title = movie_info['title']
        release_date = movie_info['release_date']
        tagline = movie_info['tagline']
        runtime = movie_info['runtime']
        vote_average = movie_info['vote_average']
        vote_count = movie_info['vote_count']
        movie_genres = [x['name'] for x in movie_info['genres']]
        check_valid = check_movie_details(overview, image, title, release_date, tagline, runtime, vote_average, vote_count, movie_genres)
        if check_valid == "not valid":
            print(f'Error: id-{movie_id} not valid')
            continue
        movie_object = {'id': movie_id,
                            "r": runtime,
                            "v": vote_average,
                            "d": release_date}
        movie_data_list.append(movie_object)
        for genre in movie_genres:
            genres[genre].append(movie_id)
        for country in watch_on.keys():
            try:
                streaming_providers = [x for x in watch_info['results'][country]['flatrate']]
                for provider in streaming_providers:
                    provider_id = provider['provider_id']
                    proivder_name = provider['provider_name']
                    provider_logo = provider['logo_path']
                    providers.append({'id': provider_id, "name": proivder_name, "logo": provider_logo})
                    watch_on[country][provider_id].append(movie_id)
            except KeyError:
                pass
                # print(f"{country} - {title} is not available for streaming")
        for country in certifications.keys():
            try:
                rating = [x for x in age_rating_info if x['iso_3166_1'] == country][0]['release_dates'][-1]['certification']
                certifications[country][rating].append(movie_id)
            except:
                pass
                # print(f"{country} - {title} - No Rating found")
    except Exception as e:
        print(e)

s3 = boto3.client('s3')
data_bucket = os.getenv("DATA_BUCKET")
found_errors = False
# Upload Genres
if report:
    with open('report-genres.json', 'w') as json_file:
        json.dump(genres, json_file)
else:
    with open('genres.json', 'w') as json_file:
        json.dump(genres, json_file)
    genre_test = test_genre_file()
    if genre_test['result']:
        s3.upload_file('genres.json', data_bucket, "genres.json")
    else:
        send_email(genre_test['message'])
        print(genre_test['message'])
        found_errors = True

# Upload Providers for each country
if report:
    for country in watch_on.keys():
        provider_filename = f"report-providers-{country}.json"
        export_data = {provider:movies for (provider,movies) in watch_on[country].items() if len(movies) > 7}
        with open(provider_filename, 'w') as json_file:
            json.dump(export_data, json_file)
else:
    for country in watch_on.keys():
        provider_filename = f"providers-{country}.json"
        data = {provider:movies for (provider,movies) in watch_on[country].items() if len(movies) > 7}
        export_data = dict(sorted(data.items(), key=lambda item: len(item[1]), reverse=True))
        with open(provider_filename, 'w') as json_file:
            json.dump(export_data, json_file)
        watch_on_test = test_watchon_file(provider_filename)
        if watch_on_test['result']:
            s3.upload_file(provider_filename, data_bucket, provider_filename)
        else:
            send_email(watch_on_test['message'])
            print(watch_on_test['message'])
            found_errors = True

ok_certs = {
    'US': ['G', 'PG', 'PG-13', 'R', 'NC-17'], 
    'CA': ['G', 'PG', '14A', '18A'], 
    'AU': ['G', 'PG', 'M', 'MA15+', 'R18+'], 
    'DE': ['0', '6', '12', '16', '18'], 
    'FR': ['U', '10', '12', '16', '18'], 
    'NZ': ['G', 'PG','13', '15', 'M', '16', '18'], 
    'IN': ['U', 'UA', 'A'], 
    'GB': ['U', 'PG', '12A', '12', '15', '18'], 
    'NL': ['AL', '6', '9', '12', '16'], 
    'BR': ['L', '10', '12', '14', '16', '18'], 
    'FI': ['S', 'K-7', 'K-12', 'K-16', 'K-18'], 
    'ES': ['APTA', '7', '12', '16', '18'], 
    'PT': ['M/3', 'M/6', 'M/12', 'M/14', 'M/16', 'M/18'], 
    'SE': ['Btl', '7', '11', '15'], 
    'DK': ['A', '7', '11', '15'], 
    'NO': ['A', '6', '9', '12', '15', '18'], 
    'HU': ['KN', '6', '12', '16', '18', 'X'], 
    'LT': ['V', 'N-7', 'N-13', 'N-16', 'N-18'], 
    'RU': ['0+', '6+', '12+', '16+', '18+'], 
    'PH': ['G', 'PG', 'R-13', 'R-16', 'R-18'], 
    'IT': ['T', 'VM14', 'VM18']
}
#  Upload certifications for each country
if report:
    for country in certifications.keys():
        certifications_filename = f"report-certifications-{country}.json"
        # if country in ok_certs.keys():
        #     export_data = {cert: movies for (cert, movies) in certifications[country].items() if cert in ok_certs[country]}
        # else:
        export_data = certifications[country]
        with open(certifications_filename, 'w') as json_file:
            json.dump(export_data, json_file)
else:
    for country in certifications.keys():
        certifications_filename = f"certifications-{country}.json"
        if country in ok_certs.keys():
            data = {cert: movies for (cert, movies) in certifications[country].items() if cert in ok_certs[country]}
            export_data = {}
            for cert in ok_certs[country]:
                if cert in data.keys():
                    export_data[cert] = data[cert]
        else:
            export_data = {}
        with open(certifications_filename, 'w') as json_file:
            json.dump(export_data, json_file)
        certifications_test = test_certification_file(certifications_filename)
        if certifications_test['result']:
            s3.upload_file(certifications_filename, data_bucket, certifications_filename)
        else:
            send_email(certifications_test['message'])
            print(certifications_test['message'])
            found_errors = True

# Upload all provider information
uniq_providers = [i for n, i in enumerate(providers) if i not in providers[n + 1:]]
providers_dict = {}
for provider in uniq_providers:
    providers_dict[provider['id']] = {}
    providers_dict[provider['id']]['name'] = provider['name']
    providers_dict[provider['id']]['logo'] = "https://image.tmdb.org/t/p/w185" + provider['logo']

if report:
    with open('report-all-data-providers.json', 'w') as json_file:
        json.dump(providers_dict, json_file)
else:
    with open('all-data-providers.json', 'w') as json_file:
        json.dump(providers_dict, json_file)
    all_provider_test = test_provider_data()
    if all_provider_test['result']:
        s3.upload_file('all-data-providers.json', data_bucket, "all-data-providers.json")
    else:
        send_email(all_provider_test['message'])
        print(all_provider_test['message'])
        found_errors = True

if report:
    with open('report-movie-filter.json', 'w') as json_file:
        json.dump(movie_data_list, json_file) 
else:
    with open('movie-filter.json', 'w') as json_file:
        json.dump(movie_data_list, json_file)
    movie_filter_test = test_movie_data()
    if movie_filter_test['result']:
        s3.upload_file('movie-filter.json', data_bucket, "movie-filter.json")
    else:
        send_email(movie_filter_test['message'])
        print(movie_filter_test['message'])
        found_errors = True

if report:
    countries = watch_on.keys()
    export_report = run_report(countries)
    send_email(export_report, 'CouchBuddy Report')
else:
    with open("movie-filter.json") as json_file:
        file_object = json.load(json_file)
    send_email(f"{len(file_object)} movies have been loaded", 'Data Refresh')