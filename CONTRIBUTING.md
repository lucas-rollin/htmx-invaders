# Contributing to HTMX Invaders

First off, thank you for taking the time to contribute! 🎉 

Whether you're fixing a bug, improving the WASM build, or adding more fuel to the fire, contributions are welcome.

## Setup & Local Development

1. **Clone & Setup Environment:**
    
    ```bash
    git clone https://github.com/lucas-rollin/htmx-invaders.git
    cd htmx-invaders
    uv sync
    ```

2. **Run Desktop Game Locally:**
    
    ```bash
    uv run htmx-invaders
    ```

3. **Run Tests:**
    
    ```bash
    uv run pytest
    ```

## WebAssembly (WASM) Development

1. **Sync WASM Dependencies:**
    
    ```bash
    uv sync --only-group wasm
    ```

2. **Stage & Run Local WASM Server:**

    ```bash
    rm -rf build/app && mkdir -p build/app
    cp -r src/htmx_invaders assets build/app/
    cp web/main.py build/app/main.py

    uv run pygbag build/app
    ```

    Open `http://localhost:8000` (or `http://localhost:8000/#debug` for interactive debugging).

3. **Test on Mobile Devices:**

    Find your local IP address (e.g., `192.168.1.X`) and run:

    ```bash
    uv run pygbag --bind <YOUR_LOCAL_IP> build/app
    ```

    Access `http://<YOUR_LOCAL_IP>:8000` on a mobile device connected to the same Wi-Fi network.

## Building Desktop Executables (PyInstaller)

* **Windows:**

    ```bash
    uv run pyinstaller --onefile --icon=htmx.ico --add-data "assets;assets" main.py
    ```

* **Linux:**

    ```bash
    uv run pyinstaller --onefile --add-data "assets:assets" main.py
    ```

## How to Contribute

1. **Fork the repository** and clone it locally.

2. Set up your environment using **`uv`**:

    ```bash
    uv sync
    ```

3. Create a new branch for your feature or fix:

    ```bash
    git switch -c feature/more-framework-jokes
    ```

4. Run tests to make sure everything works:

    ```bash
    uv run pytest
    ```

5. Push your branch and open a **Pull Request**.

Let's keep the web simple! 🚀
