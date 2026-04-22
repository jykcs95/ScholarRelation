import serpapi
from dotenv import load_dotenv
import os
import json


#store json data from the api call
def storeData(data):
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

#load json data from the file
def loadData():
    with open("data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data
    
#make api call to google scholar and store the results in a json file
def apiCall(query):
    load_dotenv() #load environment variables from .env file
    api =  os.getenv("API_KEY") #get the API key from environment variable
    client = serpapi.Client(api_key=api)
    results = client.search({
        "engine": "google_scholar",
        "q": query,
        "start": 0, #starting index of the results, 0 for the first page
        "num": 20 #number of results to return, max is 20
    })
    storeData(results.as_dict())

#use author's name as a key while author's id and count is the value in a dictionary
def get_author_id_map(data) -> dict:
    author_id_map = {}
    
    #store list of dictionaries of authors in the data, didn't want nested for loops
    all_authors = []
    for result in data.get("organic_results", []):
        all_authors.extend(result.get("publication_info", {}).get("authors", []))
    
    #iterate through the list of authors and store the author id and count in the author_id_map dictionary
    for author in all_authors:
        name = author.get("name")
        author_id = author.get("author_id")
        #if they do not have author's id, because they have not created public profile then we will ignore them
        if name and author_id:
            if name in author_id_map:
                author_id_map[name]["count"] += 1
                author_id_map[name]["author_id"] = author_id
            else:
                author_id_map[name] = {"author_id": author_id, "count": 1}
    return author_id_map

if __name__ == "__main__":
    query = input("Enter your search query: ").strip()

    apiCall(query)

    data = loadData()
    author_id_map = get_author_id_map(data)
        
    #sort the author_id_map dictionary by count in descending order
    sorted_author_id_map = dict(sorted(author_id_map.items(), key=lambda item: item[1]["count"], reverse=True))

    #print the authors by count of appearances in the data.json file
    print("\nAuthors by Count of Appearances:")
    for i, (author_name, info) in enumerate(sorted_author_id_map.items()):
        print(f"{author_name}: {info['count']} appearances, Author ID: {info['author_id']}")    
