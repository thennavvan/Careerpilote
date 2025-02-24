import React from "react"; // ✅ Add this line
const WorkExperience = ({ data }) => (
  <div className="card">
    <h2>Work Experience</h2>
    <div className="experience-list">
      {data.length > 0 ? (
        data.map((job, index) => (
          <div key={index} className="experience-item">
            <h3>{job.role} at {job.company}</h3>
            <p><strong>Duration:</strong> {job.start_date} - {job.end_date}</p>
            <ul>
              {job.details.map((detail, i) => (
                <li key={i}>{detail}</li>
              ))}
            </ul>
          </div>
        ))
      ) : (
        <p>No work experience found.</p>
      )}
    </div>
  </div>
);

export default WorkExperience;

  