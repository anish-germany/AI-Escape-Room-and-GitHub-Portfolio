from streamlit.testing.v1 import AppTest


def test_v2_ui_complete_and_restart():
    app = AppTest.from_file("../app.py").run()
    assert not app.exception
    for action in ["examine desk", "take key", "examine bookshelf", "open drawer with 314", "take card", "examine painting", "use key on painting", "unlock door with 7259"]:
        app.chat_input[0].set_value(action).run()
        assert not app.exception
    assert app.success[0].value.startswith("You escaped")
    assert app.chat_input[0].disabled
    app.button[0].click().run()
    assert not app.success
    assert app.metric[2].value == "LOCKED"
    assert not app.chat_input[0].disabled


def test_version_switch_keeps_separate_sessions(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    app = AppTest.from_file("../app.py").run()
    app.chat_input[0].set_value("examine desk").run()
    app.selectbox[0].select("Version 1 · Conversational").run()
    assert app.chat_input[0].disabled
    assert len(app.chat_message) == 0
    app.selectbox[0].select("Version 2 · Validated").run()
    assert len(app.chat_message) == 2
    assert not app.exception
