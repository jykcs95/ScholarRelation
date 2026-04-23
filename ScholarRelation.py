import serpapi
from dotenv import load_dotenv
from dataclasses import dataclass   
import os
import json

@dataclass
class Author:
    name: str
    author_id: str
    count: int

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
def get_authors(data):
    authors_dict = {}
    
    #store list of dictionaries of authors in the data, didn't want nested for loops, does end up using extra space
    all_authors = []
    for result in data.get("organic_results", []):
        all_authors.extend(result.get("publication_info", {}).get("authors", []))
    
    #iterate through the list of authors and store the author id and count in the author_id_map dictionary
    for author in all_authors:
        name = author.get("name")
        author_id = author.get("author_id")
        #if they do not have author's id, because they have not created public profile then we will ignore them
        if name:
            if name in authors_dict:
                authors_dict[name].count += 1
                if author_id:
                    authors_dict[name].author_id = author_id
            else:
                authors_dict[name] = Author(name=name, author_id=author_id, count=1)
    
    authors_list = list(authors_dict.values())
    authors_list.sort(key=lambda a: a.count, reverse=True)
    return authors_list

if __name__ == "__main__":
    query = input("Enter your search query: ").strip()

    apiCall(query)

    data = loadData()

    #returns a list of Author objects
    authors = get_authors(data)

    #print the authors by count of appearances in the data.json file
    print("\nAuthors by Count of Appearances:")
    for author in authors:
        print(f"{author.name}: {author.count} appearances, Author ID: {author.author_id}")
