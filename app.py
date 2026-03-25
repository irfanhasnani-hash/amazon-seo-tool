import streamlit as st
from fpdf import FPDF
import re
from collections import Counter

# ─────────────────────────────────────────────
# PDF GENERATOR
# ─────────────────────────────────────────────
def create_pdf(score, report, asin="N/A"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Amazon SEO Deep Audit Report (2026)", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(200, 8, f"ASIN: {asin}", ln=True, align="C")
    pdf.ln(6)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, f"Overall SEO Score: {score}/100", ln=True)
    pdf.ln(4)
    pdf.set_font("Arial", "", 11)

    emoji_map = {
        "✅": "[PASS]", "❌": "[FAIL]", "⚠️": "[WARN]", "🚫": "[ALERT]",
        "💡": "[TIP]", "🔍": "[INFO]", "🏆": "[GRADE A]", "🥈": "[GRADE B]",
        "🥉": "[GRADE C]", "📌": ">>", "📊": ">>", "█": "#", "░": "-",
        "**": "", "───": "---",
    }

    for line in report:
        clean = line
        for emoji, replacement in emoji_map.items():
            clean = clean.replace(emoji, replacement)
        # Replace common problematic characters from user input
clean = clean.replace("\u2013", "-").replace("\u2014", "-").replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
clean = clean.encode("latin-1", errors="ignore").decode("latin-1")
        pdf.multi_cell(0, 8, clean)

    return pdf.output(dest="S").encode("latin-1")

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
RESTRICTED_WORDS = [
    "best", "cheap", "free", "guaranteed", "cure", "treat", "prevent",
    "#1", "number one", "top rated", "amazing", "incredible", "miracle"
]

HIGH_VALUE_SIGNALS = [
    "premium", "professional", "certified", "patented", "fda", "bpa-free",
    "eco-friendly", "organic", "lifetime warranty", "money back"
]

def word_count(text): return len(text.split())
def char_count(text): return len(text)
def keyword_density(text, keyword):
    words = re.findall(r'\b\w+\b', text.lower())
    kw_words = keyword.lower().split()
    count = sum(1 for i in range(len(words)) if words[i:i+len(kw_words)] == kw_words)
    return round((count / max(len(words), 1)) * 100, 2)

def extract_keywords(text, top_n=10):
    stopwords = {"the","a","an","and","or","for","in","on","with","to","of","is","it","this","that","are","be","as","at","by","from"}
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    filtered = [w for w in words if w not in stopwords]
    return Counter(filtered).most_common(top_n)

def readability_score(text):
    sentences = re.split(r'[.!?]', text)
    sentences = [s for s in sentences if len(s.strip()) > 0]
    words = text.split()
    if not sentences: return 0
    avg_words = len(words) / len(sentences)
    if avg_words <= 15: return "Easy ✅"
    elif avg_words <= 25: return "Moderate ⚠️"
    else: return "Hard ❌"

