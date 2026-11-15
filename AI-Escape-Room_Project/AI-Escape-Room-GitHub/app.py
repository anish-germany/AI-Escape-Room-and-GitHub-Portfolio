"""Run: streamlit run app.py"""
import os
import streamlit as st
from dotenv import load_dotenv
from escape_room.config import INTRO
from escape_room.llm import LLMError
from escape_room.v1 import turn
from escape_room.v2 import State, apply, narrate

load_dotenv()
st.set_page_config(page_title="The Midnight Archive", page_icon="🗝️", layout="wide")
st.markdown('''<style>
.stApp {background:radial-gradient(ellipse at top right,#25312d 0%,#101b19 50%,#0c1312 100%);color:#eee8d9}
h1,h2,h3 {font-family:Georgia,serif!important;color:#f2dfb0!important}
[data-testid="stSidebar"] {background:#111e1a;border-right:1px solid #4a5140}
[data-testid="stChatMessage"] {background:#1b2924;border:1px solid #34473b;border-radius:14px}
.stButton>button {border:1px solid #7c7756;background:#20372d;color:#f2dfb0;border-radius:10px}
[data-testid="stMetricValue"] {color:#d8c58d}
</style>''', unsafe_allow_html=True)
with st.sidebar:
    st.caption("AN INTERACTIVE AI MYSTERY")
    st.header("The Archive")
    version = st.selectbox("Game version", ["Version 2 · Validated", "Version 1 · Conversational"])
    live = st.toggle("Gemini Game Master", value=False)
    st.caption("Gemini uses your server's .env key. Offline V2 makes no API requests. V1 needs Gemini.")
    if st.button("Restart game", use_container_width=True):
        st.session_state.games = {}
        st.rerun()
    st.divider()
    st.write("**How to play**")
    st.write("Explore five objects. Collect items. Solve the bookshelf riddle, unlock the painting, then decode the exit.")
    st.caption("One action per message. Try ‘I want to examine the bookshelf’ or ‘pick up the key’.")

if "games" not in st.session_state:
    st.session_state.games = {}
# A separate state and transcript for each version; no module-level shared players.
game = st.session_state.games.setdefault(version, {"state": State(), "history": [], "escaped": False, "status": ""})
is_v2 = version.startswith("Version 2")
state = game["state"]
st.caption("THE MIDNIGHT ARCHIVE / ESCAPE ROOM")
st.title("Some secrets open doors.")
st.write(INTRO)
a, b, c = st.columns(3)
a.metric("Version", "02" if is_v2 else "01")
b.metric("Puzzles solved", f"{int(state.drawer_open)+int(state.painting_open)+int(state.escaped)} / 3" if is_v2 else "LLM managed")
c.metric("Door", "OPEN" if game["escaped"] else "LOCKED")
if is_v2:
    st.progress((int(state.drawer_open)+int(state.painting_open)+int(state.escaped))/3)
    st.caption("INVENTORY · " + (" / ".join(sorted(state.inventory)) or "Nothing collected yet"))
else:
    st.info("V1 baseline: Gemini controls the story, inventory and completion using conversation history. It can make mistakes.")
    if not live or not os.getenv("GEMINI_API_KEY", "").strip():
        st.warning("Enable Gemini and configure your own free-tier API key to play V1. V2 is playable offline.")

with st.expander("Room guide & command examples"):
    st.write("Desk · Bookshelf · Painting · Drawer · Door")
    st.code("examine the desk\ntake the brass key\nexamine the painting\nuse the key on the painting\nexamine the bookshelf\nopen drawer with 123\ntake the cipher card\nread the card\nunlock door with 1234\ninventory\nhint")
    st.caption("123 and 1234 are examples, not the solutions. More commands: look around, inspect, investigate, collect, pick up, help.")

for entry in game["history"]:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])
if game["escaped"]:
    st.success("You escaped! Restart for another playthrough.")
if game["status"]:
    st.caption(game["status"])
message = st.chat_input("What do you do next?", max_chars=500,
                        disabled=game["escaped"] or (not is_v2 and (not live or not os.getenv("GEMINI_API_KEY", "").strip())))
if message:
    if is_v2:
        outcome = apply(state, message)
        reply, status = narrate(outcome) if live else (outcome, "Offline · Python rules, no LLM calls")
        game["history"].extend([{"role": "user", "content": message}, {"role": "assistant", "content": reply}])
        game["escaped"] = state.escaped
        game["status"] = status
    else:
        try:
            game["history"], game["escaped"] = turn(game["history"], message)
            game["status"] = "Gemini · conversational baseline"
        except LLMError as error:
            st.error(str(error))
            st.stop()
    st.rerun()
