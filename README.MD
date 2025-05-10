## Frontend: Settings Page (`interface/frontend/src/Settings.jsx`)

This React component serves as the settings page for the application, allowing users to customize how partnership types are defined and managed. It interacts with a `SettingsContext` to persist these configurations across the application.

### Key Functionalities:

1.  **Partnership Type Definitions Management:**
    *   Users can view and edit the textual descriptions associated with each partnership type (e.g., "Strategic Partner", "Software Partner").
    *   Each definition has a character limit (e.g., 200 characters), and the current character count is displayed.

2.  **Category Enable/Disable Toggling:**
    *   An "Edit Categories" button allows users to enter an edit mode.
    *   In edit mode, checkboxes appear next to each partnership type, allowing users to enable or disable them.
    *   When not in edit mode (i.e., after clicking "Done Editing"), only the enabled partnership types and their definitions are displayed. Disabled categories are hidden from view on this page.
    *   A warning is displayed if the user attempts to disable all partnership types while in edit mode.

3.  **Custom Category Creation:**
    *   In edit mode, an "+ Add Category" button is available.
    *   Clicking this button reveals a form where users can type a name for a new partnership category.
    *   The system prevents the creation of categories with duplicate names.
    *   Newly created categories are automatically enabled by default.

4.  **Category Deletion:**
    *   In edit mode, a delete icon (🗑️) appears next to each partnership category.
    *   Clicking the delete icon prompts the user with a confirmation dialog before permanently removing the category.
    *   This applies to both default and user-created categories.

5.  **State Management and Navigation:**
    *   The component uses `useState` for local component state (e.g., edit mode status, new category input).
    *   It utilizes `useContext` to access and modify shared settings from `SettingsContext`, including:
        *   `partnerTypeDefinitions`: An object storing the text descriptions for each type.
        *   `enabledPartnerTypes`: An array listing the names of currently active/enabled types.
        *   Functions to `addPartnerType` and `removePartnerType`.
    *   A "← Save & Return" button navigates the user back to the main page (presumably `/`). The changes made to definitions and enabled statuses are persisted through the context.

### User Interface Notes:

*   The page is styled using Tailwind CSS classes for a clean and responsive layout.
*   Input fields for definitions are disabled for categories that are themselves disabled (when in edit mode).
*   Visual cues like graying out are used for disabled items in edit mode, and items are completely hidden if disabled when not in edit mode.
*   Buttons change text and color based on the current mode (e.g., "Edit Categories" vs. "Done Editing").
