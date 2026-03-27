"""
Simple test script for Amazon SEO Audit Tool
Run: python test_audit.py
"""

import sys
import os

# Add the directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all core functions can be imported"""
    print("Testing imports...")
    try:
        from app import run_audit, extract_keywords, calculate_readability, create_pdf
        print("  [PASS] All functions imported successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] Import error: {e}")
        return False

def test_basic_functions():
    """Test core functions without running full Streamlit"""
    print("\nTesting basic functions...")
    try:
        # Import functions from app
        from app import extract_keywords, calculate_readability

        # Test keyword extraction
        test_text = "The quick brown fox jumps over the lazy dog. This is a premium product test."
        keywords = extract_keywords(test_text)
        assert isinstance(keywords, dict)
        assert len(keywords) > 0
        print(f"  [PASS] extract_keywords returned {len(keywords)} keywords")

        # Test readability
        easy = "Short sentence. Another sentence."
        level, avg = calculate_readability(easy)
        assert level == "Easy"
        print(f"  [PASS] calculate_readability: '{easy}' -> {level}")

        return True
    except Exception as e:
        print(f"  [FAIL] Function test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_audit_logic():
    """Test the audit logic with sample data"""
    print("\nTesting audit logic...")
    try:
        from app import run_audit

        sample_data = {
            'asin': 'TEST123',
            'category': 'Electronics',
            'price': 29.99,
            'target_keyword': 'wireless headphones',
            'title': 'Wireless Bluetooth Headphones - Premium Noise Cancelling - 30hr Battery Life',
            'description': '<p>Premium wireless headphones with active noise cancellation. Experience crystal-clear audio and 30-hour battery life. Perfect for travel and daily use.</p>',
            'bullet1': 'Active Noise Cancellation blocks ambient sounds for immersive experience',
            'bullet2': '30-hour battery life with USB-C fast charging',
            'bullet3': 'Premium comfort with memory foam ear cushions',
            'bullet4': 'Hi-Res audio with 40mm drivers',
            'bullet5': 'Universal compatibility with all devices',
            'backend_keywords': 'bluetooth, wireless, headphones, noise cancelling, battery life, premium, audio, comfort, hi-res, usbc'
        }

        results = run_audit(sample_data)

        # Validate results structure
        assert 'scores' in results
        assert 'feedback' in results
        assert 'grade' in results
        assert 'grade_emoji' in results
        assert 'keyword_data' in results

        # Validate score range
        total = results['scores']['total']
        assert 0 <= total <= 100, f"Score {total} out of range [0-100]"

        # Validate grade
        assert results['grade'] in ['A', 'B', 'C', 'D']

        print(f"  [PASS] Audit completed. Total score: {total}/100, Grade: {results['grade']}")
        print(f"  [INFO] Section scores:")
        for section, score in results['scores'].items():
            if section != 'total':
                print(f"    - {section}: {score}/100")

        return True
    except Exception as e:
        print(f"  [FAIL] Audit logic error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_compliance_detection():
    """Test restricted words detection"""
    print("\nTesting compliance detection...")
    try:
        from app import run_audit

        violation_data = {
            'asin': 'VIOLATION123',
            'category': 'General',
            'price': 9.99,
            'target_keyword': 'test product',
            'title': 'BEST Product Guaranteed #1 Miracle Cure Cheap Amazing',
            'description': 'This free product is incredible and top rated.',
            'bullet1': 'Feature one',
            'bullet2': 'Feature two',
            'bullet3': '',
            'bullet4': '',
            'bullet5': '',
            'backend_keywords': ''
        }

        results = run_audit(violation_data)

        # Should detect violations and have negative compliance score
        has_violations = any('🚫' in str(msg) for msg_type, msg in results['feedback']['compliance'])
        assert has_violations, "Should detect restricted words"
        print(f"  [PASS] Restricted words detected correctly")
        print(f"  [INFO] Compliance score: {results['scores']['compliance']}")

        return True
    except Exception as e:
        print(f"  [FAIL] Compliance test error: {e}")
        return False

def test_pdf_generation():
    """Test PDF creation"""
    print("\nTesting PDF generation...")
    try:
        from app import create_pdf, run_audit

        sample_data = {
            'asin': 'PDFTEST',
            'category': 'Kitchen',
            'price': 19.99,
            'target_keyword': 'kitchen knife',
            'title': 'Test Title for PDF',
            'description': 'Test description content for PDF generation.',
            'bullet1': 'Feature one',
            'bullet2': 'Feature two',
            'bullet3': 'Feature three',
            'bullet4': 'Feature four',
            'bullet5': 'Feature five',
            'backend_keywords': 'kitchen, knife, cooking, chef, cutlery'
        }

        results = run_audit(sample_data)
        pdf = create_pdf(results, sample_data)

        assert pdf is not None
        print(f"  [PASS] PDF object created successfully")

        # Get PDF as bytes using dest='S'
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        pdf_size = len(pdf_bytes)
        print(f"  [PASS] PDF generated ({pdf_size} bytes)")

        return True
    except Exception as e:
        print(f"  [FAIL] PDF generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("Amazon SEO Audit Tool - Test Suite")
    print("=" * 60)

    tests = [
        test_imports,
        test_basic_functions,
        test_audit_logic,
        test_compliance_detection,
        test_pdf_generation
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  [FAIL] {test.__name__} crashed: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    if all(results):
        print("**ALL TESTS PASSED**")
        print("=" * 60)
        print("\nTo run the Streamlit app:")
        print("  streamlit run app.py")
        return 0
    else:
        failed = sum(1 for r in results if not r)
        print(f"**{failed} TEST(S) FAILED**")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())