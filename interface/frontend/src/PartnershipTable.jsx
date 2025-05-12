import React from 'react';

function PartnershipTable({ partnershipData }) {
  if (!partnershipData) return <p>No data available.</p>;

  return (
    <div>
      <table border="1" cellPadding="5">
        <thead>
          <tr>
            <th>Partner Name</th>
            <th>Domain</th>
            <th>Type</th>
            <th>Date Scraped</th>
            <th>URL Source</th>
          </tr>
        </thead>
        <tbody>
          {partnershipData.map((data, index) => (
            <tr key={index}>
              <td>{data.partnership_name}</td>
              <td>{data.partnership_domain}</td>
              <td>{data.partnership_type}</td>
              <td>{data.date_scraped}</td>
              <td>
                <a href={data.url_scraped_from} target="_blank" rel="noopener noreferrer">
                      {data.url_scraped_from}
                    </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PartnershipTable;