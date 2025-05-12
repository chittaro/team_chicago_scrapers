import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from interface.backend.supabaseClient import supabase_backend
from supabase import PostgrestAPIError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for table names
PARTNERSHIPS_TABLE = 'partnerships'
PARTNERSHIP_CATEGORIES_TABLE = 'partnership_categories'
CATEGORY_SETTINGS_TABLE = 'category_settings'

def fetch_partnership_data(company_name):
    """Fetches all partnership data for a specified company name."""
    try:
        # Query to fetch all partnership data for the given company
        response = (
            supabase_backend.table(PARTNERSHIPS_TABLE)
            .select("*")
            .eq("company_name", company_name)
            .execute()
        )

        if response.data:
            logger.info(f"Fetched {len(response.data)} partnerships for {company_name}.")
            return response.data
        else:
            logger.warning(f"No partnerships found for {company_name}.")
            return []

    except Exception as e:
        logger.error(f"Unexpected error fetching partnership data for {company_name}: {e}")
        return []
    
def fetch_all_partnership_data():
    """Fetches all partnership data (company names and their details) from the partnerships table."""
    try:
        # Query to fetch all data from the partnerships table
        response = (
            supabase_backend.table(PARTNERSHIPS_TABLE)
            .select("*")  # Select all columns
            .execute()
        )

        if response.data:
            logger.info(f"Fetched {len(response.data)} partnerships.")
            return response.data
        else:
            logger.warning("No partnership data found.")
            return []

    except Exception as e:
        logger.error(f"Unexpected error fetching all partnership data: {e}")
        return []

def store_partnership_data(partnership_data):
    """Saves or updates partnership data entries."""
    if len(partnership_data) == 0:
        logger.error("No data to save.")
        return None

    company_name = partnership_data[0]["company_name"]

    try:
        # 1. Delete existing partnerships for the company
        delete_response = (
            supabase_backend.table(PARTNERSHIPS_TABLE)
            .delete()
            .eq("company_name", company_name)
            .execute()
        )
        logger.info(f"Deleted existing partnerships for {company_name}. Response: {delete_response}")

        # 2. Insert new partnership data
        insert_response = (
            supabase_backend.table(PARTNERSHIPS_TABLE)
            .insert(partnership_data)
            .execute()
        )
        if not insert_response.data:
            logger.error(f"Failed to save partnership data for {company_name}. Response: {insert_response}")
            return None
        
        logger.info(f"Saved partnership data for {company_name}.")
        return insert_response.data

    except Exception as e:
        logger.error(f"Unexpected error saving partnership data for {company_name}: {e}")
        return None


# --- NEW Functions for Settings Page (partnership_categories & category_settings tables) ---

def get_partnership_type_defs():
    """Fetches all partnership categories and their associated settings."""
    try:
        response = (
            supabase_backend.table(PARTNERSHIP_CATEGORIES_TABLE)
            .select("id, name, category_settings(id, category_id, definition, is_enabled, updated_at)") # Joins with category_settings
            .execute()
        )
        if response.data:
            # Transform data to match frontend expectations (name, definition, is_enabled, id for category)
            partnership_types = {}
            for category in response.data:
                setting = category.get('category_settings')[0] if category.get('category_settings') else {}
                if setting.get('is_enabled', True):
                    name = category['name']
                    definition = setting.get('definition', '')
                    partnership_types[name] = definition

            return partnership_types
        logger.info("No category settings found or empty response.")
        return []
    except PostgrestAPIError as e:
        logger.error(f"Supabase API Error fetching category settings: {e.message}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching category settings: {e}")
        return []


