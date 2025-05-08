import React from 'react';

function PartnershipTable({ partnershipData }) {
  if (!partnershipData) return <p>No data available.</p>;

  return (
    <div>
      <table border="1" cellPadding="5">
        <thead>
          <tr>
            <th>Company Name</th>
            <th>Domain</th>
            <th>Type</th>
            <th>URL Source</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(partnershipData).map(([company, data]) => (
            <tr key={company}>
              <td>{company}</td>
              <td>{data.domain}</td>
              <td>{data.type}</td>
              <td>
                {data.urls.map((url, index) => (
                  <div key={index}>
                    <a href={url} target="_blank" rel="noopener noreferrer">
                      {url}
                    </a>
                  </div>
                ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PartnershipTable;