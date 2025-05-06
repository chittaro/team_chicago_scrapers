import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

import './App.css'

function Home() {
  const [companyName, setCompanyName] = useState('')
  const [urls, setUrls] = useState([])
  const [partnerships, setPartnerships] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [showAddUrlInput, setShowAddUrlInput] = useState(false)
  const [newUrl, setNewUrl] = useState('')
  const [submittedCompany, setSubmittedCompany] = useState('')

  // Mock data for testing
  const mockUrls = [
    'https://example.com/partners',
    'https://businesswire.com/news/company-partnership',
    'https://company.com/alliances'
  ]

  const mockPartnerships = [
    {
      company_name: 'Test Company',
      partnership_name: 'Partner A',
      partnership_type: 'Strategic',
      url_scraped_from: 'https://example.com/partners',
      date_scraped: '2023-04-28',
      status: 'Pending'
    },
    {
      company_name: 'Test Company',
      partnership_name: 'Partner B',
      partnership_type: 'Technology',
      url_scraped_from: 'https://businesswire.com/news/company-partnership',
      date_scraped: '2023-04-28',
      status: 'Confirmed'
    }
  ]

  const handleCompanySubmit = async (e) => {
    e.preventDefault()
    if (!companyName.trim()) return
    
    setIsLoading(true)
    setUrls([])
    setPartnerships([])
    setSubmittedCompany(companyName)
    
    const response = await fetch(`http://127.0.0.1:5000/api/get_urls/${companyName}`, { credentials: "same-origin" })
    .then((response) => {
      if (!response.ok) throw Error(response.statusText)
      return response.json()
    })

    setUrls(response.urls)
    setIsLoading(false)
  }

  const handleRemoveUrl = (index) => {
    setUrls(prev => prev.filter((_, i) => i !== index))
  }

  const handleAddUrl = () => {
    if (newUrl.trim() && !urls.includes(newUrl)) {
      setUrls(prev => [...prev, newUrl])
      setNewUrl('')
      setShowAddUrlInput(false)
    }
  }

  const handleContinue = async () => {
    // For testing, use mock data
    setPartnerships(mockPartnerships)
    
    // TODO: Implement real API call
    // const response = await fetch(`/api/partnerships?company=${companyName}`)
    // const data = await response.json()
    // setPartnerships(data.partnerships)
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
            <label className="block text-gray-700 mb-2 text-lg">Enter a company name to find partnerships</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="e.g., Microsoft, Amazon, Tesla"
                className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={isLoading}
                className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
              >
                {isLoading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>
        </div>

        {/* Loading Animation */}
        {isLoading && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-4 text-center animate-pulse">
            <p className="text-gray-600">Searching the web for {submittedCompany} partnerships...</p>
            <div className="flex justify-center mt-4 space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
            </div>
          </div>
        )}

        {/* Live URL Display - Animated entry */}
        {urls.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-4 transition-opacity duration-500 opacity-100">
            <h2 className="text-xl font-semibold mb-4">Found URLs for {submittedCompany}</h2>
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
                  onClick={handleContinue}
                  className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors"
                >
                  Continue
                </button>
              </div>
            )}
          </div>
        )}

        {/* Partnerships Table */}
        {partnerships.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 transition-all duration-500 animate-fade-in">
            <h2 className="text-xl font-semibold mb-4">Partnerships for {submittedCompany}</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-6 py-3 text-left text-gray-700">Company Name</th>
                    <th className="px-6 py-3 text-left text-gray-700">Partnership Name</th>
                    <th className="px-6 py-3 text-left text-gray-700">Partnership Type</th>
                    <th className="px-6 py-3 text-left text-gray-700">URL Source</th>
                    <th className="px-6 py-3 text-left text-gray-700">Date Scraped</th>
                    <th className="px-6 py-3 text-left text-gray-700">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {partnerships.map((partnership, index) => (
                    <tr key={index} className="border-t hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">{partnership.company_name}</td>
                      <td className="px-6 py-4">{partnership.partnership_name}</td>
                      <td className="px-6 py-4">{partnership.partnership_type}</td>
                      <td className="px-6 py-4">
                        <a href={partnership.url_scraped_from} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline truncate block max-w-xs">
                          {partnership.url_scraped_from}
                        </a>
                      </td>
                      <td className="px-6 py-4">{partnership.date_scraped}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded text-sm font-medium ${
                          partnership.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                          partnership.status === 'Confirmed' ? 'bg-green-100 text-green-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {partnership.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Home
