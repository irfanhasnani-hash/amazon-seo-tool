import streamlit as st
from fpdf import FPDF
import re
from collections import Counter

# ─────────────────────────────────────────────
# PDF GENERATOR
# ─────────────────────────────────────────────
def create_pdf(score, report, asin="N/A", grade="N/A"):
    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_fill_color(35, 35, 60)
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(200, 15, "Amazon SEO Deep Audit Report 2026", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(200, 8, f"ASIN: {asin}  |  Grade: {grade}  |  Score: {score}/100", ln=True, align="C")

    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)

    # Score bar
    pdf.set_font("Arial", "B", 13)
    pdf.cell(200, 8, f"Overall SEO Score: {score}/100", ln=True)
    pdf.set_fill_color(220, 220, 220)
    pdf.rect(10, pdf.get_y(), 190, 6, 'F')
    pdf.set_fill_color(0, 180, 80) if score >= 70 else pdf.set_fill_color(255, 140, 0) if score >= 50 else pdf.set_fill_color(220, 50, 50)
    pdf.rect(10, pdf.get_y(), 190 * score / 100, 6, 'F')
    pdf.ln(12)

    emoji_map = {
        "✅": "[PASS]", "❌": "[FAIL]", "⚠️": "[WARN]", "🚫": "[ALERT]",
        "💡": "[TIP]", "🔍": "[INFO]", "🏆": "[GRADE A]", "🥈": "[GRADE B]",
        "🥉": "[GRADE C]", "📌": ">>", "📊": ">>", "█": "#", "░": "-",
        "**": "", "───": "---", "\u2013": "-", "\u2014": "-",
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    }

    pdf.set_font("Arial", "", 10)
    for line in report:
        clean = line
        for emoji, replacement in emoji_map.items():
            clean = clean.replace(emoji, replacement)
        clean = clean.encode("latin-1", errors="ignore").decode("latin-1")
        if clean.startswith("---"):
            pdf.set_font("Arial", "B", 11)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(190, 7, clean, ln=True, fill=True)
            pdf.set_font("Arial", "", 10)
        else:
            pdf.multi_cell(0, 7, clean)

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

POWER_WORDS = [
    "durable", "lightweight", "portable", "adjustable", "waterproof",
    "rechargeable", "ergonomic", "compact", "heavy duty", "multi-purpose"
]

def word_count(text): return len(text.split())
def char_count(text): return len(text)

def extract_keywords(text, top_n=10):
    stopwords = {
        "the","a","an","and","or","for","in","on","with","to","of","is","it",
        "this","that","are","be","as","at","by","from","our","your","you","we"
    }
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    filtered = [w for w in words if w not in stopwords]
    return Counter(filtered).most_common(top_n)

def readability_score(text):
    sentences = re.split(r'[.!?]', text)
    sentences = [s for s in sentences if len(s.strip()) > 0]
    words = text.split()
    if not sentences:
        return "N/A"
    avg_words = len(words) / len(sentences)
    if avg_words <= 15:
        return "Easy ✅"
    elif avg_words <= 25:
        return "Moderate ⚠️"
    else:
        return "Hard ❌"

def get_grade(score):
    if score >= 85: return "A", "🏆", "#00c851"
    elif score >= 70: return "B", "🥈", "#ffbb33"
    elif score >= 50: return "C", "🥉", "#ff8800"
    else: return "D", "❌", "#ff4444"

