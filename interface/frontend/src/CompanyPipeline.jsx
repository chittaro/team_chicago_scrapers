import { useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import PartnershipTable from './PartnershipTable';

function CompanyPipeline({ companyName }) {
  const [partnerships, setPartnerships] = useState(null);
  const [urls, setUrls] = useState([]);
  const [isURLSLoading, setURLSLoading] = useState(false);
  const [isDataProcessing, setDataProcessing] = useState(false);
  const [isDataFetching, setDataFetching] = useState(false);

  const PREFIX = "http://127.0.0.1:5000/api";

  const resetStates = () => {
    setPartnerships(null)
    setUrls(null)
    setURLSLoading(false)
    setDataFetching(false)
  }

  useEffect(() => {
    const fetchPartnerships = async () => {
      resetStates();

      setDataFetching(true);
      try {
        console.log("fetching data")
        const response = await fetch(`${PREFIX}/get_partner_data/${companyName}`);
        const data = await response.json();
        if (data.success){
          setPartnerships(data.data);
        }
      } catch (err) {
        console.log("Failed to fetch data in fetchPartnerships.");
      } finally {
        setDataFetching(false);
      }
    };

    fetchPartnerships();
  }, [companyName]);

  const handleFetchURLs = async () => {
    resetStates();
    
    setURLSLoading(true);
    const response = await fetch(`${PREFIX}/get_urls/${companyName}`);
    const data = await response.json();
    setUrls(data.urls);
    setURLSLoading(false);
  };

  const handleProcessData = async () => {
    setDataProcessing(true);
    const response = await fetch(`${PREFIX}/process_data/${companyName}`);
    const data = await response.json();
    if (data.success) setPartnerships(data.data);
    else setError("Failed to process data.");
    setDataProcessing(false);
  };

  return (
      <div className="max-w-4xl mx-auto px-4">
        <h2>Partnerships for {companyName}</h2>

        {/* Display data status & buttons */}
        {isDataFetching ? (
          <p>Loading data...</p>) : partnerships ? (<>
            <p>Partnership data found!</p>
            <div>
              <button 
                disabled={isURLSLoading}
                onClick={handleFetchURLs}>
                  {isURLSLoading ? "Fetching URLs..." : "Re-process Data"} </button>
            </div>
          </>) : (<>
            <p>Partnership data not found.</p>
            <div>
              <button 
                disabled={isURLSLoading}
                onClick={handleFetchURLs}>
                {isURLSLoading ? "Fetching URLs..." : "Start Pipeline"}
              </button>
            </div>
          </>)
        }

        {/* Display URLs table if exists */}
        {isURLSLoading && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-4 text-center animate-pulse">
            <p className="text-gray-600">Searching the web for {companyName} partnerships...</p>
          </div>
        )}
        {urls && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-4 transition-opacity duration-500 opacity-100">
            <h2 className="text-xl font-semibold mb-4">Found URLs for {companyName}:</h2>
            <div className="scrollable-box" style={{height: '150px', overflowY: 'auto', border: "1px solid #000"}}>
              {urls.map((item, index) => (
                <div key={index} style={{ marginBottom: '5px' }}>
                  {item}
                </div>
              ))}
            </div>
            {!partnerships && (
                <button 
                    onClick={handleProcessData}
                    disabled={isDataProcessing}
                    >
                    {isDataProcessing ? "Parsing URLs..." : "Continue"}</button>
            )}
          </div>
        )}

        {/* Display partnership table if exists */}
        {isDataProcessing && (
          <p>Processing data...</p>
        )}
        {partnerships && <PartnershipTable partnershipData={partnerships} />}


      </div>
  );
}

export default CompanyPipeline;
