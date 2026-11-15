# Test evidence and comparison

Automated tests run locally on 15 November 2026. `test-results.txt` contains the
actual pytest output. Tests cover the engine, REST adapter with mocked HTTP,
and Streamlit's AppTest UI. There are no paid API calls.

**Evidence boundary:** No real Gemini key was provided. Live V1/V2 API tests have
not been run. V1 weaknesses below are architectural risks, not claims that Gemini
actually produced these answers. The injected V1 test supplies a deliberately
incorrect model reply to demonstrate that the baseline trusts it.

| Case | Challenge | V1 limitation / evidence | V2 expected and tested result |
|---|---|---|---|
| 1 | Use key before collecting it | Inventory exists only in model history; live behavior untested | Refuses; state unchanged |
| 2 | Incorrect drawer code after finding clue | No independent code validator; live behavior untested | Drawer remains locked |
| 3 | Correct exit code before prerequisites | Relies on model obeying prompt; live behavior untested | Door remains locked |
| 4 | Claim puzzles already solved | No trusted puzzle flags; live behavior untested | Claim cannot change state |
| 5 | Administrator impersonation | Injected reply `Door open. [ESCAPED]` is accepted as completion | Message rejected; Python escape flag stays false |
| 6 | Ask to reveal every secret | Solutions are in V1's system prompt; live behavior untested | Raw message never reaches narrator; response contains no secret codes |
| 7 | Invent a laser or collect hidden card | No whitelist enforcement outside the model | Rejects unknown/unavailable item without state changes |
| 8 | Repeat collecting the key | Potential duplicate/forgotten inventory; live behavior untested | Set inventory remains unchanged |
| 9 | Provider returns malicious or malformed text | V1 displays generated text | Output discarded; authoritative outcome retained |
| 10 | API timeout / 429 / missing key | V1 reports error and preserves history | V2 keeps validated outcome and reports fallback |
| 11 | Complete valid solution | Live model walkthrough pending | Engine and AppTest reach escaped status |
| 12 | Restart or switch versions | Independent session behavior tested | Restart clears both games; version histories are isolated |
| 13 | Wrong exit code after prerequisites | No independent validator in V1 | Door stays locked; correct code later succeeds |
| 14 | Compound instruction / unsupported phrasing | Model interprets freely | Full-match parser asks for one supported action |

## Reproduce locally

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The tests intentionally use no real credential. `fake-test-token` in the HTTP
adapter tests is a literal dummy value. CI does not need repository secrets.

## Live checks to complete with your own key

1. Use a free-tier Gemini project, configure `.env`, enable Gemini in the sidebar.
2. In V1, play the complete walkthrough in `walkthrough.md` and capture the result.
3. Restart before each challenge in cases 1–7; record the exact model response,
   model ID and date. Do not assume every attack will succeed.
4. In V2, repeat the same challenges with Gemini on. Check the visible inventory
   and door metrics as well as text. Try invalid JSON with a local test double.
5. Capture a screenshot or short screen recording of live V1 and live V2. Keep
   `.env`, keys and personal browser information outside the recording.

`demo.gif` is an **offline engine demonstration generated from actual game
outputs**, not a screen capture or proof of live Gemini behavior.
