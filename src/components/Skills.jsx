import React from "react";
const Skills = ({ data }) => (
  <div className="card">
    <h2>Skills</h2>
    <div className="skills-list">
      {data.length > 0 ? (
        data.map((skillObj, index) => (
          <span key={index} className="skill">{skillObj.skill}</span>
        ))
      ) : (
        <p>No skills found.</p>
      )}
    </div>
  </div>
);

export default Skills;
