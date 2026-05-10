import os
import csv
import json

def build_consolidated_dataset():
    base_dir = r"c:\Users\anish\Desktop\dooma\scratch\companywise-dsa-interview-question"
    companies_data = {}

    if not os.path.exists(base_dir):
        print("Repo not found")
        return

    # Look for all folders (companies)
    for company in os.listdir(base_dir):
        company_path = os.path.join(base_dir, company)
        if os.path.isdir(company_path) and company != ".git":
            # We will just parse all.csv for each company if it exists
            all_csv_path = os.path.join(company_path, "all.csv")
            if os.path.exists(all_csv_path):
                questions = []
                with open(all_csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        questions.append({
                            "id": row.get("ID", ""),
                            "title": row.get("Title", ""),
                            "url": row.get("URL", ""),
                            "difficulty": row.get("Difficulty", ""),
                            "frequency": row.get("Frequency %", "")
                        })
                if questions:
                    companies_data[company] = questions

    # Save to a consolidated file
    output_path = r"c:\Users\anish\Desktop\dooma\scratch\consolidated_companies.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(companies_data, f, indent=2)

    print(f"Processed {len(companies_data)} companies.")
    total_q = sum(len(q) for q in companies_data.values())
    print(f"Total question mappings: {total_q}")

if __name__ == "__main__":
    build_consolidated_dataset()
