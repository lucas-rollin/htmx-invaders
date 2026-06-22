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

<ul>
  <li>
    <summary>Little Smiley's Adventure - Spencer YK (Menu)</summary>
    <details>
    Music by <a href="https://pixabay.com/users/spencer_yk-36670691/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=151007">Spencer Y.K.</a> from <a href="https://pixabay.com/music//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=151007">Pixabay</a>
    </details>
  </li>
  <li>
    <summary>Retro Louge - Bransboynd</summary>
    <details>
    Music by <a href="https://pixabay.com/users/bransboynd-51721546/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=389644">Roman Rumyantsev</a> from <a href="https://pixabay.com/music//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=389644">Pixabay</a>
    </details>
  </li>
  <li>
    <summary>Retro - The Mountain</summary> 
    <details>
    Music by <a href="https://pixabay.com/users/the_mountain-3616498/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=143303">Dmitrii Kolesnikov</a> from <a href="https://pixabay.com/music//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=143303">Pixabay</a>
    </detials>
  </li>
  <li>
    <summary>A Hero of the 80s - Grand Project</summary>
    <details>
    Music by <a href="https://pixabay.com/users/grand_project-19033897/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=126684">Roman Dudchyk</a> from <a href="https://pixabay.com/music//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=126684">Pixabay</a>
    </details>
  </li>
</ul>

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