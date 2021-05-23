import json
import boto3
import re



expected_genres = ["Animation","Comedy","Kids","Action & Adventure","Sci-Fi & Fantasy","Reality","Drama","Crime","Mystery","Soap","Family","Documentary","News","Talk","War & Politics","Western","Romance"]
expected_genre_count = {
    "Animation": 1000,
    "Comedy": 1300,
    "Kids": 100,
    "Action & Adventure": 700,
    "Sci-Fi & Fantasy": 700,
    "Reality": 90,
    "Drama": 1400,
    "Crime": 60,
    "Mystery": 270,
    "Soap": 40,
    "Family": 140,
    "Documentary": 150,
    "News": 5,
    "Talk": 25,
    "War & Politics": 50,
    "Western": 30,
    "Romance": 10,
	}

ok_certs = {
'AU': ['C','G','PG','M','MA15+','R18+'],
'BR': ['L','10','12','14','16','18'],
'CA': ['C','C8','G','PG','14+','18+'],
'DE': ['0','6','12','16','18'],
'ES': ['Infantil','TP','7','10','12','13','16','18'],
'FR': ['NR','10','12','16','18'],
'GB': ['U','PG','12A','12','15','18'],
'NL': ['AL','6','9','12','16'],
'RU': ['0+','6+','12+','18+','16+'],
'US': ['TV-Y','TV-Y7','TV-G','TV-PG','TV-14','PG-13','TV-MA'],
'KR': ['ALL','7','12','15','19']
}

no_certs = ['AR','AT','BE','CH','CL','CO','CZ','EC','EE','GR','ID','IE','JP','LV','MX','MY','PE','PL','RO','SG','TH','TR','VE','ZA','NZ','IN','FI','PT','SE','DK','NO','HU','LT','PH','IT']

expected_movie_number = {
'AR': 1000,
'AT': 1000,
'AU': 1500,
'BE': 800,
'BR': 900,
'CA': 1300,
'CH': 700,
'CL': 700,
'CO': 900,
'CZ': 400,
'DE': 900,
'DK': 900,
'EC': 700,
'EE': 600,
'ES': 900,
'FI': 900,
'FR': 1000,
'GB': 1000,
'GR': 400,
'HU': 600,
'ID': 600,
'IE': 1000,
'IN': 600,
'IT': 800,
'JP': 800,
'LT': 600,
'LV': 600,
'MX': 800,
'MY': 300,
'NL': 800,
'NO': 800,
'NZ': 1000,
'PE': 700,
'PH': 500,
'PL': 700,
'PT': 700,
'RO': 600,
'RU': 700,
'SE': 700,
'SG': 800,
'TH': 600,
'TR': 600,
'US': 2000,
'VE': 700,
'ZA': 600,
'KR': 700,
}

def test_genre_file():
    try:
        with open('tv_genres.json') as json_file:
            genres_obj = json.load(json_file)
        genre_keys = genres_obj.keys()
        # Checking the object has the correct genres
        for genre in expected_genres:
            if genre not in genre_keys:
                return {'result': False, 'message': f"{genre} is missing from genre json file"}
        # Checking each genre is a list with more that 50 movies
        all_genres_list = []
        for genre in expected_genres:
            genre_list = genres_obj[genre]
            genre_list_count = len(genre_list)
            if type(genre_list) != list:
                return {'result': False, 'message': f"Genre - {genre} is not a list in the json file"}
            if genre_list_count < expected_genre_count[genre]:
                return {'result': False, 'message': f"Genre - {genre} does not have enough movies in it in the json file, the count is {genre_list_count} "}
            for movie in genre_list:
                all_genres_list.append(movie)
        # check the object has more than 20,000 movies in it
        if len(all_genres_list) < 5000:
            movie_count = len(all_genres_list)
            return {'result': False, 'message': f"Genre - The genres json file does not have enough movies in it.  it only has {movie_count}"}
        return {'result': True, 'message': "file OK"}
    except Exception as e:
        return {'result': False, "message": f"Genre -Error Processing file {filename}:\n {e}"}

