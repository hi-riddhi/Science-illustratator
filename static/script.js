
const diagramList = document.getElementById("diagram-list");
const globalError = document.getElementById("global-error");

let concepts = [];
let results = [];

async function apiRequest(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "Request failed.");
    }

    return data;
}

function showError(message) {
    globalError.textContent = message;
    globalError.classList.remove("hidden");
}

function clearError() {
    globalError.textContent = "";
    globalError.classList.add("hidden");
}

function updateSummary() {
    document.getElementById("total-count").textContent = concepts.length;

    document.getElementById("generated-count").textContent =
        results.filter(item => item.svg).length;

    document.getElementById("approved-count").textContent =
        results.filter(item => item.review_status === "Approved").length;

    document.getElementById("rejected-count").textContent =
        results.filter(item => item.review_status === "Rejected").length;
}

function createElement(tag, className, text) {
    const element = document.createElement(tag);

    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;

    return element;
}

function renderDiagram(concept) {
    const result = results.find(
        item => item.concept === concept.concept
    );

    const card = createElement("article", "diagram-card");

    const header = createElement("div", "diagram-header");
    const heading = document.createElement("div");

    heading.append(
        createElement("h3", "", concept.concept),
        createElement("p", "", concept.subject)
    );

    const reviewStatus = result?.review_status || "Pending";

    header.append(
        heading,
        createElement("span", `status ${reviewStatus.toLowerCase()}`, reviewStatus)
    );

    card.appendChild(header);

    const preview = createElement("div", "preview");

    if (result?.svg) {
        const frame = document.createElement("iframe");
        frame.title = `${concept.concept} diagram`;
        frame.setAttribute("sandbox", "");
        frame.srcdoc = result.svg;
        preview.appendChild(frame);
    } else {
        preview.appendChild(
            createElement("div", "empty-preview", "No diagram generated yet.")
        );
    }

    card.appendChild(preview);

    if (result?.checks) {
        const validation = createElement("div", "validation");

        for (const [name, passed] of Object.entries(result.checks)) {
            validation.appendChild(
                createElement(
                    "span",
                    passed ? "check" : "check failed",
                    `${passed ? "✓" : "✕"} ${name}`
                )
            );
        }

        card.appendChild(validation);
    }

    if (result?.error) {
        card.appendChild(
            createElement("div", "error-message", result.error)
        );
    }

    const metadata = createElement("div", "metadata");

    const metadataItems = [
        ["Model", result?.model || "Not generated"],
        ["Input tokens", result?.input_tokens ?? "—"],
        ["Output tokens", result?.output_tokens ?? "—"],
        ["Estimated cost", result?.estimated_cost_usd !== undefined
            ? `$${result.estimated_cost_usd}` : "—"],
        ["Retries", result?.retries ?? "—"],
        ["Validation", result
            ? (result.passed ? "Passed" : "Failed") : "Pending"]
    ];

    for (const [label, value] of metadataItems) {
        const item = document.createElement("div");
        item.append(
            createElement("span", "", label),
            createElement("strong", "", String(value))
        );
        metadata.appendChild(item);
    }

    card.appendChild(metadata);

    const note = document.createElement("textarea");
    note.className = "review-note";
    note.placeholder = "Add reviewer notes...";
    note.value = result?.review_note || "";

    card.appendChild(note);

    const actions = createElement("div", "review-actions");

    const generateButton = createElement(
        "button",
        "primary-button",
        result?.svg ? "Regenerate" : "Generate diagram"
    );

    generateButton.addEventListener("click", async () => {
        generateButton.disabled = true;
        generateButton.textContent = "Generating...";
        clearError();

        try {
            await apiRequest(`/api/generate/${concept.id}`, {
                method: "POST"
            });

            await refreshData();
        } catch (error) {
            showError(error.message);
            generateButton.disabled = false;
            generateButton.textContent = "Try again";
        }
    });

    actions.appendChild(generateButton);

    const approveButton = createElement(
        "button", "approve-button", "Approve"
    );

    const rejectButton = createElement(
        "button", "reject-button", "Reject"
    );

    approveButton.disabled = !result?.svg;
    rejectButton.disabled = !result?.svg;

    async function saveReview(status) {
        approveButton.disabled = true;
        rejectButton.disabled = true;
        clearError();

        try {
            await apiRequest(`/api/review/${concept.id}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    status: status,
                    note: note.value
                })
            });

            await refreshData();
        } catch (error) {
            showError(error.message);
            approveButton.disabled = false;
            rejectButton.disabled = false;
        }
    }

    approveButton.addEventListener("click", () => saveReview("Approved"));
    rejectButton.addEventListener("click", () => saveReview("Rejected"));

    actions.append(approveButton, rejectButton);
    card.appendChild(actions);

    return card;
}

function renderAll() {
    diagramList.replaceChildren();

    for (const concept of concepts) {
        diagramList.appendChild(renderDiagram(concept));
    }

    updateSummary();
}

async function refreshData() {
    clearError();

    const [newConcepts, newResults] = await Promise.all([
        apiRequest("/api/concepts"),
        apiRequest("/api/results")
    ]);

    concepts = newConcepts;
    results = newResults;

    renderAll();
}

async function initialize() {
    try {
        await refreshData();
    } catch (error) {
        showError(error.message);
        diagramList.textContent = "Could not load the application.";
    }
}

document.getElementById("refresh-button").addEventListener(
    "click", initialize
);

initialize();