# ─────────────────────────────────────────────
# DEEP AUDIT ENGINE
# ─────────────────────────────────────────────
def deep_audit(title, bullets, description, backend_kw, category, price, asin):
    score = 0
    max_score = 0
    reports = []
    section_scores = {}

    full_text = f"{title} {' '.join(bullets)} {description} {backend_kw}".lower()

    # ── 1. TITLE AUDIT (25 pts) ──────────────────
    reports.append("─── 📌 TITLE ANALYSIS ───")
    max_score += 25
    tlen = char_count(title)
    if 150 <= tlen <= 200:
        score += 25; reports.append(f"✅ Title length: {tlen} chars — Optimal (150–200)")
    elif 100 <= tlen < 150:
        score += 18; reports.append(f"⚠️ Title length: {tlen} chars — Good but could be longer")
    elif tlen > 200:
        score += 10; reports.append(f"⚠️ Title length: {tlen} chars — May be truncated on mobile")
    else:
        score += 5; reports.append(f"❌ Title length: {tlen} chars — Too short, add more keywords")

    if title and title[0].isupper():
        reports.append("✅ Title starts with capital letter")
    else:
        reports.append("❌ Title should start with a capital letter")

    if re.search(r'\d', title):
        reports.append("✅ Title contains numbers (size/quantity) — good for CTR")
    else:
        reports.append("💡 Consider adding numbers (e.g., pack size, dimensions) to title")

    if "|" in title or "-" in title:
        reports.append("✅ Title uses separators for readability")
    else:
        reports.append("💡 Use ' | ' or ' - ' to separate key features in title")

    section_scores["Title"] = score

    # ── 2. BULLET POINTS AUDIT (20 pts) ──────────
    reports.append("─── 📌 BULLET POINTS ANALYSIS ───")
    prev = score
    max_score += 20
    valid_bullets = [b for b in bullets if len(b.strip()) > 10]
    bullet_score = 0

    if len(valid_bullets) == 5:
        bullet_score += 10; reports.append("✅ All 5 bullet points used")
    else:
        reports.append(f"❌ Only {len(valid_bullets)}/5 bullets filled — missing SEO real estate")

    caps_bullets = [b for b in valid_bullets if b.strip() and b.strip()[0].isupper()]
    if len(caps_bullets) == len(valid_bullets):
        bullet_score += 4; reports.append("✅ All bullets start with capital letters")
    else:
        reports.append("⚠️ Some bullets don't start with capitals — hurts readability")

    long_bullets = [b for b in valid_bullets if len(b) >= 150]
    if len(long_bullets) >= 3:
        bullet_score += 6; reports.append(f"✅ {len(long_bullets)} bullets are detailed (150+ chars)")
    else:
        reports.append(f"⚠️ Only {len(long_bullets)} bullets are detailed — aim for 150–250 chars each")

    score += bullet_score
    section_scores["Bullets"] = score - prev

    # ── 3. DESCRIPTION AUDIT (15 pts) ────────────
    reports.append("─── 📌 DESCRIPTION ANALYSIS ───")
    prev = score
    max_score += 15
    dlen = char_count(description)
    wcount = word_count(description)

    if dlen >= 1500:
        score += 15; reports.append(f"✅ Description: {dlen} chars — Excellent depth")
    elif dlen >= 1000:
        score += 10; reports.append(f"⚠️ Description: {dlen} chars — Good, aim for 1500+")
    elif dlen >= 500:
        score += 5; reports.append(f"⚠️ Description: {dlen} chars — Thin content")
    else:
        reports.append(f"❌ Description: {dlen} chars — Very thin, major SEO gap")

    reports.append(f"🔍 Readability: {readability_score(description)}")
    reports.append(f"🔍 Word count: {wcount} words")
    section_scores["Description"] = score - prev

    # ── 4. KEYWORD ANALYSIS (20 pts) ─────────────
    reports.append("─── 📌 KEYWORD INTELLIGENCE ───")
    prev = score
    max_score += 20

    top_kw = extract_keywords(full_text, 8)
    reports.append(f"🔍 Top keywords detected: {', '.join([k for k,_ in top_kw])}")

    if backend_kw.strip():
        bk_words = len(backend_kw.split())
        if bk_words >= 200:
            score += 10; reports.append(f"✅ Backend keywords: {bk_words} words — Maxed out")
        elif bk_words >= 100:
            score += 6; reports.append(f"⚠️ Backend keywords: {bk_words} words — Add more (target 200+)")
        else:
            score += 2; reports.append(f"❌ Backend keywords: {bk_words} words — Very low")

        # Check for repetition in backend
        bk_list = backend_kw.lower().split()
        duplicates = [w for w, c in Counter(bk_list).items() if c > 1]
        if duplicates:
            reports.append(f"⚠️ Duplicate backend keywords found: {', '.join(duplicates[:5])} — wasted space")
        else:
            score += 5; reports.append("✅ No duplicate backend keywords — efficient use of space")

        # Check if title keywords are in backend (redundancy check)
        title_words = set(re.findall(r'\b\w{4,}\b', title.lower()))
        bk_words_set = set(re.findall(r'\b\w{4,}\b', backend_kw.lower()))
        overlap = title_words & bk_words_set
        if overlap:
            reports.append(f"💡 Redundant keywords in backend (already in title): {', '.join(list(overlap)[:5])}")
        else:
            score += 5; reports.append("✅ Backend keywords are unique — no title overlap")
    else:
        reports.append("❌ No backend keywords provided — major indexing gap")

    section_scores["Keywords"] = score - prev

    # ── 5. POLICY & COMPLIANCE (10 pts) ──────────
    reports.append("─── 📌 POLICY & COMPLIANCE ───")
    prev = score
    max_score += 10
    found_restricted = [w for w in RESTRICTED_WORDS if w in full_text]
    if found_restricted:
        score -= 15
        reports.append(f"🚫 POLICY RISK: Restricted words found → {', '.join(found_restricted)}")
        reports.append("🚫 These can cause listing suppression or account suspension!")
    else:
        score += 10; reports.append("✅ No restricted/policy-violating words found")

    found_signals = [w for w in HIGH_VALUE_SIGNALS if w in full_text]
    if found_signals:
        reports.append(f"✅ Trust signals detected: {', '.join(found_signals)}")
    else:
        reports.append("💡 Add trust signals: 'certified', 'warranty', 'BPA-free', etc.")

    section_scores["Compliance"] = score - prev

    # ── 6. CATEGORY OPTIMIZATION (5 pts) ─────────
    reports.append("─── 📌 CATEGORY OPTIMIZATION ───")
    prev = score
    max_score += 5
    cat_keywords = {
        "Electronics": ["compatible", "wireless", "battery", "voltage", "watt"],
        "Kitchen": ["dishwasher safe", "bpa-free", "food grade", "oven safe"],
        "Fitness": ["resistance", "reps", "workout", "gym", "portable"],
        "Beauty": ["dermatologist", "cruelty-free", "paraben-free", "spf"],
        "General": []
    }
    cat_kws = cat_keywords.get(category, [])
    if cat_kws:
        found_cat = [k for k in cat_kws if k in full_text]
        if len(found_cat) >= 2:
            score += 5; reports.append(f"✅ Category keywords found: {', '.join(found_cat)}")
        else:
            reports.append(f"⚠️ Add category-specific terms: {', '.join(cat_kws)}")
    else:
        score += 3; reports.append("⚠️ Select a specific category for deeper analysis")

    section_scores["Category"] = score - prev

    # ── 7. PRICE SIGNAL (5 pts) ───────────────────
    reports.append("─── 📌 PRICE SIGNAL ───")
    prev = score
    max_score += 5
    if price > 0:
        if 9.99 <= price <= 49.99:
            score += 5; reports.append(f"✅ Price ${price:.2f} — Impulse buy range, high conversion potential")
        elif price < 9.99:
            score += 3; reports.append(f"⚠️ Price ${price:.2f} — Very low, may signal low quality")
        else:
            score += 3; reports.append(f"⚠️ Price ${price:.2f} — Premium range, ensure listing justifies value")
    else:
        reports.append("💡 Enter price for price signal analysis")

    section_scores["Price"] = score - prev

    # ── FINAL SCORE ───────────────────────────────
    final = min(max(score, 0), 100)

    reports.append("─── 📊 SCORE BREAKDOWN ───")
    for k, v in section_scores.items():
        bar = "█" * max(0, v) + "░" * max(0, 10 - v)
        reports.append(f"  {k}: {max(v,0)} pts")

    if final >= 85:
        reports.append("🏆 LISTING GRADE: A — Highly Optimized")
    elif final >= 70:
        reports.append("🥈 LISTING GRADE: B — Well Optimized")
    elif final >= 50:
        reports.append("🥉 LISTING GRADE: C — Needs Improvement")
    else:
        reports.append("❌ LISTING GRADE: D — Poorly Optimized")

    return final, reports, section_scores

