from collections import defaultdict
from dataclasses import dataclass  

@dataclass
class Author:
    first_name: str
    middle_name: str
    last_name: str
    count: int

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
def getContributors(data):
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