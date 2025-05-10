import React from 'react';
import { useNavigate } from 'react-router-dom';

function NavBar() {
  const navigate = useNavigate();

  return (
    <nav style={{position: 'sticky', top: 0, backgroundColor: '#f0f0f0', display: 'flex',
        justifyContent: 'space-between', padding: '10px 20px', borderBottom: '2px solid #ccc'}}>
        <button onClick={() => navigate('/')} style={{ flex: 1, borderRight: '1px solid #ccc' }}>Search</button>
        <button onClick={() => navigate('/companyTab/autodesk')} style={{ flex: 1, borderRight: '1px solid #ccc' }}>Autodesk</button>
        <button onClick={() => navigate('/companyTab/faro')} style={{ flex: 1, borderRight: '1px solid #ccc' }}>Faro</button>
        <button onClick={() => navigate('/settings')} style={{ flex: 1, borderRight: '1px solid #ccc' }}>Settings</button>
      </nav>
  );
}

export default NavBar;