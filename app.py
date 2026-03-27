import streamlit as st
import re
from fpdf import FPDF
from io import BytesIO
import html

# Page configuration
st.set_page_config(
    page_title="Amazon SEO Master 2026",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS for dark theme and styling
st.markdown("""
<style>
    .stApp {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }

    .big-score {
        font-size: 72px;
        font-weight: bold;
        text-align: center;
        margin: 20px 0;
    }

    .grade-a { color: #00c851; }
    .grade-b { color: #ffbb33; }
    .grade-c { color: #ff8800; }
    .grade-d { color: #ff4444; }

    .section-header {
        background-color: #2d2d2d;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: bold;
        margin: 15px 0 10px 0;
        border-left: 4px solid #4CAF50;
    }

    .metric-card {
        background-color: #2d2d2d;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #404040;
    }

    .stButton>button {
        background-color: #FF9900;
        color: white;
        font-weight: bold;
        font-size: 18px;
        padding: 15px;
        border-radius: 10px;
        border: none;
        width: 100%;
    }

    .stButton>button:hover {
        background-color: #FFB84D;
    }

    .download-btn {
        background-color: #4CAF50 !important;
        width: 100%;
        font-size: 16px;
        padding: 12px;
    }

    .download-btn:hover {
        background-color: #66BB6A !important;
    }

    h1, h2, h3 {
        color: #e0e0e0;
    }

    .stMetric {
        background-color: #2d2d2d;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #404040;
    }

    .stMetric > label {
        color: #b0b0b0 !important;
        font-size: 14px;
    }

    .stMetric > div[data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: bold;
    }

    .stProgress > div > div {
        background-color: #FF9900;
    }

    .tab-content {
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'audit_results' not in st.session_state:
    st.session_state.audit_results = None
if 'pdf_buffer' not in st.session_state:
    st.session_state.pdf_buffer = None

# Power words list
POWER_WORDS = ['durable', 'lightweight', 'portable', 'adjustable', 'waterproof', 'rechargeable',
              'ergonomic', 'compact', 'heavy duty', 'multi-purpose', 'premium', 'professional']

# Restricted words
RESTRICTED_WORDS = ['best', 'cheap', 'free', 'guaranteed', 'cure', 'treat', 'prevent',
                    '#1', 'number one', 'top rated', 'amazing', 'incredible', 'miracle']

# Trust signals
TRUST_SIGNALS = ['premium', 'professional', 'certified', 'patented', 'fda', 'bpa-free',
                 'eco-friendly', 'organic', 'lifetime warranty', 'money back']

# Category keywords
CATEGORY_KEYWORDS = {
    'Electronics': ['compatible', 'wireless', 'battery', 'voltage', 'watt', 'usb', 'bluetooth'],
    'Kitchen': ['dishwasher safe', 'bpa-free', 'food grade', 'oven safe', 'non-stick'],
    'Fitness': ['resistance', 'reps', 'workout', 'gym', 'portable', 'adjustable weight'],
    'Beauty': ['dermatologist', 'cruelty-free', 'paraben-free', 'spf', 'hypoallergenic']
}

# Stopwords for keyword extraction
STOPWORDS = {'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for',
             'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by',
             'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all',
             'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get',
             'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him',
             'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
             'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think',
             'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way',
             'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'}

def extract_keywords(text):
    """Extract top 15 keywords from text, excluding stopwords"""
    if not text:
        return {}

    # Convert to lowercase and find all words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    # Remove stopwords and count
    keyword_counts = {}
    for word in words:
        if word not in STOPWORDS:
            keyword_counts[word] = keyword_counts.get(word, 0) + 1

    # Return top 15
    sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_keywords[:15])

def calculate_readability(text):
    """Calculate readability score based on average words per sentence"""
    if not text:
        return "N/A", 0

    # Split into sentences (simple approach)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 0]

    if not sentences:
        return "N/A", 0

    # Count words
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    avg_words_per_sentence = len(words) / len(sentences)

    if avg_words_per_sentence <= 15:
        return "Easy", avg_words_per_sentence
    elif avg_words_per_sentence <= 25:
        return "Moderate", avg_words_per_sentence
    else:
        return "Hard", avg_words_per_sentence

def run_audit(data):
    """Run the complete SEO audit"""
    scores = {
        'title': 0,
        'bullets': 0,
        'description': 0,
        'keywords': 0,
        'compliance': 0,
        'category': 0,
        'price': 0,
        'aplus': 0,
        'total': 0
    }

    feedback = {
        'title': [],
        'bullets': [],
        'description': [],
        'keywords': [],
        'compliance': [],
        'category': [],
        'price': [],
        'aplus': []
    }

    # 1. Title Analysis (25 pts)
    title = data.get('title', '')
    title_len = len(title)

    if 150 <= title_len <= 200:
        scores['title'] += 10
        feedback['title'].append(('success', '✓ Title length optimal (150-200 characters)'))
    elif 100 <= title_len < 150:
        scores['title'] += 7
        feedback['title'].append(('warning', '⚠ Title length acceptable (100-150 chars) but could be longer'))
    elif title_len > 200:
        scores['title'] += 4
        feedback['title'].append(('warning', '⚠ Title exceeds 200 characters - may get truncated'))
    else:
        scores['title'] += 2
        feedback['title'].append(('error', '❌ Title too short (under 100 chars)'))

    if title and title[0].isupper():
        scores['title'] += 3
        feedback['title'].append(('success', '✓ Title starts with capital letter'))
    else:
        feedback['title'].append(('warning', '⚠ Title should start with capital letter'))

    if re.search(r'\d+', title):
        scores['title'] += 4
        feedback['title'].append(('success', '✓ Contains numbers (good for specificity)'))
    else:
        feedback['title'].append(('info', '💡 Consider adding relevant numbers (size, quantity, year)'))

    if '|' in title or '-' in title:
        scores['title'] += 3
        feedback['title'].append(('success', '✓ Uses separators (| or -) for readability'))
    else:
        feedback['title'].append(('info', '💡 Consider using separators (| or -) to improve readability'))

    target_keyword = data.get('target_keyword', '').lower()
    if target_keyword and target_keyword in title.lower():
        scores['title'] += 5
        feedback['title'].append(('success', f'✓ Primary keyword "{target_keyword}" found in title'))
    else:
        feedback['title'].append(('error', f'❌ Primary keyword "{target_keyword}" NOT found in title'))

    # 2. Bullet Points (20 pts)
    bullets = [data.get(f'bullet{i+1}', '') for i in range(5)]
    filled_bullets = sum(1 for b in bullets if b and len(b.strip()) > 10)
    long_bullets = sum(1 for b in bullets if b and len(b.strip()) >= 150)

    if filled_bullets == 5:
        scores['bullets'] += 8
        feedback['bullets'].append(('success', '✓ All 5 bullet points filled'))
    elif 3 <= filled_bullets <= 4:
        scores['bullets'] += 4
        feedback['bullets'].append(('warning', '⚠ Only {filled_bullets}/5 bullet points filled'))
    else:
        scores['bullets'] += 0
        feedback['bullets'].append(('error', f'❌ Only {filled_bullets}/5 bullet points filled'))

    capital_bullets = sum(1 for b in bullets if b and b[0].isupper())
    if capital_bullets == 5:
        scores['bullets'] += 3
        feedback['bullets'].append(('success', '✓ All bullets start with capital letter'))
    elif capital_bullets > 0:
        feedback['bullets'].append(('warning', f'⚠ Only {capital_bullets}/5 bullets start with capital'))
    else:
        feedback['bullets'].append(('warning', '⚠ Bullets should start with capital letters'))

    if long_bullets >= 3:
        scores['bullets'] += 5
        feedback['bullets'].append(('success', f'✓ {long_bullets} bullets are 150+ characters'))
    else:
        feedback['bullets'].append(('info', f'💡 {5-long_bullets} more bullet could be expanded to 150+ chars'))

    bullet_text = ' '.join(bullets).lower()
    power_count = sum(1 for pw in POWER_WORDS if pw in bullet_text)
    if power_count >= 3:
        scores['bullets'] += 4
        feedback['bullets'].append(('success', f'✓ Contains {power_count} power words'))
    else:
        feedback['bullets'].append(('info', f'💡 Add more power words (only {power_count} found)'))

    # 3. Description (15 pts)
    description = data.get('description', '')
    desc_len = len(description)

    if desc_len >= 1500:
        scores['description'] += 8
        feedback['description'].append(('success', '✓ Description length excellent (1500+ chars)'))
    elif desc_len >= 1000:
        scores['description'] += 5
        feedback['description'].append(('success', '✓ Description length good (1000+ chars)'))
    elif desc_len >= 500:
        scores['description'] += 3
        feedback['description'].append(('warning', '⚠ Description could be longer (500-1000 chars)'))
    else:
        scores['description'] += 0
        feedback['description'].append(('error', '❌ Description too short (under 500 chars)'))

    if target_keyword and target_keyword in description.lower():
        scores['description'] += 4
        feedback['description'].append(('success', f'✓ Primary keyword found in description'))
    else:
        feedback['description'].append(('warning', f'⚠ Primary keyword not found in description'))

    has_html = bool(re.search(r'<[^>]+>', description))
    if has_html:
        scores['description'] += 3
        feedback['description'].append(('success', '✓ HTML formatting detected (A+ Content)'))
    else:
        feedback['description'].append(('info', '💡 Consider using A+ Content with HTML formatting'))

    readability, avg_words = calculate_readability(description)
    if desc_len > 0:
        feedback['description'].append(('info', f'🔍 Readability: {readability} (avg {avg_words:.1f} words/sentence)'))
        word_count = len(re.findall(r'\b[a-zA-Z]+\b', description))
        feedback['description'].append(('info', f'📊 Word count: {word_count} words'))

    # 4. Keyword Intelligence (20 pts)
    all_text = f"{title} {description} {' '.join(bullets)}"
    all_keywords = extract_keywords(all_text)
    backend_keywords = extract_keywords(data.get('backend_keywords', ''))

    if len(all_keywords) >= 15:
        scores['keywords'] += 5
        feedback['keywords'].append(('success', '✓ 15+ unique keywords extracted from listing'))
    elif len(all_keywords) >= 8:
        scores['keywords'] += 3
        feedback['keywords'].append(('warning', f'⚠ Only {len(all_keywords)} unique keywords found'))
    else:
        scores['keywords'] += 1
        feedback['keywords'].append(('error', f'❌ Only {len(all_keywords)} unique keywords found'))

    total_words = len(re.findall(r'\b[a-zA-Z]+\b', all_text))
    target_count = all_text.lower().count(target_keyword.lower()) if target_keyword else 0
    density = (target_count / total_words * 100) if total_words > 0 else 0

    if density == 0:
        feedback['keywords'].append(('warning', f'⚠ Target keyword density: {density:.2f}% (keyword not found)'))
    elif 1 <= density <= 4:
        scores['keywords'] += 5
        feedback['keywords'].append(('success', f'✓ Target keyword density optimal: {density:.2f}%'))
    elif density > 4:
        scores['keywords'] += 0
        feedback['keywords'].append(('error', f'🚫 Keyword stuffing detected: {density:.2f}% (reduce usage)'))
    else:
        feedback['keywords'].append(('warning', f'⚠ Target keyword density low: {density:.2f}% (increase usage)'))

    backend_word_count = len(backend_keywords)
    if backend_word_count >= 200:
        scores['keywords'] += 8
        feedback['keywords'].append(('success', f'✓ Backend keywords: {backend_word_count} words (full capacity)'))
    elif backend_word_count >= 100:
        scores['keywords'] += 5
        feedback['keywords'].append(('warning', f'⚠ Backend keywords: {backend_word_count} words (underutilized)'))
    else:
        scores['keywords'] += 2
        feedback['keywords'].append(('error', f'❌ Backend keywords: only {backend_word_count} words'))

    # Check for duplicate backend keywords
    backend_text = data.get('backend_keywords', '').lower()
    backend_list = [k.strip() for k in backend_text.split(',') if k.strip()]
    if len(backend_list) == len(set(backend_list)):
        scores['keywords'] += 4
        feedback['keywords'].append(('success', '✓ No duplicate backend keywords'))
    else:
        feedback['keywords'].append(('error', '❌ Duplicate keywords found in backend search terms'))

    # Check no overlap between backend and title
    backend_set = set(backend_list)
    title_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', title.lower()))
    overlap = backend_set.intersection(title_words)
    if len(overlap) == 0:
        scores['keywords'] += 3
        feedback['keywords'].append(('success', '✓ No overlap between backend and title keywords'))
    else:
        feedback['keywords'].append(('warning', f'⚠ {len(overlap)} keywords appear in both title and backend'))

    # 5. Policy & Compliance (10 pts)
    compliance_score = 0
    text_lower = all_text.lower()
    violations = []

    for word in RESTRICTED_WORDS:
        if word.lower() in text_lower:
            violations.append(word)

    if violations:
        feedback['compliance'].append(('error', f'🚫 Restricted words found: {", ".join(violations)}'))
        compliance_score -= 15
    else:
        compliance_score += 7
        feedback['compliance'].append(('success', '✓ No restricted or policy-violating words'))

    trust_count = sum(1 for ts in TRUST_SIGNALS if ts in text_lower)
    if trust_count > 0:
        compliance_score += 3
        feedback['compliance'].append(('success', f'✓ {trust_count} trust signals detected'))
    else:
        feedback['compliance'].append(('warning', '⚠ No trust signals detected'))

    scores['compliance'] = max(0, compliance_score)

    # 6. Category Optimization (5 pts)
    category = data.get('category', 'General')
    cat_keywords = CATEGORY_KEYWORDS.get(category, [])

    if category == 'General':
        scores['category'] = 5
        feedback['category'].append(('success', '✓ General category - all keywords acceptable'))
    else:
        found_count = sum(1 for kw in cat_keywords if kw.lower() in all_text.lower())
        if found_count >= 3:
            scores['category'] = 5
            feedback['category'].append(('success', f'✓ {found_count} category-specific keywords found'))
        elif found_count >= 1:
            scores['category'] = 2
            feedback['category'].append(('warning', f'⚠ Only {found_count} category keywords (need 3+)'))
        else:
            scores['category'] = 0
            feedback['category'].append(('error', f'❌ No {category} keywords found'))

    # 7. Price Signal (5 pts)
    price = data.get('price', 0)
    if 9.99 <= price <= 49.99:
        scores['price'] = 5
        feedback['price'].append(('success', '✓ Price in impulse buy range ($9.99-$49.99)'))
    elif price < 9.99:
        scores['price'] = 3
        feedback['price'].append(('warning', '⚠ Price under $9.99 may signal low quality'))
    elif price == 49.99:
        scores['price'] = 3
        feedback['price'].append(('warning', '⚠ Premium price - ensure value proposition is clear'))
    else:
        scores['price'] = 2
        feedback['price'].append(('warning', '⚠ Price over $50 may need stronger value messaging'))

    # 8. A+ Content & Image Signals (5 pts)
    aplus_score = 0
    if has_html:
        aplus_score += 3
        feedback['aplus'].append(('success', '✓ HTML formatting detected (A+ Content)'))
    else:
        feedback['aplus'].append(('info', '💡 Add A+ Content with HTML formatting'))

    image_keywords = ['lifestyle', 'video', '360', 'infographic', 'zoom']
    image_count = sum(1 for ik in image_keywords if ik in all_text.lower())
    if image_count >= 2:
        aplus_score += 2
        feedback['aplus'].append(('success', f'✓ Media signals detected ({image_count} keywords)'))
    elif image_count == 1:
        feedback['aplus'].append(('warning', f'⚠ Only {image_count} media signal found'))
    else:
        feedback['aplus'].append(('info', '💡 Consider adding media keywords (lifestyle, video, etc.)'))

    scores['aplus'] = aplus_score

    # Calculate total
    scores['total'] = sum(scores[k] for k in ['title', 'bullets', 'description', 'keywords',
                                               'compliance', 'category', 'price', 'aplus'])

    # Clamp score to 0-100
    scores['total'] = max(0, min(100, scores['total']))

    # Determine grade
    if scores['total'] >= 85:
        grade = 'A'
        grade_emoji = '🏆'
        grade_color = '#00c851'
    elif scores['total'] >= 70:
        grade = 'B'
        grade_emoji = '🥈'
        grade_color = '#ffbb33'
    elif scores['total'] >= 50:
        grade = 'C'
        grade_emoji = '🥉'
        grade_color = '#ff8800'
    else:
        grade = 'D'
        grade_emoji = '❌'
        grade_color = '#ff4444'

    return {
        'scores': scores,
        'feedback': feedback,
        'grade': grade,
        'grade_emoji': grade_emoji,
        'grade_color': grade_color,
        'keyword_data': {
            'all_keywords': all_keywords,
            'backend_keywords': backend_keywords,
            'target_density': density,
            'target_in_title': target_keyword and target_keyword in title.lower(),
            'target_in_description': target_keyword and target_keyword in description.lower(),
            'target_in_bullets': target_keyword and any(target_keyword in b.lower() for b in bullets),
            'target_in_backend': target_keyword and target_keyword in backend_text.lower()
        }
    }

def create_pdf(results, data):
    """Generate PDF report"""
    pdf = FPDF()
    pdf.add_page()

    # Set colors
    primary_color = (76, 175, 80)  # Green
    dark_bg = (45, 45, 45)
    text_dark = (50, 50, 50)
    text_light = (200, 200, 200)

    # Header bar
    pdf.set_fill_color(*dark_bg)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_xy(0, 10)
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, 'AMAZON SEO AUDIT REPORT', align='C', ln=1)

    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f"ASIN: {data.get('asin', 'N/A')} | Grade: {results['grade']} | Score: {results['scores']['total']}/100", align='C', ln=1)

    pdf.ln(10)

    # Score progress bar
    score = results['scores']['total']
    bar_width = 180
    bar_height = 20
    pdf.set_fill_color(200, 200, 200)
    pdf.rect(10, pdf.get_y(), bar_width, bar_height)

    # Determine bar color based on score
    if score >= 70:
        bar_color = (76, 175, 80)  # Green
    elif score >= 50:
        bar_color = (255, 152, 0)  # Orange
    else:
        bar_color = (244, 67, 54)  # Red

    pdf.set_fill_color(*bar_color)
    fill_width = (score / 100) * bar_width
    pdf.rect(10, pdf.get_y(), fill_width, bar_height, 'F')

    pdf.set_xy(10, pdf.get_y() + bar_height)
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(bar_width, 10, f" {score}/100", align='L', ln=1)

    pdf.ln(15)
    pdf.set_text_color(*text_dark)

    # Audit results sections
    section_names = {
        'title': 'TITLE ANALYSIS',
        'bullets': 'BULLET POINTS',
        'description': 'DESCRIPTION & READABILITY',
        'keywords': 'KEYWORD INTELLIGENCE',
        'compliance': 'POLICY & COMPLIANCE',
        'category': 'CATEGORY OPTIMIZATION',
        'price': 'PRICE SIGNAL',
        'aplus': 'A+ CONTENT & IMAGE SIGNALS'
    }

    section_icons_pdf = {
        'title': '[TITLE]',
        'bullets': '[BULLETS]',
        'description': '[DESC]',
        'keywords': '[KEYWORDS]',
        'compliance': '[COMPLIANCE]',
        'category': '[CATEGORY]',
        'price': '[PRICE]',
        'aplus': '[APLUS]'
    }

    emoji_map = {
        '✅': '[PASS]',
        '❌': '[FAIL]',
        '⚠️': '[WARN]',
        '⚠': '[WARN]',
        '🚫': '[ALERT]',
        '💡': '[TIP]',
        '🔍': '[INFO]',
        '🏆': '[GRADE A]',
        '🥈': '[GRADE B]',
        '🥉': '[GRADE C]',
        '📌': '>>',
        '📊': '>>',
        '─': '-',
        '✓': '[PASS]',
        '❌': '[FAIL]',
        '⚠': '[WARN]',
        '💡': '[TIP]'
    }

    for section in ['title', 'bullets', 'description', 'keywords', 'compliance', 'category', 'price', 'aplus']:
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(*dark_bg)
        header_text = f" {section_icons_pdf[section]} {section_names[section]} "
        # Clean header text for Latin-1
        header_text = header_text.encode('latin-1', errors='ignore').decode('latin-1')
        pdf.cell(0, 10, header_text, fill=True, ln=1)

        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(*text_dark)

        for msg_type, message in results['feedback'][section]:
            # Convert emoji to text
            clean_msg = message
            for emoji, replacement in emoji_map.items():
                clean_msg = clean_msg.replace(emoji, replacement)

            # Clean for Latin-1
            clean_msg = clean_msg.encode('latin-1', errors='ignore').decode('latin-1')
            clean_msg = html.unescape(clean_msg)

            pdf.set_text_color(*text_dark)
            if msg_type == 'success':
                pdf.set_text_color(76, 175, 80)  # Green
            elif msg_type == 'error':
                pdf.set_text_color(244, 67, 54)  # Red
            elif msg_type == 'warning':
                pdf.set_text_color(255, 152, 0)  # Orange

            pdf.multi_cell(0, 6, clean_msg)
            pdf.ln(2)

        # Show score
        pdf.set_text_color(*text_dark)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, f"Section Score: {results['scores'][section]}/100", ln=1)
        pdf.ln(5)

    # Footer
    pdf.set_y(-30)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, 'Generated by Amazon SEO Master 2026 | Professional Audit Tool', align='C', ln=1)

    return pdf

# Sidebar
with st.sidebar:
    # Amazon Logo
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg"
             alt="Amazon Logo" width="120" style="filter: invert(1);">
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 📋 Product Details")

    asin = st.text_input("ASIN (Optional)", placeholder="e.g., B08XYZ1234", help="Amazon Standard Identification Number")

    category = st.selectbox(
        "Category",
        ["General", "Electronics", "Kitchen", "Fitness", "Beauty"],
        help="Select your product's main category"
    )

    price = st.number_input(
        "Price ($)",
        min_value=0.0,
        max_value=10000.0,
        value=29.99,
        step=0.01,
        format="%.2f"
    )

    st.markdown("---")
    st.markdown("### 🔍 SEO Content")

    target_keyword = st.text_input(
        "Primary Target Keyword",
        placeholder="e.g., wireless bluetooth headphones",
        help="Your main keyword phrase"
    )

    title = st.text_area(
        "Product Title",
        height=80,
        placeholder="Enter your full product title (aim for 150-200 chars)...",
        help="Your Amazon product listing title"
    )

    description = st.text_area(
        "Description / A+ Content",
        height=150,
        placeholder="Enter your product description with A+ HTML content...",
        help="Product description with any HTML formatting from A+ Content"
    )

    st.markdown("#### Bullet Points")

    bullet1 = st.text_input("Bullet 1", placeholder="First key feature...")
    bullet2 = st.text_input("Bullet 2", placeholder="Second key feature...")
    bullet3 = st.text_input("Bullet 3", placeholder="Third key feature...")
    bullet4 = st.text_input("Bullet 4", placeholder="Fourth key feature...")
    bullet5 = st.text_input("Bullet 5", placeholder="Fifth key feature...")

    backend_keywords = st.text_area(
        "Backend Search Terms",
        height=100,
        placeholder="Comma-separated keywords (250 characters max)...",
        help="Backend keywords separated by commas"
    )

    st.markdown("---")

    run_audit_btn = st.button("🔍 RUN DEEP SEO AUDIT", type="primary", use_container_width=True)

# Main content area
st.title("🛡️ Amazon SEO Master 2026")
st.markdown("Professional Deep Audit Tool for Amazon Product Listings")

# Welcome screen / metrics
if st.session_state.audit_results is None:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Checks Performed", "30+", delta="Comprehensive")
    with col2:
        st.metric("Scoring Sections", "8", delta="Weighted")
    with col3:
        st.metric("Max Score", "100", delta="Point-based")
    with col4:
        st.metric("PDF Export", "✅", delta="Professional")

    st.markdown("---")
    st.markdown("### 💡 How to Use")
    st.markdown("""
    1. Fill in your product details in the left sidebar
    2. Enter your full product content (title, description, bullets, backend keywords)
    3. Click **RUN DEEP SEO AUDIT** to analyze your listing
    4. Review scores, feedback, and keyword insights
    5. Download a professional PDF report
    """)

    st.markdown("---")
    st.info("⚠️ **Important**: All fields should be filled for the most accurate audit results.")

elif run_audit_btn or st.session_state.get('just_ran_audit', False):
    # Gather data
    data = {
        'asin': asin,
        'category': category,
        'price': price,
        'target_keyword': target_keyword,
        'title': title,
        'description': description,
        'bullet1': bullet1,
        'bullet2': bullet2,
        'bullet3': bullet3,
        'bullet4': bullet4,
        'bullet5': bullet5,
        'backend_keywords': backend_keywords
    }

    # Run audit
    with st.spinner("Analyzing your listing..."):
        results = run_audit(data)
        st.session_state.audit_results = results

    # Generate PDF
    with st.spinner("Generating PDF report..."):
        pdf = create_pdf(results, data)
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        buffer = BytesIO(pdf_bytes)
        st.session_state.pdf_buffer = buffer

    st.session_state.just_ran_audit = False
    st.rerun()

# Display results if available
if st.session_state.audit_results:
    results = st.session_state.audit_results

    # Score Banner
    st.markdown("---")
    st.markdown(f"""
    <div style="background-color: #2d2d2d; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 30px;">
        <div class="big-score grade-{results['grade'].lower()}">{results['grade_emoji']} {results['scores']['total']}/100</div>
        <div style="font-size: 48px; font-weight: bold; margin: 10px 0;" class="grade-{results['grade'].lower()}">Grade {results['grade']}</div>
        <div style="margin-top: 20px;">
            <progress value="{results['scores']['total']}" max="100" style="width: 100%; height: 20px; border-radius: 10px;"></progress>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Section Score Cards
    st.markdown("### 📊 Section Scores")
    col1, col2, col3, col4 = st.columns(4)

    section_labels = {
        'title': 'Title',
        'bullets': 'Bullets',
        'description': 'Description',
        'keywords': 'Keywords',
        'compliance': 'Compliance',
        'category': 'Category',
        'price': 'Price',
        'aplus': 'A+ Content'
    }

    for idx, (section, score) in enumerate(results['scores'].items()):
        if section != 'total':
            col_idx = idx % 4
            with [col1, col2, col3, col4][col_idx]:
                if score >= 15:
                    delta_color = "normal"
                elif score >= 8:
                    delta_color = "off"
                else:
                    delta_color = "inverse"

                st.metric(
                    label=section_labels[section],
                    value=f"{score}/100",
                    delta="Good" if score >= 15 else "Needs Work",
                    delta_color=delta_color
                )

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Full Audit Report", "🔍 Keyword Insights", "⚡ Quick Fixes"])

    with tab1:
        st.markdown("### Detailed Analysis by Section")
        for section in ['title', 'bullets', 'description', 'keywords', 'compliance', 'category', 'price', 'aplus']:
            st.markdown(f"#### {section_labels[section]}")

            # Display feedback
            for msg_type, message in results['feedback'][section]:
                if msg_type == 'success':
                    st.success(message)
                elif msg_type == 'error':
                    st.error(message)
                elif msg_type == 'warning':
                    st.warning(message)
                else:
                    st.info(message)

            st.markdown("---")

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Top 15 Keywords")
            kw_data = results['keyword_data']['all_keywords']
            if kw_data:
                kw_items = list(kw_data.items())
                for i in range(0, len(kw_items), 3):
                    cols = st.columns(3)
                    for j in range(3):
                        if i + j < len(kw_items):
                            word, count = kw_items[i + j]
                            with cols[j]:
                                st.metric(word, str(count))
            else:
                st.warning("No keywords extracted")

        with col2:
            st.markdown("#### Target Keyword Presence")
            kw_check = results['keyword_data']
            checks = [
                ('Title', kw_check['target_in_title']),
                ('Description', kw_check['target_in_description']),
                ('Bullets', kw_check['target_in_bullets']),
                ('Backend', kw_check['target_in_backend'])
            ]

            for label, present in checks:
                if present:
                    st.success(f"✅ {label}: Found")
                else:
                    st.error(f"❌ {label}: Not Found")

            st.markdown("---")
            st.metric("Keyword Density", f"{kw_check['target_density']:.2f}%")

    with tab3:
        # Collect issues by type
        critical = []
        warnings = []
        tips = []

        for section in results['feedback']:
            for msg_type, message in results['feedback'][section]:
                if msg_type == 'error':
                    critical.append(message)
                elif msg_type == 'warning':
                    warnings.append(message)
                elif msg_type == 'info':
                    tips.append(message)

        if critical:
            st.markdown("#### 🔴 Critical Issues")
            for issue in critical:
                st.error(issue)
        else:
            st.success("✅ No critical issues!")

        if warnings:
            st.markdown("#### 🟡 Warnings")
            for warning in warnings:
                st.warning(warning)
        else:
            st.success("✅ No warnings!")

        if tips:
            st.markdown("#### 🔵 Optimization Tips")
            for tip in tips:
                st.info(tip)
        else:
            st.success("✅ No additional tips!")

    # PDF Download
    st.markdown("---")
    if st.session_state.pdf_buffer:
        st.download_button(
            label="📥 Download Full PDF Audit Report",
            data=st.session_state.pdf_buffer,
            file_name=f"Amazon_SEO_Audit_{asin if asin else 'Product'}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
