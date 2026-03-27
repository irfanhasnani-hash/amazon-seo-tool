# Amazon SEO Deep Audit Tool

A professional Helium 10-style Amazon listing SEO analyzer built with Streamlit.

## Features

- **8 Scoring Sections** (100 points total)
  - Title Analysis (25 pts)
  - Bullet Points (20 pts)
  - Description (15 pts)
  - Keyword Intelligence (20 pts)
  - Policy & Compliance (10 pts)
  - Category Optimization (5 pts)
  - Price Signal (5 pts)
  - A+ Content & Image Signals (5 pts)

- **Grade System**
  - 🏆 Grade A (85-100): Excellent
  - 🥈 Grade B (70-84): Good
  - 🥉 Grade C (50-69): Fair
  - ❌ Grade D (0-49): Needs Work

- **3 Interactive Tabs**
  - Full Audit Report (color-coded feedback)
  - Keyword Insights (top 15 keywords, density analysis)
  - Quick Fixes (critical, warnings, tips)

- **Professional PDF Export**
  - Dark header bar with score progress bar
  - All audit details formatted
  - Emoji-to-text mapping for compatibility

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## How to Use

1. Fill in the product details in the left sidebar:
   - ASIN (optional)
   - Category (General, Electronics, Kitchen, Fitness, Beauty)
   - Price
   - Primary Target Keyword
   - Product Title
   - Description/A+ Content
   - 5 Bullet Points
   - Backend Search Terms

2. Click "RUN DEEP SEO AUDIT"

3. Review the results across three tabs

4. Download the professional PDF report

## Audit Criteria

### Title Analysis (25 pts)
- Character length: 150–200 = 10pts, 100–150 = 7pts, >200 = 4pts, <100 = 2pts
- Starts with capital letter = 3pts
- Contains numbers = 4pts
- Uses separators (| or -) = 3pts
- Primary target keyword present = 5pts

### Bullet Points (20 pts)
- All 5 filled (10+ chars each) = 8pts, 3-4 filled = 4pts
- All start with capital = 3pts
- 3+ bullets 150+ chars = 5pts
- 3+ power words detected = 4pts

### Description (15 pts)
- 1500+ chars = 8pts, 1000+ = 5pts, 500+ = 3pts, <500 = 0pts
- Target keyword in description = 4pts
- HTML tags detected = 3pts
- Readability score provided

### Keyword Intelligence (20 pts)
- 15+ unique keywords extracted = 5pts
- Target density 1-4% = 5pts (warning/penalty otherwise)
- Backend keywords 200+ words = 8pts, 100+ = 5pts, <100 = 2pts
- No duplicate backend keywords = 4pts
- No overlap with title keywords = 3pts

### Policy & Compliance (10 pts)
- Restricted words detected: -15pt penalty
- No violations = 7pts
- Trust signals detected = 3pts

### Category Optimization (5 pts)
- Category-specific keyword matching

### Price Signal (5 pts)
- $9.99–$49.99 = 5pts (optimal)
- <$9.99 = 3pts (quality concern)
- $49.99 = 3pts (premium)

### A+ Content & Image Signals (5 pts)
- HTML formatting = 3pts
- Media keywords detected = 2pts

## Requirements

- Python 3.8+
- streamlit
- fpdf

All logic is contained in a single `app.py` file for easy deployment.

## Notes

- All text is sanitized for PDF compatibility (Latin-1 encoding)
- Score is always clamped between 0-100
- No external APIs required - fully offline/rule-based
- Dark theme UI with professional styling
- Fully responsive layout

---

Built for professional Amazon sellers and SEO specialists.