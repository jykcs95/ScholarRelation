from pyorcid import OrcidAuthentication, OrcidSearch, OrcidScrapper
from dotenv import load_dotenv
import orcid
import os
import json


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