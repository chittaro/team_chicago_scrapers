import { useParams } from 'react-router-dom';
import NavBar from './NavBar';
import CompanyPipeline from './CompanyPipeline';


function CompanyTab() {
  const { companyName } = useParams();

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <NavBar />
      <CompanyPipeline companyName={companyName} />
    </div>
  );
}

export default CompanyTab;