# ─────────────────────────────────────────────
# STREAMLIT UI
# ─────────────────────────────────────────────
st.set_page_config(page_title="Amazon SEO Master 2026", layout="wide", page_icon="🛡️")

st.markdown("""
<style>
.big-score { font-size: 3rem; font-weight: bold; text-align: center; }
.grade-a { color: #00c851; }
.grade-b { color: #ffbb33; }
.grade-c { color: #ff8800; }
.grade-d { color: #ff4444; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ Amazon SEO Deep Audit Tool 2026")
st.caption("Helium 10-style listing analyzer — keyword intelligence, compliance, scoring & PDF export")

with st.sidebar:
    st.header("📋 Listing Data Input")
    asin_in = st.text_input("ASIN (optional)", placeholder="B0XXXXXXXX")
    category_in = st.selectbox("Category", ["General", "Electronics", "Kitchen", "Fitness", "Beauty"])
    price_in = st.number_input("Price ($)", min_value=0.0, value=0.0, step=0.01)
    title_in = st.text_area("Product Title", height=100, placeholder="Enter full product title...")
    desc_in = st.text_area("Description / A+ Content", height=150, placeholder="Full product description...")
    st.markdown("**Bullet Points (5)**")
    b_ins = [st.text_input(f"Bullet {i+1}", placeholder=f"Key feature {i+1}...") for i in range(5)]
    backend_in = st.text_area("Backend Search Terms", height=80, placeholder="space-separated keywords not in listing...")
    run_btn = st.button("🚀 RUN DEEP SEO AUDIT", use_container_width=True)

if run_btn:
    if not title_in.strip():
        st.error("Please enter a product title to audit.")
    else:
        with st.spinner("Running deep SEO analysis..."):
            final_score, feedback, section_scores = deep_audit(
                title_in, b_ins, desc_in, backend_in, category_in, price_in, asin_in
            )

        # Score display
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            grade_color = "grade-a" if final_score >= 85 else "grade-b" if final_score >= 70 else "grade-c" if final_score >= 50 else "grade-d"
            st.markdown(f'<div class="big-score {grade_color}">{final_score}/100</div>', unsafe_allow_html=True)
            st.progress(final_score / 100)

        # Section score chart
        st.subheader("📊 Score Breakdown by Section")
        chart_cols = st.columns(len(section_scores))
        for i, (section, pts) in enumerate(section_scores.items()):
            with chart_cols[i]:
                st.metric(section, f"{max(pts,0)} pts")

        # Detailed feedback
        st.subheader("🔍 Detailed Audit Report")
        for item in feedback:
            if item.startswith("───"):
                st.markdown(f"### {item}")
            elif item.startswith("✅"):
                st.success(item)
            elif item.startswith("❌"):
                st.error(item)
            elif item.startswith("⚠️"):
                st.warning(item)
            elif item.startswith("🚫"):
                st.error(item)
            elif item.startswith("💡"):
                st.info(item)
            else:
                st.write(item)

        # PDF Export
        st.divider()
        pdf_data = create_pdf(final_score, feedback, asin_in or "N/A")
        st.download_button(
            label="📥 Download Full PDF Audit Report",
            data=pdf_data,
            file_name=f"Amazon_SEO_Audit_{asin_in or 'listing'}.pdf",
            mime="application/pdf",
            use_container_width=True
        )