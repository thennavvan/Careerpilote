import React from "react";
const PersonalInfo = ({ data }) => {
  return (
    <div className="card">
      <h2>Personal Info</h2>
      <p><strong>Name:</strong> {data?.name || "N/A"}</p>
      <p><strong>Email:</strong> {data?.email || "N/A"}</p>
      <p><strong>Phone:</strong> {data?.phone || "N/A"}</p>
      <p>
        <strong>LinkedIn:</strong> <a href={data?.linkedin} target="_blank">{data?.linkedin}</a>
      </p>
      <p>
        <strong>GitHub:</strong> <a href={data?.github} target="_blank">{data?.github}</a>
      </p>
    </div>
  );
};

export default PersonalInfo;
