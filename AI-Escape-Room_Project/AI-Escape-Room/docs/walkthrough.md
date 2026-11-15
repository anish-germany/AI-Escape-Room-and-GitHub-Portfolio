# Spoiler walkthrough and demo script

## Legitimate playthrough

1. `examine the desk` — reveals a brass key.
2. `take the brass key` — adds it to inventory.
3. `examine the bookshelf` — triangle sides, Earth's moons, seasons = **314**.
4. `open drawer with 314` — opens the drawer; first puzzle complete.
5. `take the cipher card` — adds the cipher to inventory.
6. `read the cipher card` — Moon=7, Raven=2, Oak=5, Star=9.
7. `examine the painting` — reveals its keyhole.
8. `use the brass key on the painting` — reveals Moon, Raven, Oak, Star; second puzzle complete.
9. `unlock door with 7259` — combines order and cipher; third puzzle complete, escape.

The painting and drawer branches can be solved in either order. The key is
reusable and is not consumed. The card cannot be collected before opening the
drawer. The door requires the two preceding puzzles plus the collected card,
even if a player guesses the correct code.

## Explain the code in a demonstration

- `config.py`: room objects and fixed puzzle solutions; these are game spoilers,
  not credentials.
- `v1.py`: sends chat history to Gemini and trusts an escape marker.
- `v2.py`: parses one action, checks prerequisites, updates `State`, returns facts.
- `narrate()`: selects safe atmosphere without rendering untrusted generated facts.
- `llm.py`: HTTP request, timeouts, no key in URL and redacted error messages.
- `app.py`: session isolation, independent version transcripts, restart, inventory.
- `tests/`: valid solution, bypass attempts, failures and UI behavior.

Run the offline recording generator with `python scripts/make_demo.py` after
installing Pillow (`python -m pip install Pillow`). It produces `docs/demo.gif`
and `docs/demo-transcript.txt` from a fresh `State`, including adversarial checks.

The PDF can be regenerated with `python scripts/make_report.py` after installing
ReportLab (`python -m pip install reportlab`). The generation scripts use DejaVu
fonts, available on most Linux systems; adjust font paths on Windows if needed.
