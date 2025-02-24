import React from "react";
const Projects = ({ data }) => (
  <div className="card">
    <h2>Projects</h2>
    {data.length > 0 ? (
      data.map((proj, index) => (
        <div key={index}>
          <h3>{proj.title}</h3>
          <p>{proj.description}</p>
        </div>
      ))
    ) : (
      <p>No projects found.</p>
    )}
  </div>
);

export default Projects;
