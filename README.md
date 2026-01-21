#  Poketwo Autocatcher
This is a simple Discord self-bot designed to catch Pokémon on Poketwo 24/7 so you don't have to.  
**Use main for catching via hints and beta for catching via AI.**

---

###  Features
* **AI:** Uses a trained deep learning model to identify Pokémon instantly from images.
* **Smart Backup:** Automatically switches to a hint-based regex solver if the AI guess is incorrect or missing.
* **Performant:** Supports **GPU acceleration (CUDA)** and asynchronous processing for near-instant catches.
* **Safety Lock:** Detects captchas immediately and pauses the bot to protect your account from flags.
* **Multi-Functional:** Includes remote commands like `!say` and `!react` for manual control over the self-bot.


---

###  Quick Start
1.  **Clone the Repo:**
    ```bash
    git clone https://github.com/amansingh903/Poketwo-Autocatcher.git
    cd Poketwo-Autocatcher
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure:** Add your token and channel IDs to `config.py`.
4.  **Launch:**
    ```bash
    python main.py
    ```

---


> **Disclaimer:** Using self-bots is against Discord ToS. Use this for educational purposes (or at your own risk!).
