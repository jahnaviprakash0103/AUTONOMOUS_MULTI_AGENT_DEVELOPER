// Simple API helper
export const sendProjectIdea = async (idea) => {
    try {
        const response = await fetch("http://127.0.0.1:8000/api/project/idea", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ idea }),
        });

        if (!response.ok) throw new Error("API error");

        return await response.json();
    } catch (err) {
        console.error(err);
        return { error: err.message };
    }
};
