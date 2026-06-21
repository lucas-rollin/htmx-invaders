# HTMX vs THE FRAMEWORK SWARM
A tiny Space-Invaders-style demo built with pygame-ce.

You play as HTMX (the **"</>"** ship) defending the simple web from an
ever-descending wave of JS framework mascots. Shoot them down before
"JS fatigue" reaches critical mass.

Controls:

- LEFT/RIGHT or A/D  - move
- SPACE              - shoot
- R                  - restart after game over
- ESC                - quit

## Soundtrack:

- Hub World - Guild Wars 2
- Code Geass - The Master 
- Gate of Steiner (Synthwave Remix) - Mr. McNoggig
- Sunny Glade - Guild Wars 2
- City Ruins - 8 bit, Nier Automata
- Wretched Weaponry - 8 bit, Nier Automata
- War War - 8 bit, Nier Automata

## Start game in Development

1. Start the virtual enviroment:
```bash
python -m venv venv
```

2. Activate the virtual enviroment:
```bash
.\venv\Scripts\activate # on windows
source venv/bin/activate # on linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the game:
```bash
python main.py
```

## Using Pyinstaller to bundle

Run:
```bash
pyinstaller --onefile --icon=htmx.ico --add-data "assets;assets" main.py
```

## Thank you for Playing

*No JavaScript libraries were hurt in the making of this game*