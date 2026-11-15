from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("Body", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Title", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"))
p = Path(__file__).resolve().parents[1] / 'docs/report.pdf'
c = canvas.Canvas(str(p), pagesize=(595.28,841.89))
c.setTitle('The Midnight Archive - Design and Evaluation')
c.setAuthor('Anish Khobragade')
W,H=595.28,841.89
navy=HexColor('#172c26'); gold=HexColor('#ad8845'); gray=HexColor('#48554e')
y=0

def page(n,title,sub):
 global y
 c.setFillColor(navy); c.rect(0,H-145,W,145,fill=1,stroke=0)
 c.setFillColor(HexColor('#d6bd81')); c.setFont('Bold',10); c.drawString(44,H-43,'THE MIDNIGHT ARCHIVE / AI ESCAPE ROOM')
 c.setFillColor(HexColor('#ffffff')); c.setFont('Title',25); c.drawString(44,H-84,title)
 c.setFont('Body',10); c.drawString(44,H-112,sub)
 c.setFillColor(gray); c.setFont('Body',9); c.drawString(44,31,'Anish Khobragade | 15 November 2026 | AI-assisted implementation')
 c.drawRightString(W-44,31,f'{n} / 3')
 y=H-172

def heading(t):
 global y
 c.setFillColor(navy); c.setFont('Bold',12); c.drawString(44,y,t);y-=20

def para(t,size=9.3):
 global y
 c.setFillColor(gray);c.setFont('Body',size)
 for line in simpleSplit(t,'Body',size,W-88):
  c.drawString(44,y,line);y-=12.5
 y-=7

def diagram(nodes,edges,height):
 global y
 # positions are intentionally compact; exact labels, no generated imagery.
 top=y; boxes={}
 for key,label,col,row in nodes:
  x=44+col*174; by=top-row*66-36
  boxes[key]=(x,by,156,36)
  c.setFillColor(HexColor('#eef2eb'));c.setStrokeColor(gold);c.roundRect(x,by,156,36,5,fill=1,stroke=1)
  c.setFillColor(navy);c.setFont('Body',9)
  ls=label.split('|')
  for i,line in enumerate(ls): c.drawCentredString(x+78,by+23-i*12,line)
 c.setStrokeColor(gray);c.setFillColor(gray)
 for a,b in edges:
  x1,y1,w,h=boxes[a];x2,y2,w2,h2=boxes[b]
  if y1==y2:
   sx,sy=(x1+w if x2>x1 else x1),y1+h/2;ex,ey=(x2 if x2>x1 else x2+w2),y2+h2/2
  else:
   sx,sy=x1+w/2,y1;ex,ey=x2+w2/2,y2+h2
  c.line(sx,sy,ex,ey)
  import math
  ang=math.atan2(ey-sy,ex-sx)
  for d in [-.45,.45]:c.line(ex,ey,ex-6*math.cos(ang+d),ey-6*math.sin(ang+d))
 y=top-height

