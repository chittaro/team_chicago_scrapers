// Company.jsx
import { useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import PartnershipTable from './PartnershipTable';
import NavBar from './NavBar';


function Company() {
  const { companyName } = useParams();
  const [partnerships, setPartnerships] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const PREFIX = "http://127.0.0.1:5000/api/test";

  useEffect(() => {
    const fetchPartnerships = async () => {
      setIsLoading(true);
      setPartnerships(null)
      try {
        const response = await fetch(`${PREFIX}/get_partner_data/${companyName}`);
        const data = await response.json();
        if (data.success) {
          setPartnerships(data.data);
        } else {
          setError("No data found for this company.");
        }
      } catch (err) {
        setError("Failed to fetch data.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchPartnerships();
  }, [companyName]);

  return (
    <div className="min-h-screen bg-gray-100 py-8">
        <NavBar/>
        <div className="max-w-4xl mx-auto px-4">
            <h2>Partnerships for {companyName}</h2>
            {isLoading && <p>Loading data...</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}
            {partnerships ? (
                <PartnershipTable partnershipData={partnerships} />
            ) : (
                !isLoading && !error && <p>No partnership data available.</p>
            )}
        </div>
    </div>
  );
}

export default Company;
