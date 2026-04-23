from utilities import orcid_api, parser

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
    orcid_api.apiCall(last_name, first_name, affiliation, id)

    #load the data from the json file
    works_data = orcid_api.loadData()

    #returns a dictionary of contributor names and their counts in the works data
    contributor = parser.getContributors(works_data)

    print("\nContributors and their counts:")
    for (first_name, last_name), author in contributor.items():
        if author.middle_name:
            print(f"{author.first_name} {author.middle_name} {author.last_name}: {author.count} contributions")
        else:
            print(f"{author.first_name} {author.last_name}: {author.count} contributions")
