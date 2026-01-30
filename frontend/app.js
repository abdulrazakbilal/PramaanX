// frontend/app.js
const API_URL = "http://127.0.0.1:8000";
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

async function startListening() {
    isRecording = true;
    document.getElementById("startBtn").style.display = "none";
    document.getElementById("stopBtn").style.display = "block";
    addMessage("Microphone Active. Listening...", "user-msg");

    // 1. Get Microphone Permission
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
        // 2. Prepare Audio File
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        audioChunks = []; // Reset for next time
        
        await processAudio(audioBlob);
    };

    mediaRecorder.start();
}

function stopListening() {
    isRecording = false;
    document.getElementById("startBtn").style.display = "block";
    document.getElementById("stopBtn").style.display = "none";
    
    // This triggers the 'onstop' event above
    mediaRecorder.stop();
    addMessage("Processing Audio...", "user-msg");
}

async function processAudio(audioBlob) {
    const formData = new FormData();
    formData.append("file", audioBlob, "recording.wav");

    try {
        // Step A: Transcribe (Voice -> Text)
        const transResponse = await fetch(`${API_URL}/upload-audio`, {
            method: "POST",
            body: formData
        });
        const transData = await transResponse.json();
        const text = transData.transcription;
        
        addMessage(`YOU: "${text}"`, "user-msg");

        // Step B: Analyze (Text -> Bribe Detection)
        const analyzeResponse = await fetch(`${API_URL}/analyze-interaction`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text })
        });
        const analyzeData = await analyzeResponse.json();
        
        // Parse the JSON string returned by Ollama
        // (Sometimes LLMs add extra text, so we handle it carefully)
        let analysis;
        try {
            // Find the JSON part inside the response
            const jsonStr = analyzeData.analysis.substring(
                analyzeData.analysis.indexOf('{'), 
                analyzeData.analysis.lastIndexOf('}') + 1
            );
            analysis = JSON.parse(jsonStr);
        } catch (e) {
            console.log("Raw LLM response:", analyzeData.analysis);
            analysis = { is_bribe: false }; // Fallback
        }

        // Step C: Display Results
        if (analysis.is_bribe) {
            const alertHTML = `
                <strong>⚠️ BRIBE DETECTED!</strong><br>
                SUGGESTION: "${analysis.suggestion}"
            `;
            addMessage(alertHTML, "alert-msg");

            // SHOW THE REPORT BUTTON
            document.getElementById("reportBtn").style.display = "block";
            
            // Auto-Check Rules if relevant (Bonus)
            checkOfficialRules(text);
        } else {
            addMessage("✅ Interaction seems safe.", "ai-msg");
        }

    } catch (error) {
        console.error("Error:", error);
        addMessage("❌ Error connecting to Brain.", "alert-msg");
    }
}

async function checkOfficialRules(text) {
    // Optional: Checks if the user mentioned a specific service
    const ruleResponse = await fetch(`${API_URL}/verify-rule`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
    });
    const ruleData = await ruleResponse.json();
    if (ruleData.source !== "N/A") {
         addMessage(`📜 OFFICIAL FACT CHECK:<br>${ruleData.fact}`, "ai-msg");
    }
}

function addMessage(html, className) {
    const div = document.createElement("div");
    div.className = `message ${className}`;
    div.innerHTML = html;
    document.getElementById("transcript").appendChild(div);
    document.getElementById("transcript").scrollTop = document.getElementById("transcript").scrollHeight;
}


async function generateReport() {
    // Get the last user message text (Hack for demo)
    const messages = document.getElementsByClassName("user-msg");
    const lastText = messages[messages.length - 1].innerText.replace('YOU: "', '').replace('"', '');
    
    addMessage("Generating Legal Documents...", "ai-msg");
    
    const response = await fetch(`${API_URL}/generate-complaint`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: lastText })
    });
    
    if (response.ok) {
        // Trigger file download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "PramaanX_Legal_Complaint.pdf";
        document.body.appendChild(a);
        a.click();
        addMessage("✅ Complaint Downloaded!", "ai-msg");
    }
}