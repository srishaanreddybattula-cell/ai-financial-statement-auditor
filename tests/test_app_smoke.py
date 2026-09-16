from streamlit.testing.v1 import AppTest


def test_app_home_renders_for_a_user():
    app = AppTest.from_file("app.py").run()

    assert app.title[0].value == "Welcome to Aurevia"
    assert app.text_input[0].placeholder == "Apple, Microsoft, NVIDIA, Tesla, ASML, Alibaba, or AAPL"
    assert app.button[0].label.startswith("Analyze")
    assert any("Financial intelligence, grounded in SEC data" in item.value for item in app.sidebar.caption)