# ─────────────────────────────────────────────
# DEEP AUDIT ENGINE
# ─────────────────────────────────────────────
def deep_audit(title, bullets, description, backend_kw, category, price, asin, target_kw):
    score = 0
    reports = []
    section_scores = {}

    full_text = f"{title} {' '.join(bullets)} {description} {backend_kw}".lower()

    # ── 1. TITLE AUDIT (25 pts) ──────────────────
    reports.append("─── 📌 TITLE ANALYSIS ───")
    title_score = 0
    tlen = char_count(title)

    if 150 <= tlen <= 200:
        title_score += 10
        reports.append(f"✅ Title length: {tlen} chars — Optimal (150–200)")
    elif 100 <= tlen < 150:
        title_score += 7
        reports.append(f"⚠️ Title length: {tlen} chars — Good but could be longer")
    elif tlen > 200:
        title_score += 4
        reports.append(f"⚠️ Title length: {tlen} chars — May be truncated on mobile")
    else:
        title_score += 2
        reports.append(f"❌ Title length: {tlen} chars — Too short, add more keywords")

    if title and title[0].isupper():
        title_score += 3
        reports.append("✅ Title starts with capital letter")
    else:
        reports.append("❌ Title should start with a capital letter")

    if re.search(r'\d', title):
        title_score += 4
        reports.append("✅ Title contains numbers (size/quantity) — boosts CTR")
    else:
        reports.append("💡 Add numbers (pack size, dimensions, count) to title")

    if "|" in title or "-" in title:
        title_score += 3
        reports.append("✅ Title uses separators ( | or - ) for readability")
    else:
        reports.append("💡 Use ' | ' or ' - ' to separate key features in title")

    if target_kw and target_kw.lower() in title.lower():
        title_score += 5
        reports.append(f"✅ Primary target keyword '{target_kw}' found in title")
    elif target_kw:
        reports.append(f"❌ Primary keyword '{target_kw}' NOT in title — critical miss")

    score += title_score
    section_scores["Title"] = title_score

    # ── 2. BULLET POINTS AUDIT (20 pts) ──────────
    reports.append("─── 📌 BULLET POINTS ANALYSIS ───")
    bullet_score = 0
    valid_bullets = [b for b in bullets if len(b.strip()) > 10]

    if len(valid_bullets) == 5:
        bullet_score += 8
        reports.append("✅ All 5 bullet points used — full SEO coverage")
    elif len(valid_bullets) >= 3:
        bullet_score += 4
        reports.append(f"⚠️ {len(valid_bullets)}/5 bullets filled — add more")
    else:
        reports.append(f"❌ Only {len(valid_bullets)}/5 bullets — major SEO gap")

    caps_bullets = [b for b in valid_bullets if b.strip() and b.strip()[0].isupper()]
    if len(caps_bullets) == len(valid_bullets) and valid_bullets:
        bullet_score += 3
        reports.append("✅ All bullets start with capital letters")
    else:
        reports.append("⚠️ Some bullets don't start with capitals")

    long_bullets = [b for b in valid_bullets if len(b) >= 150]
    if len(long_bullets) >= 3:
        bullet_score += 5
        reports.append(f"✅ {len(long_bullets)} bullets are detailed (150+ chars)")
    else:
        reports.append(f"⚠️ Only {len(long_bullets)} detailed bullets — aim for 150–250 chars each")

    power_found = [w for w in POWER_WORDS if w in " ".join(bullets).lower()]
    if len(power_found) >= 3:
        bullet_score += 4
        reports.append(f"✅ Power words in bullets: {', '.join(power_found[:5])}")
    else:
        reports.append(f"💡 Add power words to bullets: waterproof, ergonomic, durable, etc.")

    score += bullet_score
    section_scores["Bullets"] = bullet_score

    # ── 3. DESCRIPTION AUDIT (15 pts) ────────────
    reports.append("─── 📌 DESCRIPTION ANALYSIS ───")
    desc_score = 0
    dlen = char_count(description)
    wcount = word_count(description)

    if dlen >= 1500:
        desc_score += 8
        reports.append(f"✅ Description: {dlen} chars — Excellent depth")
    elif dlen >= 1000:
        desc_score += 5
        reports.append(f"⚠️ Description: {dlen} chars — Good, aim for 1500+")
    elif dlen >= 500:
        desc_score += 3
        reports.append(f"⚠️ Description: {dlen} chars — Thin content")
    else:
        reports.append(f"❌ Description: {dlen} chars — Very thin, major SEO gap")

    if target_kw and target_kw.lower() in description.lower():
        desc_score += 4
        reports.append(f"✅ Target keyword '{target_kw}' found in description")
    elif target_kw:
        reports.append(f"⚠️ Target keyword '{target_kw}' missing from description")

    reports.append(f"🔍 Readability: {readability_score(description)}")
    reports.append(f"🔍 Word count: {wcount} words")

    if re.search(r'<[^>]+>', description):
        desc_score += 3
        reports.append("✅ HTML formatting detected in description — improves readability")
    else:
        reports.append("💡 Use HTML tags (<b>, <ul>, <li>) in description for better formatting")

    score += desc_score
    section_scores["Description"] = desc_score

    # ── 4. KEYWORD ANALYSIS (20 pts) ─────────────
    reports.append("─── 📌 KEYWORD INTELLIGENCE ───")
    kw_score = 0

    top_kw = extract_keywords(full_text, 10)
    reports.append(f"🔍 Top keywords detected: {', '.join([k for k, _ in top_kw])}")

    if target_kw:
        density = round(full_text.count(target_kw.lower()) / max(len(full_text.split()), 1) * 100, 2)
        if 1.0 <= density <= 4.0:
            kw_score += 5
            reports.append(f"✅ Keyword density for '{target_kw}': {density}% — Optimal")
        elif density > 4.0:
            reports.append(f"🚫 Keyword density: {density}% — Keyword stuffing risk!")
        else:
            reports.append(f"⚠️ Keyword density: {density}% — Too low, use keyword more")

    if backend_kw.strip():
        bk_count = len(backend_kw.split())
        if bk_count >= 200:
            kw_score += 8
            reports.append(f"✅ Backend keywords: {bk_count} words — Maxed out")
        elif bk_count >= 100:
            kw_score += 5
            reports.append(f"⚠️ Backend keywords: {bk_count} words — Add more (target 200+)")
        else:
            kw_score += 2
            reports.append(f"❌ Backend keywords: {bk_count} words — Very low")

        bk_list = backend_kw.lower().split()
        duplicates = [w for w, c in Counter(bk_list).items() if c > 1]
        if duplicates:
            reports.append(f"⚠️ Duplicate backend keywords: {', '.join(duplicates[:5])} — wasted space")
        else:
            kw_score += 4
            reports.append("✅ No duplicate backend keywords — efficient")

        title_words = set(re.findall(r'\b\w{4,}\b', title.lower()))
        bk_words_set = set(re.findall(r'\b\w{4,}\b', backend_kw.lower()))
        overlap = title_words & bk_words_set
        if overlap:
            reports.append(f"💡 Redundant in backend (already in title): {', '.join(list(overlap)[:5])}")
        else:
            kw_score += 3
            reports.append("✅ Backend keywords are unique — no title overlap")
    else:
        reports.append("❌ No backend keywords — major indexing gap")

    score += kw_score
    section_scores["Keywords"] = kw_score

    # ── 5. POLICY & COMPLIANCE (10 pts) ──────────
    reports.append("─── 📌 POLICY & COMPLIANCE ───")
    comp_score = 0
    found_restricted = [w for w in RESTRICTED_WORDS if w in full_text]

    if found_restricted:
        score -= 15
        comp_score -= 15
        reports.append(f"🚫 POLICY RISK: Restricted words → {', '.join(found_restricted)}")
        reports.append("🚫 Can cause listing suppression or account suspension!")
    else:
        comp_score += 7
        reports.append("✅ No restricted/policy-violating words found")

    found_signals = [w for w in HIGH_VALUE_SIGNALS if w in full_text]
    if found_signals:
        comp_score += 3
        reports.append(f"✅ Trust signals: {', '.join(found_signals)}")
    else:
        reports.append("💡 Add trust signals: certified, warranty, BPA-free, etc.")

    score += comp_score
    section_scores["Compliance"] = comp_score

    # ── 6. CATEGORY OPTIMIZATION (5 pts) ─────────
    reports.append("─── 📌 CATEGORY OPTIMIZATION ───")
    cat_score = 0
    cat_keywords = {
        "Electronics": ["compatible", "wireless", "battery", "voltage", "watt", "usb", "bluetooth"],
        "Kitchen": ["dishwasher safe", "bpa-free", "food grade", "oven safe", "non-stick"],
        "Fitness": ["resistance", "reps", "workout", "gym", "portable", "adjustable weight"],
        "Beauty": ["dermatologist", "cruelty-free", "paraben-free", "spf", "hypoallergenic"],
        "General": []
    }
    cat_kws = cat_keywords.get(category, [])
    if cat_kws:
        found_cat = [k for k in cat_kws if k in full_text]
        if len(found_cat) >= 3:
            cat_score += 5
            reports.append(f"✅ Strong category keywords: {', '.join(found_cat)}")
        elif len(found_cat) >= 1:
            cat_score += 2
            reports.append(f"⚠️ Some category keywords found: {', '.join(found_cat)} — add more")
        else:
            reports.append(f"❌ No category keywords — add: {', '.join(cat_kws[:4])}")
    else:
        cat_score += 2
        reports.append("⚠️ Select a specific category for deeper analysis")

    score += cat_score
    section_scores["Category"] = cat_score

    # ── 7. PRICE SIGNAL (5 pts) ───────────────────
    reports.append("─── 📌 PRICE SIGNAL ───")
    price_score = 0
    if price > 0:
        if 9.99 <= price <= 49.99:
            price_score += 5
            reports.append(f"✅ Price ${price:.2f} — Impulse buy range, high conversion")
        elif price < 9.99:
            price_score += 3
            reports.append(f"⚠️ Price ${price:.2f} — Very low, may signal low quality")
        else:
            price_score += 3
            reports.append(f"⚠️ Price ${price:.2f} — Premium range, justify value in listing")
    else:
        reports.append("💡 Enter price for price signal analysis")

    score += price_score
    section_scores["Price"] = price_score

    # ── 8. IMAGE & A+ SIGNALS (5 pts) ────────────
    reports.append("─── 📌 A+ CONTENT & IMAGE SIGNALS ───")
    aplus_score = 0
    if re.search(r'<[^>]+>', description):
        aplus_score += 3
        reports.append("✅ HTML/A+ content formatting detected")
    else:
        reports.append("💡 Use A+ Content or HTML formatting for richer description")

    if any(w in full_text for w in ["lifestyle", "infographic", "360", "zoom", "video"]):
        aplus_score += 2
        reports.append("✅ Rich media signals detected (lifestyle/video/360)")
    else:
        reports.append("💡 Mention lifestyle images, 360 view, or video in listing")

    score += aplus_score
    section_scores["A+ Content"] = aplus_score

    # ── FINAL ─────────────────────────────────────
    final = min(max(score, 0), 100)
    grade_letter, grade_icon, _ = get_grade(final)

    reports.append("─── 📊 SCORE BREAKDOWN ───")
    for k, v in section_scores.items():
        reports.append(f"  {k}: {max(v, 0)} pts")

    reports.append(f"{grade_icon} LISTING GRADE: {grade_letter} — Score {final}/100")

    return final, reports, section_scores

