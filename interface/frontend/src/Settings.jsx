import { Link, useNavigate } from 'react-router-dom'
import { useContext } from 'react'
import { SettingsContext } from './SettingsContext.jsx'


function Settings() {
  const navigate = useNavigate()
  const partnership_types = ["Strategic Partner", "Software Partner", "Hardware Partner", "HPC Partner", "Reseller"]

  const {
    partnerTypeDefinitions,
    setPartnerTypeDefinitions,
  } = useContext(SettingsContext)

  const handleChange = (e) => {
    const { name, value } = e.target
    if (value.length <= 200) {
      setPartnerTypeDefinitions((prev) => ({ ...prev, [name]: value }))
    }
  }

  const handleSave = () => {
    // Optionally persist to localStorage or backend here
    navigate('/') // Navigate back to home
  }


  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">Prompt Settings</h2>

        <h3 className="text-xl mb-4">Partnership Type Definitions</h3>

        {partnership_types.map((type) => (
            <div key={type} style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
            <label style={{ fontWeight: 'bold', width: '100px' }}>{type}:</label>
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
              style={{ flexGrow: 1, marginLeft: '16px', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
            />
            <span style={{ marginLeft: '12px', color: '#666', fontSize: '0.9em' }}>
              {partnerTypeDefinitions[type]?.length || 0}/200
            </span>
          </div>
        ))}

        <div className="flex justify-between items-center">
          <button
            onClick={handleSave}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
          >
            ← Save & Return
          </button>
        </div>
      </div>
    </div>
  )
}


export default Settings