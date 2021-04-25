import json
import boto3
import re



expected_genres = ['Crime', 'Comedy', 'Adventure', 'Action', 'Science Fiction', 'Animation', 'Family', 'Drama', 'Romance', 'Mystery', 'Fantasy', 'Thriller', 'War', 'Music', 'Western', 'History', 'Horror', 'Documentary']
expected_genre_count = {
	"Drama": 12000,
	"Romance": 3000,
	"Crime": 2000,
	"Comedy": 8000,
	"Action": 3500,
	"Thriller": 4500,
	"Adventure": 1500,
	"Science Fiction": 1200,
	"Animation": 900,
	"Family": 1000,
	"Mystery": 2000,
	"Horror": 2500,
	"Fantasy": 1000,
	"Documentary": 800,
	"War": 400,
	"Music": 500,
	"Western": 200,
	"History": 400,
	"TV Movie": 700,
	}

ok_certs = {
    'US': ['G', 'PG-13', 'R', 'NC-17', 'PG'], 
    'CA': ['18A', 'G', 'PG', '14A'], 
    'AU': ['G', 'PG', 'M', 'MA15+', 'R18+'], 
    'DE': ['0', '6', '12', '16', '18'], 
    'FR': ['U', '12', '10', '16', '18'], 
    'NZ': ['M', '13', '15', 'G', 'PG', '16', '18'], 
    'IN': ['U', 'UA', 'A'], 
    'GB': ['15', 'U', 'PG', '12A', '12', '18'], 
    'NL': ['AL', '6', '9', '12', '16'], 
    'BR': ['L', '10', '12', '14', '16', '18'], 
    'FI': ['S', 'K-7', 'K-12', 'K-16', 'K-18'], 
    'ES': ['APTA', '7', '12', '16', '18'], 
    'PT': ['M/3', 'M/6', 'M/12', 'M/14', 'M/16', 'M/18'], 
    'SE': ['Btl', '7', '11', '15'], 
    'DK': ['A', '7', '11', '15'], 
    'NO': ['A', '6', '9', '12', '15', '18'], 
    'HU': ['KN', '6', '12', '16', '18'], 
    'LT': ['V', 'N-7', 'N-13', 'N-16', 'N-18'], 
    'RU': ['0+', '6+', '12+', '16+', '18+'], 
    'PH': ['G', 'PG', 'R-13', 'R-16', 'R-18'], 
    'IT': ['T', 'VM14', 'VM18'],
}

no_certs = ['AR','AT','BE','CH','CL','CO','CZ','EC','EE','GR','ID','IE','JP','LV','MX','MY','PE','PL','RO','SG','TH','TR','VE','ZA','KR']

expected_movie_number = {
'AR': 4000,
'AT': 4000,
'AU': 3000,
'BE': 3000,
'BR': 2000,
'CA': 700,
'CH': 700,
'CL': 3000,
'CO': 3000,
'CZ': 1000,
'DE': 6000,
'DK': 1000,
'EC': 1000,
'EE': 1000,
'ES': 1000,
'FI': 300,
'FR': 3000,
'GB': 5000,
'GR': 1000,
'HU': 800,
'ID': 2000,
'IE': 2000,
'IN': 200,
'IT': 1000,
'JP': 2000,
'LT': 200,
'LV': 1000,
'MX': 2000,
'MY': 5,
'NL': 2000,
'NO': 200,
'NZ': 100,
'PE': 2000,
'PH': 20,
'PL': 1000,
'PT': 1000,
'RO': 1000,
'RU': 1000,
'SE': 1000,
'SG': 2000,
'TH': 1000,
'TR': 1000,
'US': 9000,
'VE': 2000,
'ZA': 1000,
'KR': 2000,
}

def test_genre_file():
    try:
        with open('genres.json') as json_file:
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
        if len(all_genres_list) < 20000:
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
    with open("all-data-providers.json") as json_file:
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
    if movie_count < 24000:
        return {'result': False, 'message': f"Movie Data - count is too low, the count is {movie_count}"}
    for movie in file_object:
        movie_id = movie['id']
        runtime = movie['r']
        vote = movie['v']
        if type(movie_id) != int:
             return {'result': False, 'message': f"Movie Data - ID is not an integer - {movie} "}
        if runtime < 25:
            return {'result': False, 'message': f"Movie Data - Runtime is too short - {movie} "}
        if (type(vote) != int) and (type(vote) != float):
            return {'result': False, 'message': f"Movie Data - Vote is not a number - {movie} "}
    return {'result': True, 'message': "file OK"}
    
    