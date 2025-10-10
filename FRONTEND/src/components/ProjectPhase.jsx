import React from "react";

function ProjectPhases({ projectPlan }) {
    if (!projectPlan) return null;

    return (
        <div className="project-phases">
            <h2>{projectPlan.project_title || "Project Plan"}</h2>
            <ol>
                {projectPlan.phases?.map((phase, idx) => (
                    <li key={idx}>
                        <strong>{phase.phase_name}</strong>: {phase.description}
                    </li>
                ))}
            </ol>
        </div>
    );
}

export default ProjectPhases;
