import React from "react";
const Education = ({ data }) => (
  <div className="card">
    <h2>Education</h2>
    {data.length > 0 ? (
      data.map((edu, index) => (
        <div key={index}>
          <h3>{edu.degree}</h3>
          <p>{edu.institution}, {edu.location} ({edu.start_date} - {edu.completion_date})</p>
        </div>
      ))
    ) : (
      <p>No education details found.</p>
    )}
  </div>
);

export default Education;
