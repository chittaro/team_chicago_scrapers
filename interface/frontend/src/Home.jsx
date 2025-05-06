import { useState, useEffect, useContext } from 'react'
import { Link } from 'react-router-dom'
import { SettingsContext } from './SettingsContext'

import './App.css'

function Home() {
  const [companyName, setCompanyName] = useState('')
  const [urls, setUrls] = useState([])
  const [partnerships, setPartnerships] = useState([])
  const [isURLSLoading, setURLSLoading] = useState(false)
  const [isDataLoading, setDataLoading] = useState(false)
  const [showAddUrlInput, setShowAddUrlInput] = useState(false)
  const [newUrl, setNewUrl] = useState('')
  const [submittedCompany, setSubmittedCompany] = useState('')
  const [tableState, setTableState] = useState('')
  const {partnerTypeDefinitions} = useContext(SettingsContext)

  const handleCompanySubmit = async (e) => {
    e.preventDefault()
    if (!companyName.trim()) return
    
    setURLSLoading(true)
    setDataLoading(false)
    setUrls([])
    setPartnerships([])
    setTableState("")
    setSubmittedCompany(companyName)
    
    const response = await fetch(`http://127.0.0.1:5000/api/get_urls/${companyName}`, { credentials: "same-origin" })
    .then((response) => {
      if (!response.ok) throw Error(response.statusText)
      return response.json()
    })

    setUrls(response.urls)
    setURLSLoading(false)
  }

  const handleAddUrl = () => {
    if (newUrl.trim() && !urls.includes(newUrl)) {
      setUrls(prev => [...prev, newUrl])
      setNewUrl('')
      setShowAddUrlInput(false)
    }
  }

  const handleContinue = async () => {
    setDataLoading(true)
    
    const response = await fetch(`http://127.0.0.1:5000/api/get_partner_data/${companyName}`, { credentials: "same-origin" })
    .then((response) => {
      if (!response.ok) throw Error(response.statusText)
      return response.json()
    })

    if (response.success){
      setPartnerships(response.data)
      setTableState("Full")
    }
    else {
      setTableState("Empty")
    }

    setDataLoading(false)
  }

  const handleParseHTML = async () => {
    setDataLoading(true)
    const response = await fetch(`http://127.0.0.1:5000/api/process_html/${companyName}`, { credentials: "same-origin" })
    .then((response) => {
      if (!response.ok) throw Error(response.statusText)
      return response.json()
    })

    if (response.success){
      setPartnerships(response.data)
      setTableState("Full")
    }
    else {
      setTableState("Fail")
    }

    setDataLoading(false)

  }

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <Link to="/settings" className="absolute top-4 right-4 text-gray-600 hover:text-gray-800 transition-colors">
        Prompt Settings
      </Link>
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-2xl font-bold text-center mb-6 text-gray-800">Hexagon Partnership Finder</h1>
        
        {/* Company Input Section - Chat-like bubble */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-4 transition-all duration-300 transform hover:shadow-lg">
          <form onSubmit={handleCompanySubmit}>
            <p className="block text-gray-700 mb-2 text-lg" style={{fontWeight: "normal"}}>Enter competitor name to find & classify partnerships</p>
            <div className="flex gap-2">
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="Company Name"
              className="company-name-input"
            />
              <button
                type="submit"
                disabled={isURLSLoading}
                className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
              >
                {isURLSLoading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>
        </div>

        {/* Loading Animation */}
        {isURLSLoading && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-4 text-center animate-pulse">
            <p className="text-gray-600">Searching the web for {submittedCompany} partnerships...</p>
          </div>
        )}

        {/* Live URL Display - Animated entry */}
        {urls.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-4 transition-opacity duration-500 opacity-100">
            <h2 className="text-xl font-semibold mb-4">Found URLs for {submittedCompany}:</h2>
            <div className="scrollable-box"   style={{height: '150px', overflowY: 'auto', border: "1px solid #000"}}>
              {urls.map((item, index) => (
                <div key={index} style={{ marginBottom: '5px' }}>
                  {item}
                </div>
              ))}
            </div>

            {/* Add URL Input */}
            {showAddUrlInput ? (
              <div className="mt-4 flex gap-2">
                <input
                  type="text"
                  value={newUrl}
                  onChange={(e) => setNewUrl(e.target.value)}
                  placeholder="https://example.com/partners"
                  className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleAddUrl}
                  className="bg-blue-500 text-white px-3 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                >
                  Add
                </button>
                <button
                  onClick={() => setShowAddUrlInput(false)}
                  className="bg-gray-300 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  Cancel
                </button>
              </div>
            ) : (
              <div className="mt-4 space-x-4">
                <button 
                  onClick={() => setShowAddUrlInput(true)}
                  className="text-blue-500 hover:text-blue-700 transition-colors underline"
                >
                  + Add Another URL
                </button>
                <button
                  type="submit"
                  disabled={isDataLoading}
                  onClick={handleContinue}
                  className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
                >
                  {isDataLoading ? 'Parsing...' : 'Continue'}
                </button>
              </div>
            )}
          </div>
        )}

        {isDataLoading && (
            <div className="bg-white rounded-lg shadow-md p-6 mb-4 text-center animate-pulse">
              <p className="text-gray-600">Parsing URLs for partnership data...</p>
            </div>
        )}

        {/* Partnerships Table */}
        {tableState.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 transition-all duration-500 animate-fade-in">
            <h2 className="text-xl font-semibold mb-4">Partnerships for {submittedCompany}:</h2>
            {tableState == "Empty" && (<>
              <h3 style={{ fontWeight: 'normal' }}>Partnership data hasn't been parsed yet. Fetch data?</h3>
              
            </>)}
            {tableState == "Full" && ( <>
              <h3 style={{ fontWeight: 'normal' }}>Existing partnership data found in the database!</h3>
              <button
                  type="submit"
                  disabled={isDataLoading}
                  onClick={handleParseHTML}
                  className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
                >
                  {isDataLoading ? 'Processing...' : 'Re-Process Data'}
              </button>

              <div className="overflow-x-auto">
                <div className="overflow-x-auto border border-black rounded-md">
                  <table className="partnership-table">
                    <thead>
                      <tr>
                        <th>Company Name</th>
                        <th>Domain</th>
                        <th>Type</th>
                        <th>URL Source</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(partnerships).map(([companyName, entry]) => (
                        <tr key={companyName}>
                          <td>{companyName}</td>
                          <td>{entry.domain}</td>
                          <td>{entry.type}</td>
                          <td>
                            <div className="url-scroll-container">
                              {entry.urls.map((url, index) => (
                                <div key={index}>
                                  <a href={url} target="_blank" rel="noopener noreferrer">
                                    {url}
                                  </a>
                                </div>
                              ))}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

                </div>
              </div>
            </>)}
            
            {tableState == "Fail" && (
              <h3 style={{ fontWeight: 'normal' }}>Failed to process data</h3>
            )}

          </div>
        )}
      </div>
    </div>
  )
}

export default Home
