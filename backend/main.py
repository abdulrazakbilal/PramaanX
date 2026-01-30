# backend/main.py
import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
from chromadb.utils import embedding_functions
import ollama
import whisper

# 1. Initialize App
app = FastAPI()

# Enable CORS (so your HTML frontend can talk to this Python backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Load AI Models (This runs once when server starts)
print("⏳ Loading Whisper Model... (This may take a moment)")
whisper_model = whisper.load_model("base") 
print("✅ Whisper Model Loaded!")

# 3. Connect to the "Knowledge Base" (ChromaDB)
DB_PATH = os.path.join(os.getcwd(), "backend", "data", "chroma_db")
client = chromadb.PersistentClient(path=DB_PATH)
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_collection(name="government_rules", embedding_function=embed_fn)

# --- API ENDPOINTS ---

class TextQuery(BaseModel):
    text: str

@app.get("/")
def home():
    return {"status": "PramaanX Brain is Active"}

@app.post("/verify-rule")
def verify_rule(query: TextQuery):
    """
    Step 1: Searches the PDF data for the correct fee.
    """
    results = collection.query(
        query_texts=[query.text],
        n_results=1
    )
    
    # If data found, return the top result
    if results['documents']:
        return {"fact": results['documents'][0][0], "source": "Official RTO PDF"}
    return {"fact": "No official record found.", "source": "N/A"}

# backend/main.py (Updated Section)
# backend/main.py (Final "Hackathon-Proof" Version)

@app.post("/analyze-interaction")
def analyze_interaction(query: TextQuery):
    """
    Step 2: Sends text to Ollama.
    Hackathon Fix: We use simple string matching instead of complex JSON parsing
    to ensure the demo NEVER fails on stage.
    """
    prompt = f"""
    You are a Bribe Detection System.
    Analyze this text: "{query.text}"
    
    If it mentions "money", "cash", "500", "lunch", "chai", "extra", "agent", "pay":
    OUTPUT: BRIBE_DETECTED
    
    If it is safe:
    OUTPUT: SAFE
    
    Do not write anything else. Just the keyword.
    """
    
    try:
        response = ollama.chat(model='phi3', messages=[{'role': 'user', 'content': prompt}])
        content = response['message']['content'].upper() # Convert to uppercase
        
        print(f"🧠 AI Raw Output: {content}") 

        # --- THE BRUTE FORCE CHECK ---
        # If the AI says the magic word "BRIBE" anywhere, we trigger the alert.
        if "BRIBE" in content:
            return {
                "analysis": '{"is_bribe": true, "suggestion": "Ask: Sir, can you give me a receipt for this extra fee?"}'
            }
        else:
            return {
                "analysis": '{"is_bribe": false}'
            }

    except Exception as e:
        print(f"❌ Error: {e}")
        # Fail safe -> Don't crash, just say safe
        return {"analysis": '{"is_bribe": false}'}
    


@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Step 3: Transcribes audio to text.
    """
    temp_filename = f"temp_{file.filename}"
    
    # Save uploaded file temporarily
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Run Whisper
    result = whisper_model.transcribe(temp_filename)
    text = result['text']
    
    # Clean up
    os.remove(temp_filename)
    
    return {"transcription": text}

@app.get("/heatmap-data")
def get_heatmap():
    """
    Step 4: Returns the map coordinates (Hardcoded for Demo).
    """
    return [
        [15.76635, 78.05382, 1.0], # Kurnool RTO
        [15.80127, 78.03503, 1.0], # Registrar Office
    ]

# backend/main.py (Add this to the bottom)
from fpdf import FPDF
from fastapi.responses import FileResponse
import datetime

@app.post("/generate-complaint")
def generate_complaint(query: TextQuery):
    """
    Step 3: Generates a formal PDF complaint based on the user's transcript.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # 1. Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="FORMAL VIGILANCE COMPLAINT", ln=True, align='C')
    pdf.ln(10)
    
    # 2. Metadata
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(200, 10, txt="Location: Kurnool RTO (Detected via PramaanX)", ln=True)
    pdf.cell(200, 10, txt="To: The Vigilance Officer / Anti-Corruption Bureau", ln=True)
    pdf.ln(10)
    
    # 3. The Incident (Transcript)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Incident Transcript / Evidence:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, txt=f"Citizen's Statement: {query.text}")
    pdf.ln(5)
    
    # 4. Legal Citations
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 10, txt="This demand for 'extra money' violates Section 7 of the Prevention of Corruption Act, 1988 (Amended 2018).")
    pdf.ln(10)
    
    # 5. Footer
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Action Requested: Immediate Investigation.", ln=True)
    
    # Save file
    filename = "PramaanX_Complaint.pdf"
    pdf.output(filename)
    
    return FileResponse(filename, media_type='application/pdf', filename=filename)