def add_new_category(name, definition="", is_enabled=True):
    """Adds a new partnership category and its initial setting."""
    try:
        # 1. Add to partnership_categories table
        category_response = (
            supabase_backend.table(PARTNERSHIP_CATEGORIES_TABLE)
            .insert({"name": name})
            .execute()
        )
        if not category_response.data:
            logger.error(f"Failed to add new category '{name}'. Response: {category_response}")
            return None
        
        new_category = category_response.data[0]
        category_id = new_category['id']

        # 2. Add to category_settings table
        setting_response = (
            supabase_backend.table(CATEGORY_SETTINGS_TABLE)
            .insert({
                "category_id": category_id,
                "definition": definition,
                "is_enabled": is_enabled
            })
            .execute()
        )
        if not setting_response.data:
            logger.error(f"Failed to add settings for new category '{name}'. Response: {setting_response}")
            # Attempt to clean up by deleting the category if settings failed
            supabase_backend.table(PARTNERSHIP_CATEGORIES_TABLE).delete().eq("id", category_id).execute()
            return None

        # Return a combined object similar to get_all_category_settings format
        return {
            'id': category_id,
            'name': new_category['name'],
            'definition': setting_response.data[0]['definition'],
            'is_enabled': setting_response.data[0]['is_enabled'],
            'setting_id': setting_response.data[0]['id']
        }
    except PostgrestAPIError as e:
        if '23505' in str(e.code): # Unique violation for category name
             logger.warning(f"Supabase API Error: Category '{name}' already exists. {e.message}")
        else:
            logger.error(f"Supabase API Error adding category '{name}': {e.message}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error adding category '{name}': {e}")
        return None

def update_category_setting(setting_id, definition=None, is_enabled=None):
    """Updates a category's definition and/or enabled status in category_settings."""
    if definition is None and is_enabled is None:
        logger.warning("Update_category_setting called without any data to update.")
        return None # Or perhaps return the current setting if fetched

    update_payload = {}
    if definition is not None:
        update_payload['definition'] = definition
    if is_enabled is not None:
        update_payload['is_enabled'] = is_enabled

    try:
        response = (
            supabase_backend.table(CATEGORY_SETTINGS_TABLE)
            .update(update_payload)
            .eq("id", setting_id) # Use the ID of the category_settings row
            .execute()
        )
        if response.data:
            return response.data[0] # Returns the updated setting row
        logger.error(f"Failed to update category setting ID '{setting_id}'. Response: {response}")
        return None
    except PostgrestAPIError as e:
        logger.error(f"Supabase API Error updating category setting ID '{setting_id}': {e.message}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error updating category setting ID '{setting_id}': {e}")
        return None

def delete_category_by_id(category_id):
    """Deletes a partnership category. Relies on ON DELETE CASCADE for category_settings."""
    try:
        response = (
            supabase_backend.table(PARTNERSHIP_CATEGORIES_TABLE)
            .delete()
            .eq("id", category_id)
            .execute()
        )
        if response.data:
            logger.info(f"Successfully deleted category ID '{category_id}' and its settings.")
            return response.data[0] # Contains the deleted category row
        logger.warning(f"Category ID '{category_id}' not found or not deleted. Response: {response}")
        return None # Or indicate not found if that's a distinct case
    except PostgrestAPIError as e:
        logger.error(f"Supabase API Error deleting category ID '{category_id}': {e.message}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error deleting category ID '{category_id}': {e}")
        return None

# Example usage commented out:
# if __name__ == '__main__':
#     # Test new settings functions
#     # print("--- Testing Category Settings ---")
#     # all_settings = get_all_category_settings()
#     # print(f"Initial settings: {all_settings}")

#     # new_cat_data = add_new_category("Test Custom Category", "This is a test def.", True)
#     # if new_cat_data:
#     #     print(f"Added new category: {new_cat_data}")
#     #     all_settings = get_all_category_settings()
#     #     print(f"Settings after add: {all_settings}")
        
#     #     # Find our test category to update
#     #     test_cat_to_update = next((cat for cat in all_settings if cat['name'] == "Test Custom Category"), None)
#     #     if test_cat_to_update:
#     #         updated_setting = update_category_setting(test_cat_to_update['setting_id'], definition="Updated test def.", is_enabled=False)
#     #         print(f"Updated setting: {updated_setting}")
#     #         all_settings_after_update = get_all_category_settings()
#     #         print(f"Settings after update: {all_settings_after_update}")

#     #         # Delete the test category
#     #         deleted_cat = delete_category_by_id(test_cat_to_update['id'])
#     #         print(f"Deleted category response: {deleted_cat}")
#     #         all_settings_after_delete = get_all_category_settings()
#     #         print(f"Settings after delete: {all_settings_after_delete}")
#     # else:
#     #     print("Failed to add Test Custom Category for further testing.")
    pass
 