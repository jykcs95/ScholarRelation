# ScholarRelation

ScholarRelation is a research utility designed to bridge the gap between academic work and contributor identification. By leveraging the **ORCID Public API**, it allows users to search for scholars by name, affiliation, or specific ORCID IDs to visualize collaboration networks and contribution counts.

## ✨ Features

- **Flexible Search:** Query contributors using a specific **ORCID iD** or search by **First Name**, **Last Name**, and **Institutional Affiliation**.
- **Contributor Analytics:** Automatically parses academic works associated with an ORCID profile to return a dictionary of collaborators and their total contribution counts.
- **Middle Name Support:** Specifically handles and displays middle names to ensure accurate scholar identification.
- **JSON Data Persistence:** Stores API call results locally for offline analysis and faster subsequent loads.

## 🚀 Getting Started

### Prerequisites
Ensure you have Python installed, along with the `requests` library for API communication.
```bash
pip install requests
```

### Usage
Run the main script to start an interactive search session:
```bash
python main.py
```
1. **Search by ID:** Enter a 16-digit ORCID iD (e.g., `0000-0002-1825-0097`) to pull data for a specific scholar.
2. **Search by Name:** Press **Enter** on the ID prompt to search by `First Name`, `Last Name`, and `Affiliation`.
3. **View Results:** The program will print a ranked list of contributors and their contribution totals.

## 🛠️ Project Structure

- `main.py`: The entry point for the interactive user interface.
- `utilities/orcid_api.py`: Handles all direct communication with the **ORCID Public API** and JSON data loading.
- `utilities/parser.py`: Contains the logic to extract and count contributors from the academic works data.

## 📖 Use Cases
This tool is particularly useful for researchers who need to:
- **Map Collaboration Networks:** See which researchers frequently work together.
- **Verify Affiliations:** Confirm the professional standing and institutional history of potential collaborators.
- **Authorship Verification:** Generate accurate counts of contributions for grant reporting or academic dossiers.

## ⚖️ License
Distributed under the MIT License.
