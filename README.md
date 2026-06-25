# HTMX vs THE FRAMEWORK SWARM
A tiny Space-Invaders-style demo built with pygame-ce.

You play as HTMX (the **"</>"** ship) defending the simple web from an
ever-descending wave of JS framework mascots. Shoot them down before
"JS fatigue" reaches critical mass.

## Play in your browser (WASM)

No installation required! The game is compiled to WebAssembly and hosted on GitHub Pages:

- [https://lucas-rollin.github.io/htmx-invaders/](https://lucas-rollin.github.io/htmx-invaders/)

## Controls

- LEFT/RIGHT or A/D  - move
- SPACE              - shoot
- R                  - restart after game over
- ESC                - quit

## Soundtrack:

<ul>
  <li>
    <strong>Little Smiley's Adventure</strong> -
    Music by <a href="https://pixabay.com/users/spencer_yk-36670691/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=151007">Spencer Y.K.</a> from <a href="https://pixabay.com/music//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=151007">Pixabay</a>
  </li>
  <li>
    <strong>Retro Louge - Bransboynd</strong> -
    Music by <a href="https://pixabay.com/users/bransboynd-51721546/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=389644">Roman Rumyantsev</a> from <a href="https://pixabay.com/music//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=389644">Pixabay</a>
  </li>
  <li>
    <strong>Retro - The Mountain</strong> - 
    Music by <a href="https://pixabay.com/users/the_mountain-3616498/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=143303">Dmitrii Kolesnikov</a> from <a href="https://pixabay.com/music//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=143303">Pixabay</a>
  </li>
  <li>
    <strong>A Hero of the 80s - Grand Project</strong> -
    Music by <a href="https://pixabay.com/users/grand_project-19033897/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=126684">Roman Dudchyk</a> from <a href="https://pixabay.com/music//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=126684">Pixabay</a>
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

## Using Pyinstaller to bundle an executable

Run:
```bash
pyinstaller --onefile --icon=htmx.ico --add-data "assets;assets" main.py # on windows
pyinstaller --onefile --add-data "assets:assets" main.py # on linux
```

The executable will be located in the `dist/` folder.

## Thank you for Playing

*No JavaScript libraries were hurt in the making of this game*
