import { Link, useNavigate } from 'react-router-dom'
import { useContext, useState } from 'react'
import { SettingsContext } from './SettingsContext.jsx'


function Settings() {
  const navigate = useNavigate()
  const [editMode, setEditMode] = useState(false)
  const [newCategoryName, setNewCategoryName] = useState('')
  const [showAddCategory, setShowAddCategory] = useState(false)

  const {
    partnerTypeDefinitions,
    setPartnerTypeDefinitions,
    enabledPartnerTypes,
    setEnabledPartnerTypes,
    addPartnerType,
    removePartnerType
  } = useContext(SettingsContext)

  // Get list of all partnership types from definitions
  const partnership_types = Object.keys(partnerTypeDefinitions)

  const handleSave = () => {
    navigate('/')
  }

  const togglePartnerType = (type) => {
    setEnabledPartnerTypes(prev => {
      if (prev.includes(type)) {
        return prev.filter(t => t !== type)
      } else {
        return [...prev, type]
      }
    })
  }

  const handleDeleteCategory = (type) => {
    if (window.confirm(`Are you sure you want to delete the "${type}" category?`)) {
      removePartnerType(type)
    }
  }

  const handleAddCategory = () => {
    if (newCategoryName.trim() && !partnership_types.includes(newCategoryName.trim())) {
      addPartnerType(newCategoryName.trim())
      setNewCategoryName('')
      setShowAddCategory(false)
    }
  }

  // Determine which types to display based on edit mode
  const typesToDisplay = editMode 
    ? partnership_types 
    : partnership_types.filter(type => enabledPartnerTypes.includes(type))

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">Prompt Settings</h2>

        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl" style={{ fontWeight: 'normal' }}>Partnership Type Definitions</h3>
          {editMode && (
            <button
              onClick={() => setShowAddCategory(!showAddCategory)}
              className="bg-blue-500 text-white px-3 py-1 rounded-md text-sm hover:bg-blue-600 transition"
            >
              + Add Category
            </button>
          )}
        </div>

        {/* Add New Category Form */}
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
              />
              <button
                onClick={handleAddCategory}
                className="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600"
                disabled={!newCategoryName.trim() || partnership_types.includes(newCategoryName.trim())}
              >
                Add
              </button>
              <button
                onClick={() => {
                  setShowAddCategory(false)
                  setNewCategoryName('')
                }}
                className="bg-gray-300 text-gray-700 px-3 py-1 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {typesToDisplay.length === 0 && !editMode ? (
          <div className="p-4 text-gray-700 bg-gray-100 rounded-md mb-4">
            No partnership types are enabled. Click "Edit Categories" to add or enable categories.
          </div>
        ) : (
          typesToDisplay.map((type) => (
            <div key={type} style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', marginRight: '12px', minWidth: '120px' }}>
                {editMode && (
                  <input
                    type="checkbox"
                    checked={enabledPartnerTypes.includes(type)}
                    onChange={() => togglePartnerType(type)}
                    style={{ marginRight: '8px', width: '16px', height: '16px' }}
                  />
                )}
                <label style={{ fontWeight: 'bold' }}>{type}:</label>
              </div>
              <input
                type="text"
                value={partnerTypeDefinitions[type]}
                onChange={(e) => {
                  const newDefs = {...partnerTypeDefinitions};
                  if (e.target.value.length <= 200) {
                    newDefs[type] = e.target.value;
                    setPartnerTypeDefinitions(newDefs);
                  }
                }}
                disabled={editMode && !enabledPartnerTypes.includes(type)}
                style={{ 
                  flexGrow: 1, 
                  padding: '8px', 
                  border: '1px solid #ccc', 
                  borderRadius: '4px',
                  opacity: (editMode && !enabledPartnerTypes.includes(type)) ? 0.5 : 1
                }}
              />
              <span style={{ margin: '0 12px', color: '#666', fontSize: '0.9em', minWidth: '50px', textAlign: 'right' }}>
                {partnerTypeDefinitions[type]?.length || 0}/200
              </span>
              {editMode && (
                <button
                  onClick={() => handleDeleteCategory(type)}
                  className="text-red-500 hover:text-red-700 p-1"
                  title="Delete category"
                >
                  🗑️
                </button>
              )}
            </div>
          ))
        )}

        {editMode && enabledPartnerTypes.length === 0 && (
          <div className="p-4 text-amber-700 bg-amber-100 rounded-md mb-4">
            Warning: You've disabled all partnership types. At least one type should be enabled.
          </div>
        )}

        <div className="flex justify-between items-center mt-6">
          <button
            onClick={handleSave}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
          >
            ← Save & Return
          </button>
          <button
            onClick={() => setEditMode(!editMode)}
            className={`${editMode ? 'bg-green-500' : 'bg-gray-500'} text-white px-4 py-2 rounded hover:${editMode ? 'bg-green-600' : 'bg-gray-600'} transition`}
          >
            {editMode ? 'Done Editing' : 'Edit Categories'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Settings