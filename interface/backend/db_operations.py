# Use absolute-like path from project root
from interface.backend.supabaseClient import supabase_backend
from supabase import PostgrestAPIError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for table names
PARTNERSHIPS_TABLE = 'partnerships'
PARTNERSHIP_CATEGORIES_TABLE = 'partnership_categories'
CATEGORY_SETTINGS_TABLE = 'category_settings'

def add_or_update_partnership(partnership_data):
    """
    Adds a new partnership or updates an existing one if it matches
    on the unique constraint (company_name and partnership_name).

    Args:
        partnership_data (dict): A dictionary containing partnership details.
                                 Example corresponding to the schema:
                                 {
                                     'id': 'uuid_if_known_for_update', # Optional, auto-gen on insert
                                     'company_name': 'ExampleCorp',    # Required
                                     'partnership_name': 'Alpha Alliance', # Required
                                     'partnership_type': 'Strategic',    # Optional
                                     'url_scraped_from': 'https://example.com/alpha', # Optional
                                     'date_scraped': 'timestamp_if_specific', # Optional, auto-gen on insert
                                     'status': 'Pending'                 # Optional, defaults to 'Pending' on insert
                                 }

    Returns:
        dict: The inserted or updated record, or None if an error occurred.
    """
    if not partnership_data.get('company_name') or not partnership_data.get('partnership_name'):
        logger.error("company_name and partnership_name are required to add or update a partnership.")
        return None

    try:
        existing_response = (
            supabase_backend.table(PARTNERSHIPS_TABLE)
            .select("id, company_name, partnership_name") # Select enough to identify
            .eq("company_name", partnership_data['company_name'])
            .eq("partnership_name", partnership_data['partnership_name'])
            .limit(1)
            .execute()
        )

        if existing_response.data:
            record_id = existing_response.data[0]['id']
            
            # Construct payload for update: exclude keys used for matching and typically immutable fields.
            # id is the primary key, company_name & partnership_name are for matching.
            # date_scraped is usually set at creation.
            fields_to_exclude_from_update_payload = {'id', 'company_name', 'partnership_name', 'date_scraped'}
            update_payload = {
                key: value for key, value in partnership_data.items()
                if key not in fields_to_exclude_from_update_payload and value is not None # only update provided fields
            }

            if not update_payload: 
                logger.info(f"Partnership for {partnership_data['company_name']} - {partnership_data['partnership_name']} (ID: {record_id}) already exists and no new mutable data provided to update.")
                return existing_response.data[0]
            
            logger.info(f"Updating existing partnership ID: {record_id} with payload: {update_payload}")
            response = (
                supabase_backend.table(PARTNERSHIPS_TABLE)
                .update(update_payload)
                .eq("id", record_id)
                .execute()
            )
        else:
            # Insert new record. `id` and `date_scraped` will use DB defaults if not in partnership_data.
            # `status` will use DB default if not in partnership_data.
            logger.info(f"Inserting new partnership for {partnership_data['company_name']} - {partnership_data['partnership_name']}")
            
            # Prepare insert data: ensure no explicit None for fields with DB defaults unless intended
            insert_payload = {k: v for k, v in partnership_data.items() if v is not None}
            # Remove 'id' if it's None and you want DB to generate it, though Supabase handles this well.
            if 'id' in insert_payload and insert_payload['id'] is None:
                del insert_payload['id']
                
            response = (
                supabase_backend.table(PARTNERSHIPS_TABLE)
                .insert(insert_payload) 
                .execute()
            )

        if response.data:
            logger.info(f"Successfully processed partnership: {response.data[0]}")
            return response.data[0]
        else:
            # Attempt to get more details from the response if it's an error object
            error_message = "Unknown error"
            if hasattr(response, 'error') and response.error:
                error_message = response.error.message if hasattr(response.error, 'message') else str(response.error)
            elif hasattr(response, 'message'): # For some error structures
                 error_message = response.message
            logger.error(f"Failed to add or update partnership. Supabase response: {error_message}. Full response object: {response}")
            return None
            
    except PostgrestAPIError as e:
        logger.error(f"Supabase API Error during partnership upsert for {partnership_data.get('company_name')}/{partnership_data.get('partnership_name')}: {e.message}")
        logger.error(f"Details: {e.details}, Code: {e.code}, Hint: {e.hint}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during partnership upsert for {partnership_data.get('company_name')}/{partnership_data.get('partnership_name')}: {e}")
        return None

def get_partnership_by_partnership_name(partnership_name):
    """
    Retrieves a partnership by its partnership name.
    """
    try:
        response = (
            supabase_backend.table(PARTNERSHIPS_TABLE)
            .select("*")
            .eq("partnership_name", partnership_name)
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error fetching partnership by partnership name {partnership_name}: {e}")
        return None

# --- NEW Functions for Settings Page (partnership_categories & category_settings tables) ---

def get_all_category_settings():
    """Fetches all partnership categories and their associated settings."""
    try:
        response = (
            supabase_backend.table(PARTNERSHIP_CATEGORIES_TABLE)
            .select("id, name, category_settings(id, category_id, definition, is_enabled, updated_at)") # Joins with category_settings
            .execute()
        )
        if response.data:
            # Transform data to match frontend expectations (name, definition, is_enabled, id for category)
            transformed_data = []
            for category in response.data:
                setting = category.get('category_settings')[0] if category.get('category_settings') else {}
                transformed_data.append({
                    'id': category['id'], # This is partnership_categories.id
                    'name': category['name'],
                    'definition': setting.get('definition', ''),
                    'is_enabled': setting.get('is_enabled', True),
                    'setting_id': setting.get('id') # This is category_settings.id, useful for updates
                })
            return transformed_data
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
 