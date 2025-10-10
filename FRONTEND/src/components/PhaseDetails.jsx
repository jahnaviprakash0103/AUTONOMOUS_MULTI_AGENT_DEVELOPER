import React from "react";

function PhaseDetails({ details }) {
    if (!details || details.error) return null;

    return (
        <div className="phase-details">
            <h3>Phase 1 Details</h3>
            <p>
                <strong>{details.phase_name}</strong>: {details.description}
            </p>
        </div>
    );
}

export default PhaseDetails;
