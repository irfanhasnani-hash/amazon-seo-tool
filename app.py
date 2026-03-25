import streamlit as st
from fpdf import FPDF

# --- PDF GENERATOR FUNCTION ---
def create_pdf(score, report):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Amazon SEO Audit Report (2026)", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, f"Overall SEO Score: {score}%", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 12)
    for line in report:
        # Remove emojis for PDF compatibility
        clean_line = line.replace("✅", "PASS:").replace("❌", "FAIL:").replace("⚠️", "WARN:").replace("🚫", "ALERT:")
        pdf.multi_cell(0, 10, clean_line)
    
    return pdf.output(dest="S").encode("latin-1")

# --- (Keep your existing deep_audit function here) ---
def deep_audit(title, bullets, description, category):
    # ... [Same logic as before] ...
    score = 0
    reports = []
    if 80 <= len(title) <= 150: score += 35; reports.append("✅ **Title Length:** Perfect.")
    elif len(title) > 200: reports.append("❌ **Title Alert:** Too long.")
    else: score += 15; reports.append("⚠️ **Title Alert:** Too short.")
    
    valid_bullets = [b for b in bullets if len(b.strip()) > 10]
    if len(valid_bullets) == 5: score += 25; reports.append("✅ **Bullet Points:** All 5 used.")
    else: reports.append(f"❌ **Bullet Points:** Using {len(valid_bullets)}/5.")
    
    restricted = ["best", "cheap", "free", "guaranteed"]
    found = [w for w in restricted if w in title.lower() or description.lower()]
    if found: score -= 20; reports.append(f"🚫 **Policy Risk:** Restricted words found.")
    
    if len(description) > 1000: score += 20; reports.append("✅ **Description:** Detailed.")
    else: score += 5; reports.append("⚠️ **Description:** Thin.")
    
    return min(max(score, 0), 100), reports

# --- UI DESIGN ---
st.set_page_config(page_title="Amazon SEO Master 2026", layout="wide")
st.title("🛡️ Amazon SEO Accuracy Tool")

with st.sidebar:
    st.header("Listing Data")
    title_in = st.text_area("Product Title")
    desc_in = st.text_area("Description")
    b_ins = [st.text_input(f"Bullet {i+1}") for i in range(5)]
    run_btn = st.button("🚀 RUN 100% ACCURATE AUDIT")

if run_btn:
    final_score, feedback = deep_audit(title_in, b_ins, desc_in, "General")
    st.metric("SEO SCORE", f"{final_score}%")
    for item in feedback:
        st.write(item)
    
    # PDF Download Button
    pdf_data = create_pdf(final_score, feedback)
    st.download_button(
        label="📥 Download PDF Audit Report",
        data=pdf_data,
        file_name="Amazon_SEO_Report.pdf",
        mime="application/pdf"
    )