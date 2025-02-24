import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Home.css";
import React from "react";

export default function Home() {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState(null);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  const handleFileUpload = (event, type) => {
    const file = event.target.files[0];
    if (type === "resume") setResume(file);
    else setJobDescription(file);
  };

  const handlePortfolioCreation = async () => {
    if (!resume) {
      alert("Please select a resume to upload!");
      return;
    }
    setUploading(true);
    const formData = new FormData();
    formData.append("file", resume);

    try {
      const response = await fetch("http://localhost:3000/api/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (response.ok) {
        alert("Upload successful! Generating portfolio...");
        navigate(`/user/${data.user_id}`);
      } else {
        alert("Upload failed: " + data.message);
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Error uploading file.");
    }

    setUploading(false);
  };

  const handlePrepStart = () => {
    navigate("/user/chat");
  };

  return (
    <div className="container">
      <h1 className="title">Job Application Assistant</h1>
      
      <div className="upload-section">
        <div className="upload-box">
          <input type="file" accept="application/pdf" onChange={(e) => handleFileUpload(e, "resume")} id="resume-upload" hidden />
          <label htmlFor="resume-upload" className="upload-label">{resume ? resume.name : "Upload Resume"}</label>
        </div>

        <div className="upload-box">
          <input type="file" onChange={(e) => handleFileUpload(e, "jd")} id="jd-upload" hidden />
          <label htmlFor="jd-upload" className="upload-label">{jobDescription ? jobDescription.name : "Upload Job Description"}</label>
        </div>
      </div>
      
      <div className="button-section">
        <button className="feature-button" onClick={handlePortfolioCreation} disabled={uploading}>
          {uploading ? "Uploading..." : "Create Portfolio"}
        </button>
        <button className="feature-button" onClick={handlePrepStart}>Interview Prep</button>
        <button className="feature-button">Resume Optimizer</button>
        <button className="feature-button">Skill Gap Analysis</button>
      </div>

      <div className="info-section">
        <h2 className="info-title">How It Works</h2>
        <div className="feature-card">
          <h3>Portfolio Creation</h3>
          <p>Generate a professional portfolio from your resume.</p>
        </div>
        <div className="feature-card">
          <h3>Interview Prep</h3>
          <p>Upload a job description and receive AI-generated interview Q&A.</p>
        </div>
        <div className="feature-card">
          <h3>Resume Optimizer</h3>
          <p>Improve your resume with corrections, enhancements, and scoring.</p>
        </div>
        <div className="feature-card">
          <h3>Skill Gap Analysis</h3>
          <p>Identify skill gaps and receive suggested improvements based on the job description.</p>
        </div>
      </div>
    </div>
  );
}
