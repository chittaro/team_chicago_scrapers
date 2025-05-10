import { useNavigate } from 'react-router-dom'
import { useContext, useState, useEffect, useCallback } from 'react'
import { SettingsContext } from './SettingsContext.jsx'

// Helper for debouncing
function debounce(func, delay) {
  let timeoutId;
  return function(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      func.apply(this, args);
    }, delay);
  };
}

function Settings() {
  const navigate = useNavigate()
  const [editMode, setEditMode] = useState(false)
  const [newCategoryName, setNewCategoryName] = useState('')
  const [showAddCategory, setShowAddCategory] = useState(false)
  const [actionError, setActionError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Local state for definition inputs to allow smooth typing
  const [localDefinitions, setLocalDefinitions] = useState({})

  const {
    categorySettings,
    isLoading: isLoadingContext,
    error: errorContext,
    addCategory,
    updateSetting,
    deleteCategory,
  } = useContext(SettingsContext)

  // Effect to initialize localDefinitions when categorySettings load or change
  useEffect(() => {
    const initialDefs = {}
    categorySettings.forEach(setting => {
      initialDefs[setting.setting_id] = setting.definition
    })
    setLocalDefinitions(initialDefs)
  }, [categorySettings])

  const handleSave = () => {
    // Before navigating, ensure any pending debounced updates are flushed or saved if necessary.
    // For this debounced approach, changes are saved automatically after typing stops.
    // If there were a true "batch save" on this button, logic would go here.
    navigate('/')
  }

  const handleToggleEnable = async (setting) => {
    setActionError(null)
    setIsSubmitting(true)
    try {
      await updateSetting(setting.setting_id, undefined, !setting.is_enabled)
    } catch (e) {
      setActionError(e.message || 'Failed to toggle category status.')
    } finally {
      setIsSubmitting(false)
    }
  }

  // Debounced version of the actual API call for definition update
  const debouncedUpdateDefinition = useCallback(
    debounce(async (setting_id, newDefinition) => {
      setActionError(null)
      // No setIsSubmitting here for debounced calls to avoid UI flicker during typing pauses
      try {
        await updateSetting(setting_id, newDefinition, undefined)
      } catch (e) {
        console.error("Failed to update definition via debounce:", e)
        setActionError(e.message || 'Failed to save definition.')
        // Optionally, revert localDefinitions if API call fails
        // For simplicity, not implemented here, relies on context re-fetch for consistency on error
      }
    }, 1500), // Adjust delay as needed (e.g., 1.5 seconds)
    [updateSetting] // updateSetting from context should be stable
  )

  const handleDefinitionInputChange = (setting, newDefinitionValue) => {
    if (newDefinitionValue.length <= 200) {
      // Update local state immediately for responsive typing
      setLocalDefinitions(prev => ({
        ...prev,
        [setting.setting_id]: newDefinitionValue
      }))
      // Trigger the debounced API call
      debouncedUpdateDefinition(setting.setting_id, newDefinitionValue)
    } else {
      setActionError('Definition cannot exceed 200 characters.')
    }
  }

  const handleDelete = async (category) => {
    setActionError(null)
    if (window.confirm(`Are you sure you want to delete the "${category.name}" category?`)) {
      setIsSubmitting(true)
      try {
        await deleteCategory(category.id)
      } catch (e) {
        setActionError(e.message || 'Failed to delete category.')
      } finally {
        setIsSubmitting(false)
      }
    }
  }

  const handleAdd = async () => {
    setActionError(null)
    const trimmedName = newCategoryName.trim()
    if (trimmedName && !categorySettings.some(c => c.name === trimmedName)) {
      setIsSubmitting(true)
      try {
        await addCategory(trimmedName)
        setNewCategoryName('')
        setShowAddCategory(false)
      } catch (e) {
        setActionError(e.message || 'Failed to add category.')
      } finally {
        setIsSubmitting(false)
      }
    } else if (categorySettings.some(c => c.name === trimmedName)) {
      setActionError('A category with this name already exists.')
    }
  }
  
  const typesToDisplay = editMode
    ? categorySettings
    : categorySettings.filter(setting => setting.is_enabled)

  const enabledCategoriesInEditModeCount = categorySettings.filter(s => s.is_enabled).length

  if (isLoadingContext && !categorySettings.length) {
    return <div className="p-6 text-center">Loading settings...</div>
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">Prompt Settings</h2>
        
        {errorContext && (
          <div className="p-3 mb-4 text-red-700 bg-red-100 rounded-md">
            Error loading settings: {errorContext}
          </div>
        )}
        {actionError && (
          <div className="p-3 mb-4 text-red-700 bg-red-100 rounded-md">
            {actionError}
          </div>
        )}

        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl" style={{ fontWeight: 'normal' }}>Partnership Type Definitions</h3>
          {editMode && (
            <button
              onClick={() => { setShowAddCategory(prev => !prev); setActionError(null); setNewCategoryName(''); }}
              className="bg-blue-500 text-white px-3 py-1 rounded-md text-sm hover:bg-blue-600 transition"
              disabled={isSubmitting}
            >
              {showAddCategory ? '- Cancel Add' : '+ Add Category'}
            </button>
          )}
        </div>

        {editMode && showAddCategory && (
          <div className="mb-6 p-4 border border-blue-200 bg-blue-50 rounded-md">
            <h4 className="font-medium mb-2">Create New Category</h4>
            <div className="flex gap-2">
              <input
                type="text"
                value={newCategoryName}
                onChange={(e) => setNewCategoryName(e.target.value)}
                placeholder="Category Name"
                className="flex-1 p-2 border rounded"
                disabled={isSubmitting}
              />
              <button
                onClick={handleAdd}
                className="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600 transition"
                disabled={isSubmitting || !newCategoryName.trim() || categorySettings.some(c => c.name === newCategoryName.trim())}
              >
                {isSubmitting ? 'Adding...' : 'Add'}
              </button>
              <button
                onClick={() => { setShowAddCategory(false); setNewCategoryName(''); setActionError(null); }}
                className="bg-gray-300 text-gray-700 px-3 py-1 rounded hover:bg-gray-400 transition"
                disabled={isSubmitting}
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {(typesToDisplay.length === 0 && !editMode && !isLoadingContext && !errorContext) ? (
          <div className="p-4 text-gray-700 bg-gray-100 rounded-md mb-4">
            No partnership types are currently enabled. Click "Edit Categories" to enable or add new categories.
          </div>
        ) : (
          typesToDisplay.map((setting) => (
            <div key={setting.id} style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', marginRight: '12px', minWidth: '120px' }}>
                {editMode && (
                  <input
                    type="checkbox"
                    checked={setting.is_enabled}
                    onChange={() => handleToggleEnable(setting)}
                    style={{ marginRight: '8px', width: '16px', height: '16px' }}
                    disabled={isSubmitting}
                  />
                )}
                <label style={{ fontWeight: 'bold', color: (!editMode || setting.is_enabled) ? 'inherit' : '#999' }}>
                  {setting.name}:
                </label>
              </div>
              <input
                type="text"
                value={localDefinitions[setting.setting_id] !== undefined ? localDefinitions[setting.setting_id] : ''}
                onChange={(e) => handleDefinitionInputChange(setting, e.target.value)}
                disabled={(editMode && !setting.is_enabled) || isSubmitting}
                style={{
                  flexGrow: 1,
                  padding: '8px',
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                  opacity: (editMode && !setting.is_enabled) ? 0.5 : 1
                }}
              />
              <span style={{ margin: '0 12px', color: '#666', fontSize: '0.9em', minWidth: '50px', textAlign: 'right' }}>
                {(localDefinitions[setting.setting_id]?.length || 0)}/200
              </span>
              {editMode && (
                <button
                  onClick={() => handleDelete(setting)}
                  className="text-red-500 hover:text-red-700 p-1 transition"
                  title="Delete category"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? '...' : '🗑️'}
                </button>
              )}
            </div>
          ))
        )}

        {editMode && enabledCategoriesInEditModeCount === 0 && (
          <div className="p-4 text-amber-700 bg-amber-100 rounded-md mb-4">
            Warning: You've disabled all partnership types. At least one type should be enabled for searches to be effective.
          </div>
        )}

        <div className="flex justify-between items-center mt-6">
          <button
            onClick={handleSave}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
            disabled={isSubmitting}
          >
            ← Save & Return
          </button>
          <button
            onClick={() => { setEditMode(prev => !prev); setActionError(null); setShowAddCategory(false); }}
            className={`${editMode ? 'bg-green-500' : 'bg-gray-500'} text-white px-4 py-2 rounded hover:${editMode ? 'bg-green-600' : 'bg-gray-600'} transition`}
            disabled={isSubmitting || isLoadingContext}
          >
            {isSubmitting ? '...' : (editMode ? 'Done Editing' : 'Edit Categories')}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Settings