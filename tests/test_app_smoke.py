from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def test_app_home_renders_for_a_user():
    app = AppTest.from_file(ROOT / "app.py").run()

    assert app.title[0].value == "Welcome to Aurevia"
    assert app.text_input[0].placeholder == "Apple, Microsoft, NVIDIA, Tesla, ASML, Alibaba, or AAPL"
    assert any(button.label.startswith("Analyze") for button in app.button)


def test_sidebar_navigation_controls_are_interactive():
    app = AppTest.from_file(ROOT / "app.py").run()

    labels = [button.label for button in app.button]
    assert "◈  Home" in labels
    assert "⌕  Company Analysis" in labels
    assert "▣  Financial Statements" in labels
    assert "◫  Key Metrics" in labels
    assert "⇄  Compare Companies" in labels
    assert "♧  Saved Reports" in labels

    company_button = next(button for button in app.button if button.label == "⌕  Company Analysis")
    company_button.click().run()

    assert "Company Analysis" in app.caption[0].value or any(
        "Company Analysis" in text.value for text in app.text if hasattr(text, "value")
    )
