import React, { useState } from "react";

function IdeaForm({ onSubmit, loading }) {
    const [idea, setIdea] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!idea.trim()) return;
        onSubmit(idea);
    };

    return (
        <form onSubmit={handleSubmit} className="idea-form">
            <textarea
                value={idea}
                onChange={(e) => setIdea(e.target.value)}
                placeholder="Enter your project idea..."
                rows={5}
            />
            <button type="submit" disabled={loading}>
                {loading ? "Processing..." : "Generate Phases"}
            </button>
        </form>
    );
}

export default IdeaForm;