def test_watchon_file(filename):
    try:
        with open(filename) as json_file:
            file_object = json.load(json_file)
        providers = file_object.keys()
        country = filename.split(".")[0].split("-")[1]
        all_movies_list = []
        for provider in providers:
            provider_list = file_object[provider]
            if type(provider_list) != list:
                return {'result': False, 'message': f"Provider - {filename} - {provider} is not a list in the json file"}
            if len(provider_list) < 7:
                return {'result': False, 'message': f"Provider - {filename} - {provider}  does not have enough movies in it in the json file"}
            for movie in provider_list:
                all_movies_list.append(movie)
        movie_count = len(set(all_movies_list))
        if movie_count < expected_movie_number[country]:
                return {'result': False, 'message': f"Provider - The {filename} providers json file does not have enough movies in it.  it only has {movie_count}"}
        return {'result': True, 'message': "file OK"}
    except Exception as e:
        return {'result': False, "message": f"Provider -Error Processing file {filename}:\n {e}"}

def test_certification_file(filename):
    try:
        with open(filename) as json_file:
            file_object = json.load(json_file)
        certifications = file_object.keys()
        country = filename.split(".")[0].split("-")[1]
        if country in no_certs:
            if file_object == {}:
                return {'result': True, 'message': "file OK"}
            else:
                return {'result': False, 'message': f"Certification - {filename} is expected to be empty"}
        expected_certs = ok_certs[country]
        file_certs = list(file_object.keys())
        cert_matches = 0
        for cert in file_certs:
            if cert in expected_certs:
                cert_matches = cert_matches + 1
        if cert_matches < 3:
            return {'result': False, 'message': f"Certification - {country} certifications do not match enough of the expected certs. found: {file_certs}, expected: {expected_certs}"}
        # if sorted(file_certs) != sorted(expected_certs):
            # return {'result': False, 'message': f"Certification - {country} certifications do not match the expected. found: {file_certs}, expected: {expected_certs}"}
        all_movies_list = []
        for cert in certifications:
            cert_list = file_object[cert]
            if type(cert_list) != list:
                return {'result': False, 'message': f"Certification - {filename} - {cert} is not a list in the json file"}
            if len(cert_list) < 1:
                return {'result': False, 'message': f"Certification - {filename} - {cert}  does not have enough movies in it in the json file"}
            for movie in cert_list:
                all_movies_list.append(movie)
        if len(all_movies_list) < expected_movie_number[country]:
                movie_count = len(all_movies_list)
                return {'result': False, 'message': f"Certification - The {filename} certifications json file does not have enough movies in it.  it only has {movie_count}"}
        return {'result': True, 'message': "file OK"}
    except Exception as e:
        return {'result': False, "message": f"Certification - Error Processing file {filename}:\n {e}"}


def test_provider_data():
    with open("tv_all-data-providers.json") as json_file:
        file_object = json.load(json_file)
    providers = file_object.keys()
    provider_count = len(providers)
    if provider_count < 60:
        return {'result': False, 'message': f"All Provider Data - Provider number is too low.  The count is {provider_count}"}
    for provider in providers:
        name = file_object[provider]['name']
        logo = file_object[provider]['logo']
        if type(name) != str:
            return {'result': False, 'message': f"All Provider Data - {provider} is not a string"}
        if len(name) < 2:
            return {'result': False, 'message': f"All Provider Data - {provider} is less than 2 characters"}
        if type(logo) != str:
            return {'result': False, 'message': f"All Provider Data - {provider} ({name}) logo is not a string"}
        logo_correct = re.match("https:\/\/image.tmdb.org\/t\/p\/w185\/\w+.jpg", logo)
        if not logo_correct:
            return {'result': False, 'message': f"All Provider Data - {provider} ({name}) logo name does not match the expected result, image is {logo}"}
    return {'result': True, 'message': "file OK"}

def test_movie_data():
    with open("movie-filter.json") as json_file:
        file_object = json.load(json_file)
    movie_count = len(file_object)
    if movie_count < 4000:
        return {'result': False, 'message': f"TV Data - count is too low, the count is {movie_count}"}
    for movie in file_object:
        movie_id = movie['id']
        runtime = movie['r']
        vote = movie['v']
        seasons = movie['se']
        release_date = movie['d']
        if type(movie_id) != int:
             return {'result': False, 'message': f"TV Data - ID is not an integer - {movie} "}
        if runtime < 25:
            return {'result': False, 'message': f"TV Data - Runtime is too short - {movie} "}
        if (type(vote) != int) and (type(vote) != float):
            return {'result': False, 'message': f"TV Data - Vote is not a number - {movie} "}
        if type(seasons) != int:
            return {'result': False, 'message': f"TV Data - seasons is not an integer - {movie} "}
        if len(release_date.split("-")) != 3:
            return {'result': False, 'message': f"TV Data - release Date is not the correct format - {movie} "}
    return {'result': True, 'message': "file OK"}
    
    