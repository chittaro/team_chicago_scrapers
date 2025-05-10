from flask import Blueprint, jsonify, request
# Use absolute-like path from project root
from interface.backend.db_operations import (
    get_all_category_settings,
    add_new_category,
    update_category_setting,
    delete_category_by_id
)
import uuid # For type hinting and potentially validating UUIDs

# Create a Blueprint for settings routes
# The first argument is the blueprint's name, the second is its import name,
# and url_prefix will prefix all routes defined in this blueprint.
settings_bp = Blueprint('settings_bp', __name__, url_prefix='/api/settings')

@settings_bp.route('', methods=['GET'])
def handle_get_all_settings():
    """API endpoint to fetch all category settings."""
    settings = get_all_category_settings()
    if settings is not None: # get_all_category_settings returns [] on no data or error
        return jsonify(settings), 200
    return jsonify({"error": "Failed to retrieve settings"}), 500

@settings_bp.route('/category', methods=['POST'])
def handle_add_category():
    """API endpoint to add a new partnership category."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Category name is required"}), 400

    name = data.get('name')
    definition = data.get('definition', '') # Optional
    is_enabled = data.get('is_enabled', True) # Optional

    new_category_setting = add_new_category(name, definition, is_enabled)

    if new_category_setting:
        return jsonify(new_category_setting), 201
    elif new_category_setting is None and name: # Check if it was a unique constraint violation
        # db_operations.add_new_category logs a warning for unique violations
        # and returns None in that specific case.
        # We need a way to differentiate this from other errors if db_operations doesn't explicitly.
        # For now, assume any None return after a name was provided might be due to this or other DB error.
        # A more robust solution would have add_new_category return a specific error code/message.
        existing_categories = get_all_category_settings()
        if any(cat['name'] == name for cat in existing_categories):
             return jsonify({"error": f"Category '{name}' already exists."}), 409 # Conflict

    return jsonify({"error": f"Failed to add category '{name}'"}), 500

@settings_bp.route('/category_setting/<uuid:setting_id>', methods=['PUT'])
def handle_update_category_setting(setting_id):
    """API endpoint to update a category's setting (definition, is_enabled)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided for update"}), 400

    definition = data.get('definition') # Can be None if not updating
    is_enabled = data.get('is_enabled') # Can be None if not updating

    if definition is None and is_enabled is None:
        return jsonify({"error": "No fields to update (definition or is_enabled required)"}), 400

    updated_setting = update_category_setting(str(setting_id), definition=definition, is_enabled=is_enabled)

    if updated_setting:
        return jsonify(updated_setting), 200
    return jsonify({"error": f"Failed to update category setting ID '{setting_id}' or setting not found"}), 500 # Or 404 if known not found

@settings_bp.route('/category/<uuid:category_id>', methods=['DELETE'])
def handle_delete_category(category_id):
    """API endpoint to delete a partnership category."""
    deleted_category_info = delete_category_by_id(str(category_id))

    if deleted_category_info:
        # The response from delete_category_by_id contains the deleted row info
        return jsonify({"message": f"Category ID '{category_id}' deleted successfully", "deleted_category": deleted_category_info}), 200
    # db_operations.delete_category_by_id logs a warning if not found but returns None.
    # It doesn't distinguish between "not found" and "other error" clearly for the API to return 404 vs 500.
    # For simplicity, we'll assume a None return here means it wasn't deleted (either not found or error).
    return jsonify({"error": f"Failed to delete category ID '{category_id}' or category not found"}), 500 # Or 404 