const form = document.getElementById("prediction-form");
const resultEmpty = document.getElementById("result-empty");
const resultCard = document.getElementById("result-card");
const predictedClass = document.getElementById("predicted-class");
const predictedProbability = document.getElementById("predicted-probability");
const riskLevel = document.getElementById("risk-level");
const apiMessage = document.getElementById("api-message");
const historyBody = document.getElementById("history-body");
const refreshHistory = document.getElementById("refresh-history");

function normalizeFormValue(key, value) {
    const integerFields = ["quejas_recientes", "antiguedad_meses"];
    if (integerFields.includes(key)) return Number.parseInt(value, 10);
    if (key === "distrito") return value;
    return Number.parseFloat(value);
}

function renderResult(data) {
    resultEmpty.classList.add("hidden");
    resultCard.classList.remove("hidden");
    predictedClass.textContent = data.predicted_class;
    predictedProbability.textContent = `${(data.predicted_probability * 100).toFixed(2)}%`;
    riskLevel.textContent = data.risk_level;
    riskLevel.className = `badge ${data.risk_level}`;
    apiMessage.textContent = JSON.stringify(data, null, 2);
}

function renderHistory(rows) {
    if (!rows.length) {
        historyBody.innerHTML = `<tr><td colspan="6">Sin registros todavia.</td></tr>`;
        return;
    }

    historyBody.innerHTML = rows.map((row) => `
        <tr>
            <td>${row.id}</td>
            <td>${row.distrito}</td>
            <td>${row.predicted_class}</td>
            <td>${(row.predicted_probability * 100).toFixed(2)}%</td>
            <td>${row.risk_level}</td>
            <td>${new Date(row.created_at).toLocaleString()}</td>
        </tr>
    `).join("");
}

async function loadHistory() {
    try {
        const response = await fetch("/api/history");
        const data = await response.json();
        renderHistory(data);
    } catch (error) {
        historyBody.innerHTML = `<tr><td colspan="6">No se pudo cargar el historial.</td></tr>`;
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const payload = {};

    for (const [key, value] of formData.entries()) {
        payload[key] = normalizeFormValue(key, value);
    }

    apiMessage.textContent = "Consultando API...";

    try {
        const response = await fetch("/api/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (!response.ok) {
            apiMessage.textContent = JSON.stringify(data, null, 2);
            return;
        }

        renderResult(data);
        loadHistory();
    } catch (error) {
        apiMessage.textContent = `Error al consumir la API: ${error.message}`;
    }
});

refreshHistory.addEventListener("click", loadHistory);
loadHistory();
