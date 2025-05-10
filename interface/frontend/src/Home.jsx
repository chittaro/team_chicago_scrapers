import { useState, useEffect, useContext } from 'react'
import { useNavigate } from 'react-router-dom';
import { SettingsContext } from './SettingsContext'

import NavBar from './NavBar';
import CompanyPipeline from './CompanyPipeline';

import './App.css'

function Home() {
  const [companyName, setCompanyName] = useState('')
  const [showCompany, setShowCompany] = useState(false);
  const {partnerTypeDefinitions} = useContext(SettingsContext)

  const navigate = useNavigate();

  // remove '/test' to use real functions
  const PREFIX = "http://127.0.0.1:5000/api/test"

  const handleCompanySubmit = async (e) => {
    e.preventDefault()
    if (!companyName.trim()) return
    
    setShowCompany(true)
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <NavBar/>
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
                className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
              >
                Search
              </button>
            </div>
          </form>
        </div>

        {showCompany && <CompanyPipeline companyName={companyName} />}


      </div>
    </div>
  )
}

export default Home
