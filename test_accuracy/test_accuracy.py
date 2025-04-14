import sys
import os
import pandas as pd

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
manual_data_dir = os.path.join(parent_dir, "manual_data")
scraped_data_dir = os.path.join(parent_dir, "data")


def load_data(company_name):
    # load manual data into DataFrame
    normed_name = '_'.join(company_name.lower().split(' '))
    manual_data_path = os.path.join(manual_data_dir, f"{normed_name}_data.csv")
    manual_df = pd.read_csv(manual_data_path)
    manual_df["Partner Name"] = manual_df["Partner Name"].str.lower()
    manual_df["Links"] = manual_df["Links"].str.lower()

    # load our collected data
    company_dir = os.path.join(scraped_data_dir, f"{company_name}")
    scraped_url_path = os.path.join(company_dir, "urls.txt")
    scraped_partners_path = os.path.join(company_dir, "partners.txt")

    scraped_data = {}
    with open(scraped_url_path, "r") as f:
        scraped_data["Links"] = [line.strip().lower() for line in f.readlines()]

    with open(scraped_partners_path, "r") as f:
        scraped_data["Partner Name"] = [line.strip().lower() for line in f.readlines()]

    return manual_df, scraped_data

def get_stats(company_name):
    manual_df, scraped_data = load_data(company_name)

    num_old_partners = len(manual_df["Partner Name"])
    num_new_partners = len(scraped_data["Partner Name"])

    num_old_links = len(manual_df["Links"])
    num_new_links = len(scraped_data["Links"])
    
    print(f"*** PARTNERSHIP ANALYSIS ***")
    print(f"# of partnerships (old solution): {num_old_partners}")
    print(f"# of partnerships (new solution): {num_new_partners}")
    print(f" - {round((num_new_partners/num_old_partners) * 100, 2)}% increase -")

    print(f"\n*** Partnership name accuracy: ***")
    # TODO: normalzie naming scheme to identify more overlaps
    overlap = set(manual_df["Partner Name"]) & set(scraped_data["Partner Name"])
    print(f"There were {len(overlap)} overlaps: {overlap}")
    print(f" - Found {round((len(overlap)/num_old_partners) * 100, 2)}% of manually identified partnerships -")


    print(f"\n\n*** LINKS ANALYSIS ***")
    print(f"# of links (old solution): {num_old_links}")
    print(f"# of links (new solution): {num_new_links}")
    print(f" - {round((num_new_links/num_old_links) * 100, 2)}% increase -")

    print(f"\n*** Link accuracy: ***")
    # TODO: normalzie naming scheme to identify more overlaps
    overlap = set(manual_df["Links"]) & set(scraped_data["Links"])
    print(f"There were {len(overlap)} overlaps: {overlap}")
    print(f" - Found {round((len(overlap)/num_old_links) * 100, 2)}% of manually sourced links -")

    print(f"Old link sample: {manual_df["Links"][0:5]}")
    print(f"New link sample: {scraped_data["Links"][0:5]}")

get_stats("autodesk")