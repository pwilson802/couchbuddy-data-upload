import json

def all_movies():
    with open("report-movie-filter.json") as json_file:
        file_object = json.load(json_file)
    movie_count = len(file_object)
    result = "------ All Movies ------\n\n"
    result = result + f"Count: {movie_count}\n"
    return result

def genres():
    try:
        with open('report-genres.json') as json_file:
            genres_obj = json.load(json_file)
        genre_keys = genres_obj.keys()
        result = "------ GENRES ------\n\n"
        for genre in genre_keys:
            count = len(genres_obj[genre])
            out_line = f"{genre}: {count}"
            result = result + out_line + "\n"
        return result
    except:
        return "Genre Error"

def providers(countries):
    with open("report-all-data-providers.json") as json_file:
        provider_data = json.load(json_file)
    result = "------ PROVIDERS ------\n"
    for country in countries:
        result = result + f"\n___{country}___\n"
        filename = f"report-providers-{country}.json"
        with open(filename) as json_file:
            file_object = json.load(json_file)
        providers = file_object.keys()
        all_movies = []
        for provider in providers:
            provider_name = provider_data[provider]['name']
            count = len(file_object[provider])
            for movie in file_object[provider]:
                all_movies.append(movie)
            result = result + f"{provider_name}: {count}\n"
        total = len(set(all_movies))
        result = result + f"TOTAL: {total}\n"
    return result

def certifications(countries):
    result = "------ Certifications ------\n"
    for country in countries:
        result = result + f"\n___{country}___\n"
        filename = f"report-certifications-{country}.json"
        with open(filename) as json_file:
            file_object = json.load(json_file)
        certifications = file_object.keys()
        total = 0
        for cert in certifications:
            count = len(file_object[cert])
            total += count
            result = result + f"{cert}: {count}\n"
        result = result + f"TOTAL: {total}\n"
    return result

def run_report(countries):
    result = ""
    all_movie_report = all_movies()
    result = result + all_movie_report + "\n\n\n"
    genres_report = genres()
    result = result + genres_report + "\n\n\n"
    providers_report = providers(countries)
    result = result + providers_report + "\n\n\n"
    certifications_report = certifications(countries)
    result = result + certifications_report + "\n\n\n"
    return result