# ─────────────────────────────────────────────
# STREAMLIT UI
# ─────────────────────────────────────────────
st.set_page_config(page_title="Amazon SEO Master 2026", layout="wide", page_icon="🛡️")

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .big-score { font-size: 3.5rem; font-weight: 900; text-align: center; padding: 10px; }
    .grade-a { color: #00c851; }
    .grade-b { color: #ffbb33; }
    .grade-c { color: #ff8800; }
    .grade-d { color: #ff4444; }
    .section-header { font-size: 1.1rem; font-weight: bold; background: #1e2130;
                      padding: 8px 12px; border-radius: 6px; margin: 10px 0 4px 0; }
    div[data-testid="stMetricValue"] { font-size: 1.4rem !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ Amazon SEO Deep Audit Tool 2026")
st.caption("Helium 10-style analyzer — keyword intelligence, compliance, A+ signals, scoring & PDF export")

# ── SIDEBAR ───────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", width=120)
    st.header("📋 Listing Input")
    asin_in = st.text_input("ASIN (optional)", placeholder="B0XXXXXXXX")
    category_in = st.selectbox("Category", ["General", "Electronics", "Kitchen", "Fitness", "Beauty"])
    price_in = st.number_input("Price ($)", min_value=0.0, value=0.0, step=0.01)
    target_kw_in = st.text_input("🎯 Primary Target Keyword", placeholder="e.g. wireless earbuds")
    title_in = st.text_area("Product Title", height=100, placeholder="Enter full product title...")
    desc_in = st.text_area("Description / A+ Content", height=150, placeholder="Full product description...")
    st.markdown("**Bullet Points (5)**")
    b_ins = [st.text_input(f"Bullet {i+1}", placeholder=f"Key feature {i+1}...") for i in range(5)]
    backend_in = st.text_area("Backend Search Terms", height=80, placeholder="space-separated keywords...")
    st.divider()
    run_btn = st.button("🚀 RUN DEEP SEO AUDIT", use_container_width=True, type="primary")

# ── MAIN PANEL ────────────────────────────────
if not run_btn:
    st.info("👈 Fill in your listing details in the sidebar and click **RUN DEEP SEO AUDIT**")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Checks Performed", "30+")
    col2.metric("Scoring Sections", "8")
    col3.metric("Max Score", "100")
    col4.metric("PDF Export", "✅ Yes")

if run_btn:
    if not title_in.strip():
        st.error("⚠️ Please enter a product title to audit.")
    else:
        with st.spinner("🔍 Running deep SEO analysis..."):
            final_score, feedback, section_scores = deep_audit(
                title_in, b_ins, desc_in, backend_in,
                category_in, price_in, asin_in, target_kw_in
            )

        grade_letter, grade_icon, grade_color = get_grade(final_score)
        grade_class = f"grade-{grade_letter.lower()}"

        # ── TOP SCORE BANNER ──────────────────────
        st.divider()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                f'<div class="big-score {grade_class}">{grade_icon} {final_score}/100</div>',
                unsafe_allow_html=True
            )
            st.progress(final_score / 100)
            st.markdown(
                f'<div style="text-align:center; font-size:1.2rem; color:{grade_color};">'
                f'Grade: <b>{grade_letter}</b></div>',
                unsafe_allow_html=True
            )

        st.divider()

        # ── SECTION SCORE METRICS ─────────────────
        st.subheader("📊 Score Breakdown by Section")
        cols = st.columns(len(section_scores))
        for i, (section, pts) in enumerate(section_scores.items()):
            with cols[i]:
                delta_color = "normal" if pts >= 3 else "inverse"
                st.metric(section, f"{max(pts, 0)} pts", delta=None)

        st.divider()

        # ── TABS FOR REPORT ───────────────────────
        tab1, tab2, tab3 = st.tabs(["📋 Full Audit Report", "🔑 Keyword Insights", "💡 Quick Fixes"])

        with tab1:
            for item in feedback:
                if item.startswith("───"):
                    st.markdown(f"<div class='section-header'>{item}</div>", unsafe_allow_html=True)
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

        with tab2:
            st.subheader("🔑 Top Keywords in Your Listing")
            full_text = f"{title_in} {' '.join(b_ins)} {desc_in} {backend_in}".lower()
            top_kw = extract_keywords(full_text, 15)
            if top_kw:
                kw_cols = st.columns(3)
                for i, (kw, count) in enumerate(top_kw):
                    with kw_cols[i % 3]:
                        st.metric(kw, f"{count}x")
            else:
                st.info("No keywords detected — add more content to your listing.")

            if target_kw_in:
                st.subheader(f"🎯 Target Keyword: '{target_kw_in}'")
                in_title = "✅ Yes" if target_kw_in.lower() in title_in.lower() else "❌ No"
                in_desc = "✅ Yes" if target_kw_in.lower() in desc_in.lower() else "❌ No"
                in_bullets = "✅ Yes" if any(target_kw_in.lower() in b.lower() for b in b_ins) else "❌ No"
                in_backend = "✅ Yes" if target_kw_in.lower() in backend_in.lower() else "❌ No"
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("In Title", in_title)
                c2.metric("In Description", in_desc)
                c3.metric("In Bullets", in_bullets)
                c4.metric("In Backend", in_backend)

        with tab3:
            st.subheader("💡 Priority Fixes to Boost Your Score")
            fixes = [item for item in feedback if item.startswith("❌") or item.startswith("🚫")]
            warnings = [item for item in feedback if item.startswith("⚠️")]
            tips = [item for item in feedback if item.startswith("💡")]

            if fixes:
                st.markdown("### 🔴 Critical Issues")
                for f in fixes:
                    st.error(f)
            if warnings:
                st.markdown("### 🟡 Warnings")
                for w in warnings:
                    st.warning(w)
            if tips:
                st.markdown("### 🔵 Optimization Tips")
                for t in tips:
                    st.info(t)
            if not fixes and not warnings:
                st.success("🎉 No critical issues found! Your listing is well optimized.")

        # ── PDF EXPORT ────────────────────────────
        st.divider()
        pdf_data = create_pdf(final_score, feedback, asin_in or "N/A", grade_letter)
        st.download_button(
            label="📥 Download Full PDF Audit Report",
            data=pdf_data,
            file_name=f"Amazon_SEO_Audit_{asin_in or 'listing'}.pdf",
            mime="application/pdf",
            use_container_width=True
        )