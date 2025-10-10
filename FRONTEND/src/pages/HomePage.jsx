import React, { useState } from "react";
import IdeaForm from "../components/IdeaForm";
import ProjectPhases from "../components/ProjectPhase";
import PhaseDetails from "../components/PhaseDetails";
import Loader from "../components/Loader";
import { sendProjectIdea } from "../api/api";

function HomePage() {
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState(null);

    const handleIdeaSubmit = async (idea) => {
        setLoading(true);
        const data = await sendProjectIdea(idea);
        setResponse(data);
        setLoading(false);
    };

    return (
        <div className="container">
            <h1>Project Idea Planner</h1>
            <IdeaForm onSubmit={handleIdeaSubmit} loading={loading} />
            {loading && <Loader />}

            {response && (
                <div className="result">
                    {response.error && <p className="error">{response.error}</p>}
                    {response.project_plan && (
                        <ProjectPhases projectPlan={response.project_plan} />
                    )}
                    {response.phase1_details && (
                        <PhaseDetails details={response.phase1_details} />
                    )}
                </div>
            )}
        </div>
    );
}

export default HomePage;
