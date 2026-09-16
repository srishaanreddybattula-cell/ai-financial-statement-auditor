from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def test_app_home_renders_for_a_user():
    app = AppTest.from_file(ROOT / "app.py").run()

    assert app.title[0].value == "Welcome to Aurevia"
    assert app.text_input[0].placeholder == "Apple, Microsoft, NVIDIA, Tesla, ASML, Alibaba, or AAPL"
    assert app.button[0].label.startswith("Analyze")
