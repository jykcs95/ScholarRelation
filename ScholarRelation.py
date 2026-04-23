from pyorcid import OrcidAuthentication, OrcidSearch, OrcidScrapper
import orcid
from dotenv import load_dotenv
from dataclasses import dataclass   
import os
import json

@dataclass
class Author:
    first_name: str
    middle_name: str
    last_name: str
    count: int

#store json data from the api call
def storeData(data):
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

#load json data from the file if needed
def loadData():
    with open("data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

#getting the put-codes from the works data
def extract_put_codes(works_data: list) -> list:
    return [
        work_summary["put-code"]
        for work in works_data
        if isinstance(work, dict)
        for group in work.get("group", [])
        for work_summary in group.get("work-summary", [])
        if "put-code" in work_summary
    ]

#parse a full name into first name, middle name, and last name
def parse_name(full_name):
    words = full_name.strip().split()
    if len(words) >= 3:
        first_name = words[0]
        last_name = words[-1]
        middle_name = " ".join(words[1:-1])
        return {
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "full_name": full_name
        }
    else:
        return {
            "first_name": words[0] if len(words) >= 1 else "",
            "middle_name": "",
            "last_name": words[-1] if len(words) >= 2 else "",
            "full_name": full_name
        }

#count how many times each contributor name appears in the works data
def get_contributors(data):
    contributor_counts = {}
    works = data if isinstance(data, list) else [data]

    for work in works:
        contributors = work.get("contributors", {}).get("contributor", [])
        for contributor in contributors:
            credit_name = contributor.get("credit-name", {}).get("value").replace("‘", "").replace("’", "")
            if not credit_name:
                continue
            parsed_name = parse_name(credit_name)
            # Use (first_name, last_name) as the key to group people with same first and last names
            key = (parsed_name["first_name"], parsed_name["last_name"])
            if key not in contributor_counts:
                contributor_counts[key] = Author(
                    first_name=parsed_name["first_name"],
                    middle_name=parsed_name["middle_name"] if parsed_name["middle_name"] else None,
                    last_name=parsed_name["last_name"],
                    count=0
                )
            contributor_counts[key].count += 1

    #sort the contributors by count in descending order
    contributor_counts = dict(sorted(contributor_counts.items(), key=lambda item: item[1].count, reverse=True))
    return contributor_counts

def apiCall(query)-> None: 
    #load environment variables from .env file
    load_dotenv()
    
    #get the ORCID ID and API KEY from environment variable
    client_id =  os.getenv("ORCID_ID") 
    client_secret = os.getenv("API_KEY")

    #create Authentication and API objects using the ORCID client ID and secret
    auth = OrcidAuthentication(client_id, client_secret)
    api = orcid.PublicAPI(client_id, client_secret, sandbox=False)

    #create a public access token using the authentication object
    access_token = auth.get_public_access_token()


    #get the first result of the search query to get the ORCID ID of the author
    result = OrcidSearch(access_token).search(query).get("expanded-result", [])[0]
    orcid_id = result["orcid-id"]

    #use the ORCID ID to get the works data of the author using the scrapper class
    scrapper = OrcidScrapper(orcid_id = orcid_id)
    works_data = scrapper.works()

    #extract the put-codes from the works data 
    put_codes = extract_put_codes(works_data)
    
    #search for each put-code to get the detailed data of each work and store it in a list
    detailed_data= []
    for put in put_codes:
        work_details = api.read_record_public(orcid_id,'work', token=access_token,put_code = put)
        detailed_data.append(work_details)

    #store the detailed data in a json file
    storeData(detailed_data)


if __name__ == "__main__":
    #Ask the user for a scholar's name
    query = input("Enter your search query: ").strip()

    #Make the API call to get the data and store it in a json file
    apiCall(query)

    #load the data from the json file
    works_data = loadData()

    #returns a dictionary of contributor names and their counts in the works data
    contributor = get_contributors(works_data)

    print("\nContributors and their counts:")
    for (first_name, last_name), author in contributor.items():
        if author.middle_name:
            print(f"{author.first_name} {author.middle_name} {author.last_name}: {author.count} contributions")
        else:
            print(f"{author.first_name} {author.last_name}: {author.count} contributions")

    #print the authors by count of appearances in the data.json file
    #print("\nAuthors by Count of Appearances:")
    #for author in authors:
        # print(f"{author.name}: {author.count} appearances, Author ID: {author.author_id}")
