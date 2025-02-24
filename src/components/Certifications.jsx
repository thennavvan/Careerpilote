import React from "react"; // ✅ Add this line
const Certifications = ({ data }) => (
  <div className="card">
    <h2>Certifications</h2>
    <div className="certification-list">
      {data.length > 0 ? (
        data.map((certObj, index) => (
          <span key={index} className="certification-item">
            {certObj.certification} {/* ✅ Extract the correct field */}
          </span>
        ))
      ) : (
        <p>No certifications found.</p>
      )}
    </div>
  </div>
);

export default Certifications;

