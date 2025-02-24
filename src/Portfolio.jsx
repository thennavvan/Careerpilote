import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import "./styles.css";
import React from "react";

const Portfolio = () => {
    const { id } = useParams();
    const [userData, setUserData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const response = await fetch(`http://localhost:3000/api/user/${id}`);
                const data = await response.json();
                console.log("Fetched Data:", data);
                setUserData(data);
            } catch (error) {
                console.error("Error fetching user data:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchUserData();
    }, [id]);

    if (loading) return <h2>Loading portfolio...</h2>;
    if (!userData || Object.keys(userData).length === 0) return <h2>User data not found</h2>;

    return (
        <div className="container">
            {/* ✨ Personal Info */}
            {userData.personal_info && (
                <div className="personal-info">
                    <h1>{userData.personal_info.name || "No Name Provided"}</h1>
                    <p>Email: {userData.personal_info.email || "N/A"}</p>
                    <p>Phone: {userData.personal_info.phone || "N/A"}</p>
                </div>
            )}

            {/* 🎓 Education */}
            <div className="section">
                <h2>Education</h2>
                <ul>
                    {userData.education?.length ? (
                        userData.education.map((edu, index) => (
                            <li key={index}>
                                <strong>{edu.degree || "No Degree"}</strong> at {edu.institution || "No Institution"}
                                ({edu.start_date || "Start Date N/A"} - {edu.completion_date || "End Date N/A"})
                            </li>
                        ))
                    ) : (
                        <p>No education details available.</p>
                    )}
                </ul>
            </div>

            {/* 💡 Skills */}
            <div className="section">
                <h2>Skills</h2>
                <div className="skills-list">
                    {userData.skills?.length ? (
                        userData.skills.map((skill, index) => (
                            <span key={index} className="skill-badge">{skill.skill || "No Skill Provided"}</span>
                        ))
                    ) : (
                        <p>No skills available.</p>
                    )}
                </div>
            </div>

            {/* 🔥 Work Experience */}
            <div className="section">
                <h2>Work Experience</h2>
                {userData.work_experience?.length ? (
                    userData.work_experience.map((exp, index) => (
                        <div key={index} className="experience">
                            <h3>{exp.role || "No Role Provided"}</h3>
                            <ul>
                                {exp.details?.length ? (
                                    exp.details.map((detail, i) => <li key={i}>{detail}</li>)
                                ) : (
                                    <li>No details provided.</li>
                                )}
                            </ul>
                        </div>
                    ))
                ) : (
                    <p>No work experience available.</p>
                )}
            </div>

            {/* 🚀 Projects */}
            <div className="section">
                <h2>Projects</h2>
                {userData.projects?.length ? (
                    userData.projects.map((proj, index) => (
                        <div key={index} className="project">
                            <h3>{proj.title || "No Title Provided"}</h3>
                            <ul>
                                {proj.description?.length ? (
                                    proj.description.map((desc, i) => <li key={i}>{desc}</li>)
                                ) : (
                                    <li>No description provided.</li>
                                )}
                            </ul>
                        </div>
                    ))
                ) : (
                    <p>No projects available.</p>
                )}
            </div>

            {/* 🎖 Certifications */}
            <div className="section">
                <h2>Certifications</h2>
                <div className="certifications-list">
                    {userData.certifications?.length ? (
                        userData.certifications.map((cert, index) => (
                            <div key={index} className="certification">
                                <p>{cert.certification || "No Certification Provided"}</p>
                            </div>
                        ))
                    ) : (
                        <p>No certifications available.</p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Portfolio;
