# Retro Snake Console Game 🐍

A polished, high-performance, and fully responsive implementation of the classic Snake game optimized for Windows PowerShell and Command Prompt.

---

## 🕹️ Controls

*   **W / Arrow Up:** Move Up
*   **S / Arrow Down:** Move Down
*   **A / Arrow Left:** Move Left
*   **D / Arrow Right:** Move Right
*   **P:** Pause / Resume Game
*   **R:** Restart Game (from Game Over or during Gameplay)
*   **Q:** Quit Game (returns to Menu / Exits)

---

## ✨ Features

*   **Zero-Flicker Rendering:** Redraws only changing cells and HUD lines using precise cursor placement escape sequences, ensuring smooth graphics.
*   **Auto-Centering Layout:** Automatically centers the gameplay bounding box both vertically and horizontally based on current console dimensions.
*   **Responsive Terminal Resize:** Monitors window bounds and dynamically adjusts margins on the fly without breaking the UI.
*   **Side-by-Side HUD & Legend:** Displays real-time Score, High Score, Level, Snake Length, and Speed on a dedicated top stats line, with a control instructions legend aligned on the right.
*   **Speed Scaling Difficulty:** Movement speed increases seamlessly as the snake levels up (every 50 points).
*   **Persistent High Score:** High scores are saved locally inside `snake_highscore.txt`.

---

## 🚀 Installation & How to Run

### Prerequisites
1.  Windows 10/11 operating system.
2.  Python 3.x installed.

### Execution
Open PowerShell or Command Prompt, navigate to this folder, and run:
```powershell
python snake_game.py
```
*Note: Make sure your terminal window is resized to at least 80 columns by 30 rows.*
