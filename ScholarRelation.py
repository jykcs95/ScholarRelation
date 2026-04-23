from pyorcid import OrcidAuthentication, OrcidSearch, OrcidScrapper
import orcid
from dotenv import load_dotenv
from dataclasses import dataclass   
from collections import defaultdict
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
    full_name = full_name.strip()

    #Checks if the data stored has the last name, first name format
    if "," in full_name:
        # Assume format "Last Name, First Name"
        parts = full_name.split(",", 1)
        last_name = parts[0].strip()
        first_name = parts[1].strip()
        middle_name = ""
        return {
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name
        }
    else:
        words = full_name.split()
        #Assuming the first word is the first name, the last word is the last name, and anything in between is the middle name
        if len(words) >= 3:
            first_name = words[0]
            last_name = words[-1]
            middle_name = " ".join(words[1:-1])
            return {
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name
            }
        #If there are only two words, we can assume that there is no middle name
        else:
            return {
                "first_name": words[0] if len(words) >= 1 else "",
                "middle_name": "",
                "last_name": words[-1] if len(words) >= 2 else ""
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

    # Merge all similar contributors for each last name
    contributors_by_last = defaultdict(list)
    for key, author in contributor_counts.items():
        contributors_by_last[key[1]].append((key[0], key, author))
    
    keys_to_remove = []
    for last, entries in contributors_by_last.items():
        if len(entries) > 1:
            # Sort by quality: full names first (no "."), then by length of first_name descending
            def sort_key(x):
                first = x[0]
                if "." not in first:
                    return (0, -len(first))  # full names prioritized, longer first names better
                else:
                    return (1, -len(first))  # initials second, longer initials better
            entries.sort(key=sort_key)
            
            # Get the best candidate for author's name and add all the count to it
            best_first, best_key, best_author = entries[0]
            for first, key, author in entries[1:]:
                best_author.count += author.count
                keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del contributor_counts[key]

    #sort the contributors by count in descending order
    contributor_counts = dict(sorted(contributor_counts.items(), key=lambda item: item[1].count, reverse=True))
    return contributor_counts

# Calling the Orcid API to figure out user's orcid ID which will allow us to search and store individuals work detailed data 
def apiCall(last_name, first_name, affiliation, id = None)-> None: 
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

    #Prompt the search query based on available data
    match (bool(id), bool(affiliation)):
        case (True, _):
            search_query = f"orcid:{id}"
        case (False, True):
            search_query = f"affiliation-org-name:{affiliation} AND family-name:{last_name} AND given-names:{first_name}"
        case (False, False):
            search_query = f"family-name:{last_name} AND given-names:{first_name}"

    #get the first result of the search query to get the ORCID ID of the author
    result = OrcidSearch(access_token).search(search_query).get("expanded-result", [])
    orcid_id = None
    if result:
        orcid_id = result[0]["orcid-id"]

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
    #Ask the user to search either by ORCID ID or by name and affiliation
    id = input("Enter ORCID ID (or press Enter to search by name and affiliation): ").strip()

    if id:
        first_name = ""
        last_name = ""
        affiliation = ""
    else:
        first_name = input("Enter first name: ").strip()
        last_name = input("Enter last name: ").strip()
        affiliation = input("Enter affiliation: ").strip()

    #Make the API call to get the data and store it in a json file
    apiCall(last_name, first_name, affiliation, id)

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
