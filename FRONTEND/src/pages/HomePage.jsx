import React, { useState } from "react";
import IdeaForm from "../components/IdeaForm";
import Loader from "../components/Loader";
import { sendProjectIdea } from "../api/api";

// Optional: use a code highlighter
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

function HomePage() {
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState(null);
    const [files, setFiles] = useState([]);

    const handleIdeaSubmit = async (idea) => {
        setLoading(true);
        setResponse(null);
        setFiles([]);

        try {
            const data = await sendProjectIdea(idea);
            setResponse(data);

            // If backend returned generated files
            if (data.files && Array.isArray(data.files)) {
                setFiles(data.files);
            }
        } catch (error) {
            console.error("Error submitting idea:", error);
            setResponse({ error: "Failed to process idea." });
        }

        setLoading(false);
    };

    // ✅ Function to safely extract JSON code blocks from text_response
    const parseTextResponse = (text) => {
        if (!text) return null;
        try {
            const jsonMatch = text.match(/```json\n([\s\S]*?)```/);
            if (jsonMatch) {
                return JSON.parse(jsonMatch[1]);
            }
        } catch (err) {
            console.error("Error parsing JSON from response:", err);
        }
        return null;
    };

    const parsedCodeResponse = parseTextResponse(response?.text_response);

    // ✅ Download all files as ZIP
    const handleDownloadAll = () => {
        // assuming backend serves a route like /download/all
        window.open("http://127.0.0.1:8000/download/all", "_blank");
    };

    return (
        <div className="container" style={{ padding: "2rem" }}>
            <h1>🚀 Autonomous Developer</h1>
            <p>Enter your project idea and watch the AI agents build it step by step.</p>

            <IdeaForm onSubmit={handleIdeaSubmit} loading={loading} />
            {loading && <Loader />}

            {response && (
                <div className="result" style={{ marginTop: "2rem" }}>
                    {response.error && (
                        <p className="error" style={{ color: "red" }}>{response.error}</p>
                    )}

                    {response.message && (
                        <p style={{ color: "green", fontWeight: "bold" }}>{response.message}</p>
                    )}

                    {/* 📦 Download All Button */}
                    {files.length > 0 && (
                        <div style={{ marginTop: "2rem" }}>
                            <button
                                onClick={handleDownloadAll}
                                style={{
                                    backgroundColor: "#007bff",
                                    color: "white",
                                    padding: "10px 16px",
                                    border: "none",
                                    borderRadius: "8px",
                                    cursor: "pointer",
                                    fontWeight: "bold",
                                }}
                            >
                                📦 Download All Files (ZIP)
                            </button>
                        </div>
                    )}

                    {/* 📂 File Downloads */}
                    {files.length > 0 && (
                        <div style={{ marginTop: "2rem" }}>
                            <h2>📁 Individual Files</h2>
                            <ul>
                                {files.map((file) => (
                                    <li key={file.name}>
                                        <a
                                            href={file.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            style={{ color: "#007bff" }}
                                        >
                                            {file.name}
                                        </a>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* 🧩 Phase Outputs */}
                    {response.phases && (
                        <div style={{ marginTop: "2rem" }}>
                            <h2>🧠 Phase Outputs</h2>
                            {Object.entries(response.phases).map(([phaseName, phaseData]) => (
                                <div
                                    key={phaseName}
                                    style={{
                                        marginTop: "1.5rem",
                                        border: "1px solid #ccc",
                                        borderRadius: "10px",
                                        padding: "1rem",
                                    }}
                                >
                                    <h3>{phaseName}</h3>

                                    {/* 👩‍💻 Developer Output */}
                                    {phaseData.developer?.length > 0 && (
                                        <div style={{ marginTop: "1rem" }}>
                                            <h4>💻 Developer Code</h4>
                                            {phaseData.developer.map((dev, index) => (
                                                <div key={index} style={{ marginBottom: "1rem" }}>
                                                    <strong>🗓 {dev.day} - {dev.task}</strong>
                                                    {dev.result?.code && (
                                                        <SyntaxHighlighter
                                                            language="python"
                                                            style={oneDark}
                                                            customStyle={{
                                                                borderRadius: "8px",
                                                                marginTop: "0.5rem",
                                                            }}
                                                        >
                                                            {typeof dev.result.code === "string"
                                                                ? dev.result.code
                                                                : JSON.stringify(dev.result.code, null, 2)}
                                                        </SyntaxHighlighter>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {/* 🧪 QA Output */}
                                    {phaseData.qa?.length > 0 && (
                                        <div style={{ marginTop: "1rem" }}>
                                            <h4>🧪 QA Test Cases</h4>
                                            {phaseData.qa.map((qa, index) => (
                                                <SyntaxHighlighter
                                                    key={index}
                                                    language="json"
                                                    style={oneDark}
                                                    customStyle={{
                                                        borderRadius: "8px",
                                                        marginTop: "0.5rem",
                                                    }}
                                                >
                                                    {JSON.stringify(qa.test_cases, null, 2)}
                                                </SyntaxHighlighter>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default HomePage;
