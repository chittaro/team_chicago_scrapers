import { useState } from 'react'

import NavBar from './NavBar';
import CompanyPipeline from './CompanyPipeline';

import './App.css'

const PREFIX = "http://127.0.0.1:5000/api";


function Home() {
  const [companyName, setCompanyName] = useState('')
  const [tempCompanyName, setTempCompanyName] = useState('')
  const [showCompany, setShowCompany] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  const handleCompanySubmit = async (e) => {
    e.preventDefault()
    if (!tempCompanyName.trim()) return
    
    setCompanyName(tempCompanyName)
    setShowCompany(true)
  }

  const getFormattedDate = () => {
    const date = new Date();
    const day = String(date.getDate()).padStart(2, '0');  // Ensure two digits for day
    const month = String(date.getMonth() + 1).padStart(2, '0');  // Ensure two digits for month (months are 0-indexed)
    const year = date.getFullYear();  // Full year (YYYY)
    return `${day}.${month}.${year}`;
  };

  const downloadCSV = async () => {
    setIsDownloading(true);
    let partnerships = []
    try {
      console.log("fetching all partnership data")
      const response = await fetch(`${PREFIX}/get_all_partner_data/`);
      const data = await response.json();
      if (!data.success){
        return
      }
      partnerships = data.data;
    } catch (err) {
      console.log(`Failed to fetch data, error: ${err}`);
      setIsDownloading(false);
      return
    }

    setIsDownloading(false);

    const headers = Object.keys(partnerships[0]);
    const csvRows = [headers.join(",")];

    partnerships.forEach((row) => {
      const values = headers.map(header => `"${row[header] || ''}"`);
      csvRows.push(values.join(","));
    });

    const csvContent = csvRows.join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const date = getFormattedDate();
    link.href = url;
    link.download = `competitor_partnerships_${date}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <NavBar/>
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-2xl font-bold text-center mb-6 text-gray-800">Hexagon Partnership Finder</h1>
        <button 
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            onClick={downloadCSV}
            disabled={isDownloading}>
            Download CSV of ALL Competitor Data
        </button>
        
        {/* Company Input Section - Chat-like bubble */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-4 transition-all duration-300 transform hover:shadow-lg">
          <form onSubmit={handleCompanySubmit}>
            <p className="block text-gray-700 mb-2 text-lg" style={{fontWeight: "normal"}}>Enter competitor name to find & classify partnerships</p>
            <div className="flex gap-2">
            <input
              type="text"
              value={tempCompanyName}
              onChange={(e) => setTempCompanyName(e.target.value)}
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
