"""V2: the engine is the only writer of game state.

The parser accepts a bounded natural-language grammar with full-match patterns.
Unknown or compound instructions fail closed and ask for one supported action.
The model can select an atmosphere line; it cannot supply displayed game facts.
"""
from dataclasses import dataclass, field, asdict
import json
import re
from .config import OBJECTS, DRAWER_CODE, DOOR_CODE
from .llm import generate, LLMError


@dataclass
class State:
    examined: set = field(default_factory=set)
    inventory: set = field(default_factory=set)
    painting_open: bool = False
    drawer_open: bool = False
    escaped: bool = False

    def public(self):
        return {**asdict(self), "examined": sorted(self.examined),
                "inventory": sorted(self.inventory)}


HELP = ("Try: look around; examine the desk; take the brass key; examine the bookshelf; "
        "examine the painting; use the brass key on the painting; open drawer with 123; "
        "take the cipher card; read the cipher card; unlock door with 1234; inventory; hint. "
        "Use one action per message. Codes here are examples.")


def parse(message):
    text = message.lower().strip().rstrip(".!?")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"^(?:please |i want to |i would like to |i |can i )", "", text)
    text = re.sub(r"^(?:please )", "", text)
    if text in ("look", "look around", "examine room", "examine the room"):
        return "look", "", ""
    if text in ("help", "hint", "inventory"):
        return text, "", ""
    patterns = (
        (r"(?:examine|inspect|investigate|look at|read) (?:the )?(.+)", "examine"),
        (r"(?:take|collect|pick up) (?:the )?(.+)", "take"),
        (r"use (?:the )?(?:brass )?key on (?:the )?painting", "key"),
        (r"(?:open|unlock) (?:the )?(drawer|door|exit)(?: with(?: (?:the )?code)?| code)? (\d+)", "code"),
        (r"(?:open|unlock) (?:the )?(drawer|door|exit)", "open"),
    )
    for pattern, verb in patterns:
        match = re.fullmatch(pattern, text)
        if match:
            groups = match.groups()
            return verb, groups[0] if groups else "", groups[1] if len(groups) > 1 else ""
    return "unknown", "", ""


def apply(state, message):
    """Validate then mutate. Rejected actions leave state exactly unchanged."""
    if not isinstance(message, str) or not message.strip() or len(message) > 500:
        return "Enter one action between 1 and 500 characters."
    verb, target, code = parse(message)
    if state.escaped:
        return "You have escaped. Restart to play again."
    if verb == "help":
        return HELP
    if verb == "inventory":
        return "Inventory: " + (", ".join(sorted(state.inventory)) or "empty") + "."
    if verb == "look":
        return "The room contains a desk, bookshelf, painting, locked drawer and keypad door."
    if verb == "hint":
        if "bookshelf" not in state.examined:
            return "Investigate the bookshelf. Its riddle is the first puzzle."
        if not state.drawer_open:
            return "Count each thing in the bookshelf riddle, in the order written."
        if "cipher card" not in state.inventory:
            return "Collect the item inside the open drawer."
        if not state.painting_open:
            return "The painting has a keyhole. Look for a key on the desk and collect it."
        return "Match the painting's symbol order to the cipher card. Try the resulting four digits on the door."
    if verb == "examine":
        if target in ("card", "cipher card"):
            if "cipher card" not in state.inventory:
                return "Collect the cipher card before reading it."
            return "Cipher card: Moon=7, Raven=2, Oak=5, Star=9."
        if target not in OBJECTS:
            return "That object is not available. Examine the desk, bookshelf, painting, drawer or door."
        state.examined.add(target)
        if target == "desk":
            return "A brass key rests on the desk." if "brass key" not in state.inventory else "The desk is empty; you already collected its brass key."
        if target == "bookshelf":
            return "A riddle reads: How many sides has a triangle, how many moons orbit Earth, how many seasons has a year? Enter those digits on the drawer."
        if target == "painting":
            return "Behind the painting: Order: Moon, Raven, Oak, Star." if state.painting_open else "A tiny keyhole is hidden in the painting's frame."
        if target == "drawer":
            return ("The drawer is open. " + ("Its cipher card is in your inventory." if "cipher card" in state.inventory else "A cipher card waits inside.")) if state.drawer_open else "The drawer is locked with a three-digit combination."
        return "The exit has a four-digit keypad. You need the drawer's cipher card and the painting's symbol order."
    if verb == "take":
        item = {"key": "brass key", "card": "cipher card"}.get(target, target)
        if item in state.inventory:
            return "You already have that item."
        if item == "brass key" and "desk" in state.examined:
            state.inventory.add(item)
            return "You collect the brass key."
        if item == "cipher card" and state.drawer_open:
            state.inventory.add(item)
            return "You collect the cipher card. Read it to decode the symbols."
        return "That item is not available to collect. Examine its location and unlock any container first."
    if verb == "key":
        if "brass key" not in state.inventory:
            return "You must collect the brass key before using it."
        if "painting" not in state.examined:
            return "Examine the painting before using the key."
        state.painting_open = True
        return "The painting swings open. Order: Moon, Raven, Oak, Star."
    if verb in ("open", "code"):
        if target == "drawer":
            if state.drawer_open:
                return "The drawer is already open."
            if "bookshelf" not in state.examined:
                return "Find and examine the bookshelf clue first."
            if code != DRAWER_CODE:
                return "The drawer stays locked. Its combination needs three correct digits."
            state.drawer_open = True
            return "The drawer clicks open. A cipher card is inside; collect it."
        if not (state.drawer_open and state.painting_open and "cipher card" in state.inventory):
            return "The exit stays locked. Solve the drawer and painting puzzles, and collect the cipher card first."
        if code != DOOR_CODE:
            return "The door code is incorrect. Match the symbol order to the cipher card."
        state.escaped = True
        return "The lock releases. You step into the dawn. You escaped the Midnight Archive!"
    return "I could not interpret that as one room action. " + HELP


ATMOSPHERE = (
    "Lamplight pools across the old wood.",
    "Rain taps softly against the library windows.",
    "Somewhere in the archive, a clock ticks.",
)


def narrate(outcome, generator=generate):
    """Constrained Game Master: choose tone without rendering model-written facts.

    No raw player messages, full state, system secrets or chat history are sent.
    Even a compromised model can only select one preapproved atmosphere sentence.
    The authoritative outcome is always shown, including during outages.
    """
    try:
        raw = generator(
            'Choose a fitting atmospheric line for the validated escape-room outcome. '
            'Return only JSON: {"line": 0}, {"line": 1}, or {"line": 2}. '
            + json.dumps(list(ATMOSPHERE)),
            [{"role": "user", "content": json.dumps({"validated_outcome": outcome})}],
        )
        data = json.loads(raw)
        index = data.get("line") if isinstance(data, dict) else None
        if type(index) is not int or index not in range(len(ATMOSPHERE)) or set(data) != {"line"}:
            return outcome, "fallback: unsupported model output"
        return outcome + "\n\n*" + ATMOSPHERE[index] + "*", "Gemini atmosphere"
    except (LLMError, ValueError, TypeError):
        return outcome, "fallback: Gemini unavailable"
