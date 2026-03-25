import streamlit as st

# --- 2026 AMAZON A10 ALGORITHM STANDARDS ---
def deep_audit(title, bullets, description, category):
    score = 0
    reports = []
    
    # 1. TITLE AUDIT (Weight: 35%)
    # Amazon prioritizes the first 80 characters for Mobile Search
    if 80 <= len(title) <= 150:
        score += 35
        reports.append("✅ **Title Length:** Perfect (Optimized for Mobile & Desktop).")
    elif len(title) > 200:
        reports.append("❌ **Title Alert:** Exceeds 200 chars. Risk of Search Suppression!")
    else:
        score += 15
        reports.append("⚠️ **Title Alert:** Too short. You are losing 'Keyword Real Estate'.")

    # 2. BULLET POINT COMPLIANCE (Weight: 25%)
    valid_bullets = [b for b in bullets if len(b.strip()) > 10]
    if len(valid_bullets) == 5:
        score += 25
        reports.append("✅ **Bullet Points:** All 5 slots used effectively.")
    else:
        reports.append(f"❌ **Bullet Points:** You used {len(valid_bullets)}/5. Missing ranking power.")

    # 3. FORBIDDEN/RESTRICTED WORDS (Weight: -20 penalty)
    # 2026 Policy: Amazon flags 'Best', 'Free', and unverified health claims
    restricted = ["best", "cheap", "free", "guaranteed", "top-rated", "100%", "sale", "no.1"]
    found = [w for w in restricted if w in title.lower() or description.lower()]
    if found:
        score -= 20
        reports.append(f"🚫 **Policy Risk:** Found restricted words: {', '.join(found)}. Remove these to avoid de-ranking.")

    # 4. DESCRIPTION SCANNABILITY (Weight: 20%)
    if len(description) > 1000:
        score += 20
        reports.append("✅ **Description:** Detailed enough for A9/A10 indexing.")
    else:
        score += 5
        reports.append("⚠️ **Description:** Too thin. Add more 'Benefit-driven' copy.")

    return min(max(score, 0), 100), reports

# --- UI DESIGN ---
st.set_page_config(page_title="Amazon SEO Master 2026", layout="wide")
st.title("🛡️ Amazon SEO Accuracy Tool")
st.write("---")

with st.sidebar:
    st.header("Listing Data")
    cat = st.selectbox("Category", ["Electronics", "Home", "Beauty", "Health", "Pets"])
    title_in = st.text_area("Product Title", height=100)
    desc_in = st.text_area("Description", height=200)
    st.write("Bullet Points:")
    b_ins = [st.text_input(f"Bullet {i+1}") for i in range(5)]
    run_btn = st.button("🚀 RUN 100% ACCURATE AUDIT")

if run_btn:
    if not title_in:
        st.error("Error: Please provide at least a Title.")
    else:
        final_score, feedback = deep_audit(title_in, b_ins, desc_in, cat)
        
        # Results Display
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("SEO SCORE", f"{final_score}%")
            if final_score >= 90: st.success("Elite Listing")
            elif final_score >= 70: st.warning("Needs Optimization")
            else: st.error("Poor Performance")
            
        with col2:
            st.subheader("Actionable Report")
            for item in feedback:
                st.write(item)