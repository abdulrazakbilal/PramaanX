# backend/create_sample_pdf.py
from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'GOVERNMENT OF ANDHRA PRADESH - TRANSPORT DEPARTMENT', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

def create_dummy_pdf():
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Content simulating the Government Order
    content = [
        "G.O.Ms.No. 123 - Dated: 01-01-2025",
        "SUBJECT: REVISED FEE STRUCTURE FOR RTO SERVICES",
        "",
        "The following are the official fees for services in Kurnool RTO.",
        "Any demand exceeding these amounts is a violation of the Prevention of Corruption Act.",
        "",
        "1. LEARNER LICENSE (LL):",
        "   - Official Fee: Rs. 500",
        "   - Allowed Service Charge: Rs. 50",
        "   - Documents: Aadhar, Address Proof",
        "",
        "2. PERMANENT DRIVING LICENSE (DL):",
        "   - Official Fee: Rs. 1200",
        "   - Allowed Service Charge: Rs. 100",
        "   - Documents: Valid LL, Medical Cert",
        "",
        "3. VEHICLE TRANSFER (OWNERSHIP):",
        "   - Official Fee: Rs. 1500",
        "   - Allowed Service Charge: Rs. 200",
        "   - Documents: Form 29, Form 30",
        "",
        "IMPORTANT NOTICE:",
        "Officers asking for 'Bribes' or 'Speed Money' will face suspension.",
        "Report strictly via PramaanX."
    ]

    for line in content:
        pdf.cell(0, 10, txt=line, ln=True)

    # Ensure directory exists
    output_path = os.path.join("backend", "data", "rules_pdfs", "ap_rto_fees.pdf")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    pdf.output(output_path)
    print(f"✅ Dummy PDF created successfully at: {output_path}")

if __name__ == "__main__":
    create_dummy_pdf()