page(1,'Design and implementation','A conversational baseline and a Python-validated improvement')
heading('1. Objective and puzzle design')
para('The application places a player inside a locked library. A Streamlit chat interface accepts natural-language actions to explore five objects: a desk, bookshelf, painting, locked drawer and exit door. The objective is to collect items, solve three puzzles and escape. Python and a free-tier Gemini API integration meet the technical brief without training a model or using a GPU.')
para('The bookshelf riddle asks for the number of triangle sides, Earth\'s moons and yearly seasons. The answer 314 unlocks the drawer, which contains a cipher card. A brass key collected from the desk opens the painting and reveals a symbol order. Combining that order with the card yields 7259, the final door code. The door also requires the earlier puzzle flags and the collected card, so guessing the code alone cannot complete V2.')
heading('2. Version 1: interactive conversational Game Master')
para('The initial implementation sends the room rules, solutions and full conversation to Gemini. The model describes objects, remembers player actions and tracks inventory through dialogue. Streamlit stores the history within the session and provides restart. A generated [ESCAPED] marker triggers completion. This is intentionally a simple baseline for normal, cooperative players.')
diagram([('p','Player / Streamlit',0,0),('h','Conversation history',1,0),('g','Gemini + room prompt',2,0),('o','Narration + escape marker',2,1)],[('p','h'),('h','g'),('g','o')],130)
para('Architecture limitation: Python does not verify whether the generated narration is physically possible. The system prompt includes secrets and the escape marker is trusted. Consequently, an incorrect model answer can become the displayed game truth. This risk motivated the second version; no actual live Gemini failure is claimed in this report.')
heading('3. Technologies and setup')
para('The project uses Python 3.11+, Streamlit, requests and python-dotenv. A server-side .env provides GEMINI_API_KEY and GEMINI_MODEL; .env.example documents the settings and .gitignore excludes credentials. The default model is gemini-2.5-flash-lite. Model availability and free quotas should be checked in Google AI Studio. The application does not automatically detect the account billing tier.')
c.showPage()
page(2,'Reliability through explicit rules','Version 2: structured state, validation and constrained narration')
heading('4. State and action validation')
para('A Python dataclass holds examined objects, a set of inventory items, drawer status, painting status and escape status. Each browser session has its own state and transcript for each version. The apply() function is the only game-state writer. It parses one action, checks object availability and prerequisites, then updates state only when permitted. Invalid actions return useful feedback without changing state.')
para('The parser accepts common phrases such as "I want to examine the bookshelf", "pick up the key" and "use the key on the painting". Full-match patterns reject compound or unrecognized instructions instead of executing a plausible substring. This bounds language support, but explicit examples and hints make the interface usable. Inventory sets make repeated collection idempotent.')
heading('5. Version 2 architecture')
diagram([('ui','Player / Streamlit',0,0),('p','Bounded language parser',1,0),('e','Python validator|+ room rules',2,0),('s','Session state',2,1),('o','Validated outcome',1,1),('g','Gemini selects atmosphere',0,1),('v','Exact JSON validation|or deterministic fallback',0,2),('d','Outcome + safe line|shown in Streamlit',1,2)], [('ui','p'),('p','e'),('e','s'),('e','o'),('o','g'),('g','v'),('v','d')],205)
para('The narrator receives only an already validated outcome, not the raw player instruction, full state or all hidden solutions. It chooses one of three predefined atmospheric sentences using JSON. Python validates the exact schema and index, then displays the authoritative outcome plus the approved line. Arbitrary model prose never reaches the player. Timeouts and malformed responses fall back to the outcome.')
heading('6. Improvements and tradeoffs')
para('A player cannot use an uncollected key, take an item from a locked drawer, assert that puzzles are solved or impersonate an administrator to alter state. Completion comes from the engine\'s escaped flag rather than a generated phrase. Restart creates fresh state; switching versions preserves separate transcripts. V2 also works offline with explicit labelling and no network requests.')
para('The cost of this design is a smaller LLM role: V1 provides free-form storytelling, while V2 uses Gemini for constrained atmospheric narration. This intentionally favors consistency over linguistic variety. The engine does not secure publicly available source-code solutions, prevent brute-force guessing or provide accounts, multiplayer support or permanent saves. These are limitations rather than claims of production security.')
c.showPage()
page(3,'Testing and evidence','Automated checks, development record and remaining live validation')
heading('7. Evaluation method and results')
para('The local suite contains 50 passing tests covering Python game transitions, inventory, rejected actions, Gemini REST response handling and Streamlit AppTest interaction. The full valid walkthrough reaches escape; the UI disables further actions and restart restores a locked door. Test output and a 14-scenario comparison table are included in docs/. The offline GIF and transcript are generated from real engine outputs, not a live Gemini recording.')
# compact readable comparison table
rows=[('Challenge','Version 2 observed result'),('Use key before collecting','Rejected; state unchanged'),('Incorrect drawer code','Drawer stays locked'),('Correct exit code too early','Prerequisites block escape'),('Claim solved / impersonate admin','No state change'),('Reveal all codes / invent object','No secret output or invented item'),('Malicious narrator / API outage','Validated outcome retained'),('Valid solution / restart','Escape succeeds; restart clears')]
widths=[224,283]; rowh=25
for i,row in enumerate(rows):
 c.setFillColor(navy if i==0 else HexColor('#eef2eb') if i%2 else HexColor('#f7f8f5'))
 c.rect(44,y-rowh,507,rowh,fill=1,stroke=0)
 c.setFillColor(HexColor('#ffffff') if i==0 else gray);c.setFont('Bold' if i==0 else 'Body',9)
 c.drawString(51,y-16,row[0]);c.drawString(51+widths[0],y-16,row[1]);y-=rowh
y-=19
heading('8. What is and is not demonstrated')
para('No real API credential was supplied, so live V1/V2 Gemini behavior remains untested. HTTP adapter tests use mocked responses, including errors and timeouts. A controlled V1 fault-injection test deliberately returns an incorrect escape marker: the baseline accepts it, whereas the V2 engine rejects the same administrator claim. This demonstrates the trust boundary, not an empirically observed Gemini jailbreak.')
para('Before submission, the student should run both versions with a personal free-tier key, record model ID and exact outputs for the challenging cases, capture a short live screen recording and add the evidence to GitHub. The supplied test guide describes this procedure. No successful live API run, personal student review or GitHub publication is implied by the automated results.')
heading('9. Development, portfolio and reflection')
para('The work was committed in actual implementation stages: the V1 baseline, the V2 validation engine, the test suite and documentation. The v1.0 tag retains the original baseline; v2.0 marks the completed package. The repository contains the source, configuration template, architecture diagrams, walkthrough, evidence and this report. The instructor needs access to the final repository URL.')
para('ChatGPT (Codex) assisted with code, puzzle design, tests and documentation. The student must review the work and explain how validation differs from prompting, why model output is untrusted, and where the bounded parser can reject legitimate English. Future work could add a validated structured-action interpreter, richer safe narration templates and persistent saves without transferring state authority to the LLM.')
para('References: Course brief, MiniProject_01_EscapeRoom.pdf (supplied). Google Gemini REST reference: https://ai.google.dev/api/generate-content ; Gemini pricing/free-tier reference: https://ai.google.dev/gemini-api/docs/pricing .',size=9)
c.save()
print(p)
