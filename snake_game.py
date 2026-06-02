# -*- coding: utf-8 -*-
"""
SNAKE GAME - Clean Class-Based Modular Architecture
===================================================
A polished retro console Snake Game with high performance,
zero flickering, terminal auto-centering, resizing response,
and thread-safe synchronous input checking.
"""

import os
import sys
import msvcrt
import time
import random
import re
import shutil

# Enable Windows ANSI mode
os.system('')

# ─── COLORS & TEXT EFFECTS ────────────────────────────────────────
PURPLE  = '\033[35m'
BLUE    = '\033[34m'
GREEN   = '\033[32m'
BGREEN  = '\033[92m'
YELLOW  = '\033[33m'
RED     = '\033[31m'
WHITE   = '\033[37m'
CYAN    = '\033[36m'
BOLD    = '\033[1m'
RESET   = '\033[0m'

# ─── LAYOUT METRICS ───────────────────────────────────────────────
BOX_W = 72
BOX_H = 30

BOARD_ROWS = 18
BOARD_COLS = 30

# ─── CLASSES ──────────────────────────────────────────────────────

class ScoreManager:
    """Manages scores, high scores, levels, and persistent storage."""
    def __init__(self):
        self.score = 0
        self.high_score = self.load_high()
        self.level = 1

    def load_high(self):
        try:
            if os.path.exists('snake_highscore.txt'):
                with open('snake_highscore.txt', 'r') as f:
                    return int(f.read().strip())
        except:
            pass
        return 0

    def save_high(self):
        try:
            with open('snake_highscore.txt', 'w') as f:
                f.write(str(self.high_score))
        except:
            pass

    def add_score(self, points):
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high()
        self.level = 1 + (self.score // 50)

    def reset(self):
        self.score = 0
        self.level = 1


class Snake:
    """Manages the coordinates, movements, and directions of the snake."""
    def __init__(self, start_x, start_y):
        self.body = [
            (start_x, start_y),
            (start_x, start_y - 1),
            (start_x, start_y - 2)
        ]
        self.direction = 'RIGHT'
        self.next_direction = 'RIGHT'
        self.grew = False

    def get_head(self):
        return self.body[0]

    def get_body(self):
        return self.body[1:]

    def get_all(self):
        return self.body

    def set_direction(self, new_dir):
        opposites = {
            'UP': 'DOWN',
            'DOWN': 'UP',
            'LEFT': 'RIGHT',
            'RIGHT': 'LEFT'
        }
        if new_dir != opposites.get(self.direction):
            self.next_direction = new_dir

    def move(self):
        self.direction = self.next_direction
        hx, hy = self.body[0]
        if self.direction == 'UP':
            hx -= 1
        elif self.direction == 'DOWN':
            hx += 1
        elif self.direction == 'LEFT':
            hy -= 1
        elif self.direction == 'RIGHT':
            hy += 1
        self.body.insert(0, (hx, hy))
        if not self.grew:
            self.body.pop()
        else:
            self.grew = False

    def grow(self):
        self.grew = True

    def check_self_collision(self):
        head = self.body[0]
        return head in self.body[1:]

    def check_wall_collision(self, rows, cols):
        hx, hy = self.body[0]
        return hx < 0 or hx >= rows or hy < 0 or hy >= cols

    def length(self):
        return len(self.body)


class Food:
    """Handles food spawning at safe random positions on the grid."""
    def __init__(self, snake_body):
        self.x = 0
        self.y = 0
        self.respawn(snake_body)

    def respawn(self, snake_body):
        attempts = 0
        while attempts < 1000:
            self.x = random.randint(0, BOARD_ROWS - 1)
            self.y = random.randint(0, BOARD_COLS - 1)
            if (self.x, self.y) not in snake_body:
                break
            attempts += 1

    def get_pos(self):
        return (self.x, self.y)


class InputHandler:
    """Manages console input check synchronously."""
    def get_key(self):
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key in (b'\xe0', b'\x00'):
                if msvcrt.kbhit():
                    key2 = msvcrt.getch()
                    if key2 == b'H': return 'UP'
                    if key2 == b'P': return 'DOWN'
                    if key2 == b'K': return 'LEFT'
                    if key2 == b'M': return 'RIGHT'
                return None
            try:
                return key.decode('utf-8', errors='ignore').upper()
            except:
                return None
        return None


class Renderer:
    """Handles margins positioning, terminal centering, and rendering."""
    def __init__(self):
        self.term_w = 0
        self.term_h = 0
        self.pad_x = 0
        self.pad_y = 0
        self.update_padding()

    def cls(self):
        os.system('cls')

    def hide_cursor(self):
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()

    def show_cursor(self):
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()

    def move_to(self, row, col):
        sys.stdout.write(f'\033[{row};{col}H')

    def update_padding(self):
        size = shutil.get_terminal_size()
        self.term_w = size.columns
        self.term_h = size.lines
        self.pad_x = max(0, (self.term_w - BOX_W) // 2)
        self.pad_y = max(0, (self.term_h - BOX_H) // 2)

    def check_resize(self):
        size = shutil.get_terminal_size()
        if size.columns != self.term_w or size.lines != self.term_h:
            self.cls()
            self.update_padding()
            return True
        return False

    def box_top(self):
        return PURPLE + '+' + '-' * (BOX_W - 2) + '+' + RESET

    def box_bottom(self):
        return PURPLE + '+' + '-' * (BOX_W - 2) + '+' + RESET

    def box_sep(self):
        return PURPLE + '+' + '-' * (BOX_W - 2) + '+' + RESET

    def box_line(self, text='', color=WHITE):
        ansi_escape = re.compile(r'\x1b\[[0-9;]*[mK]')
        plain_text = ansi_escape.sub('', text)
        pad = (BOX_W - 2 - len(plain_text)) // 2
        pad_left = pad
        pad_right = BOX_W - 2 - len(plain_text) - pad_left
        inner = " " * max(0, pad_left) + color + text + RESET + " " * max(0, pad_right)
        return PURPLE + '|' + RESET + inner + PURPLE + '|' + RESET

    def box_line_raw(self, left_text='', right_text='', lcolor=WHITE, rcolor=WHITE):
        gap = BOX_W - 2 - len(left_text) - len(right_text)
        inner = lcolor + left_text + RESET + ' ' * gap + rcolor + right_text + RESET
        return PURPLE + '|' + RESET + inner + PURPLE + '|' + RESET

    def draw_raw_line(self, row_idx, content_str):
        self.move_to(row_idx + self.pad_y, 1 + self.pad_x)
        sys.stdout.write(content_str)

    def format_board_row(self, board_part, control_str):
        pad_size = 34 - len(control_str)
        inner = board_part + ' ' * 2 + YELLOW + control_str + RESET + ' ' * max(0, pad_size)
        return PURPLE + '|' + RESET + inner + PURPLE + '|' + RESET

    def render_menu(self, high_score):
        self.draw_raw_line(1, self.box_top())
        self.draw_raw_line(2, self.box_line())
        self.draw_raw_line(3, self.box_line('S  N  A  K  E     G  A  M  E', CYAN + BOLD))
        self.draw_raw_line(4, self.box_line())
        self.draw_raw_line(5, self.box_sep())
        self.draw_raw_line(6, self.box_line())
        self.draw_raw_line(7, self.box_line('Retro Snake for Windows', WHITE))
        self.draw_raw_line(8, self.box_line())
        self.draw_raw_line(9, self.box_sep())
        self.draw_raw_line(10, self.box_line())
        self.draw_raw_line(11, self.box_line('[P]  Play Game', GREEN + BOLD))
        self.draw_raw_line(12, self.box_line('[Q]  Quit', RED + BOLD))
        self.draw_raw_line(13, self.box_line())
        self.draw_raw_line(14, self.box_sep())
        self.draw_raw_line(15, self.box_line(f'HIGH SCORE: {high_score}', YELLOW + BOLD))
        self.draw_raw_line(16, self.box_line())
        # pad remaining lines to BOX_H
        for r in range(17, BOX_H):
            self.draw_raw_line(r, self.box_line())
        self.draw_raw_line(BOX_H, self.box_bottom())
        sys.stdout.flush()

    def render_gameover(self, score, high_score, level):
        self.draw_raw_line(1, self.box_top())
        self.draw_raw_line(2, self.box_line())
        self.draw_raw_line(3, self.box_line('G  A  M  E     O  V  E  R', RED + BOLD))
        self.draw_raw_line(4, self.box_line())
        self.draw_raw_line(5, self.box_sep())
        self.draw_raw_line(6, self.box_line())
        self.draw_raw_line(7, self.box_line(f'FINAL SCORE :  {score}', YELLOW + BOLD))
        self.draw_raw_line(8, self.box_line(f'HIGH SCORE  :  {high_score}', YELLOW + BOLD))
        self.draw_raw_line(9, self.box_line(f'LEVEL REACHED: {level}', CYAN + BOLD))
        self.draw_raw_line(10, self.box_line())
        self.draw_raw_line(11, self.box_sep())
        self.draw_raw_line(12, self.box_line())
        self.draw_raw_line(13, self.box_line('[R] Play Again        [M] Menu        [Q] Quit', GREEN + BOLD))
        self.draw_raw_line(14, self.box_line())
        for r in range(15, BOX_H):
            self.draw_raw_line(r, self.box_line())
        self.draw_raw_line(BOX_H, self.box_bottom())
        sys.stdout.flush()

    def render_board(self, snake, food, score, high_score, level, speed_delay, status_msg):
        head = snake.get_head()
        body_all = snake.get_all()
        
        # Split body segments into head, middle, and tail
        body_middle = body_all[1:-1] if len(body_all) > 2 else []
        tail = body_all[-1] if len(body_all) > 1 else None
        
        food_pos = food.get_pos()

        # Head char based on direction
        head_char = ">"
        if snake.direction == 'UP': head_char = "^"
        elif snake.direction == 'DOWN': head_char = "v"
        elif snake.direction == 'LEFT': head_char = "<"

        # Build cells string
        lines = []
        for r in range(BOARD_ROWS):
            row_str = ''
            for c in range(BOARD_COLS):
                if (r, c) == head:
                    row_str += BGREEN + head_char + RESET
                elif (r, c) in body_middle:
                    row_str += GREEN + 'o' + RESET
                elif tail and (r, c) == tail:
                    row_str += GREEN + '·' + RESET
                elif (r, c) == food_pos:
                    row_str += RED + '*' + RESET
                else:
                    row_str += ' '
            lines.append(row_str)

        # Draw static box headers
        self.draw_raw_line(1, self.box_top())
        self.draw_raw_line(2, self.box_line('S N A K E   G A M E', CYAN + BOLD))
        self.draw_raw_line(3, self.box_sep())

        # HUD row
        hud_left = f" SCORE: {score}  HIGH: {high_score}  LEVEL: {level}"
        hud_right = f"LEN: {snake.length()}  SPEED: {speed_delay:.2f}s  [{status_msg}] "
        self.draw_raw_line(4, self.box_line_raw(hud_left, hud_right, lcolor=YELLOW + BOLD, rcolor=YELLOW + BOLD))
        self.draw_raw_line(5, self.box_sep())

        # Controls instructions panel
        controls = [
            'Controls:',
            '--------------',
            'W / Up    Move Up',
            'S / Down  Move Down',
            'A / Left  Move Left',
            'D / Right Move Right',
            'P         Pause Game',
            'R         Restart Game',
            'Q         Quit Game',
        ]

        # Top board boundary inside the box row 6
        board_top = '  ' + WHITE + '+' + '-' * BOARD_COLS + '+' + RESET
        ctrl_str = controls[0] if len(controls) > 0 else ''
        self.draw_raw_line(6, self.format_board_row(board_top, ctrl_str))

        # Main Board Rows (Rows 7 to 24)
        for r in range(BOARD_ROWS):
            board_cells = '  ' + WHITE + '|' + RESET + lines[r] + WHITE + '|' + RESET
            ctrl_str = controls[r + 1] if r + 1 < len(controls) else ''
            self.draw_raw_line(7 + r, self.format_board_row(board_cells, ctrl_str))

        # Bottom board boundary inside the box row 25
        board_bot = '  ' + WHITE + '+' + '-' * BOARD_COLS + '+' + RESET
        ctrl_str = controls[21] if len(controls) > 21 else ''
        self.draw_raw_line(25, self.format_board_row(board_bot, ctrl_str))

        self.draw_raw_line(26, self.box_sep())

        # Status warning/footer rows
        if status_msg == "PAUSED":
            self.draw_raw_line(27, self.box_line('* * * P A U S E D * * *', YELLOW + BOLD))
        else:
            self.draw_raw_line(27, self.box_line('W/A/S/D or Arrows = Move | P = Pause | R = Restart | Q = Quit', WHITE))

        self.draw_raw_line(28, self.box_bottom())
        sys.stdout.flush()


class Game:
    """Manages game loop synchronization, state machine, and loops coordination."""
    def __init__(self):
        self.score_manager = ScoreManager()
        self.renderer = Renderer()
        self.input_handler = InputHandler()
        self.state = 'MENU'
        self.running = True

    def show_menu(self):
        self.renderer.cls()
        self.renderer.update_padding()
        self.renderer.render_menu(self.score_manager.high_score)

        while True:
            # Check terminal resizing dynamically
            if self.renderer.check_resize():
                self.renderer.render_menu(self.score_manager.high_score)

            k = self.input_handler.get_key()
            if k == 'P':
                return 'PLAY'
            elif k == 'Q':
                return 'QUIT'
            time.sleep(0.05)

    def show_gameover(self):
        self.renderer.cls()
        self.renderer.update_padding()
        self.renderer.render_gameover(self.score_manager.score, self.score_manager.high_score, self.score_manager.level)

        while True:
            if self.renderer.check_resize():
                self.renderer.render_gameover(self.score_manager.score, self.score_manager.high_score, self.score_manager.level)

            k = self.input_handler.get_key()
            if k == 'R':
                return 'PLAY'
            elif k == 'M':
                return 'MENU'
            elif k == 'Q':
                return 'QUIT'
            time.sleep(0.05)

    def play_game(self):
        self.renderer.cls()
        self.renderer.update_padding()
        self.score_manager.reset()

        snake = Snake(BOARD_ROWS // 2, BOARD_COLS // 2)
        food = Food(snake.get_all())
        
        paused = False
        base_speed = 0.15
        speed_delay = base_speed
        
        status = "RUNNING"
        self.renderer.render_board(snake, food, self.score_manager.score, self.score_manager.high_score, self.score_manager.level, speed_delay, status)

        last_move_time = time.time()

        while True:
            # Handle terminal resizing dynamically
            if self.renderer.check_resize():
                self.renderer.render_board(snake, food, self.score_manager.score, self.score_manager.high_score, self.score_manager.level, speed_delay, status)

            k = self.input_handler.get_key()
            if k == 'Q':
                return 'MENU'
            elif k == 'P':
                paused = not paused
                status = "PAUSED" if paused else "RUNNING"
                self.renderer.render_board(snake, food, self.score_manager.score, self.score_manager.high_score, self.score_manager.level, speed_delay, status)
            elif k == 'R':
                # Quick restart inside gameplay
                self.score_manager.reset()
                snake = Snake(BOARD_ROWS // 2, BOARD_COLS // 2)
                food = Food(snake.get_all())
                paused = False
                status = "RUNNING"
                speed_delay = base_speed
                self.renderer.cls()
                self.renderer.render_board(snake, food, self.score_manager.score, self.score_manager.high_score, self.score_manager.level, speed_delay, status)
                last_move_time = time.time()
                continue

            # Steer snake
            if k in ('W', 'UP'):    snake.set_direction('UP')
            elif k in ('S', 'DOWN'):  snake.set_direction('DOWN')
            elif k in ('A', 'LEFT'):  snake.set_direction('LEFT')
            elif k in ('D', 'RIGHT'): snake.set_direction('RIGHT')

            now = time.time()
            if not paused and (now - last_move_time) >= speed_delay:
                last_move_time = now

                snake.move()

                # Collision checks
                if snake.check_wall_collision(BOARD_ROWS, BOARD_COLS):
                    return 'GAMEOVER'
                if snake.check_self_collision():
                    return 'GAMEOVER'

                # Food collision
                if snake.get_head() == food.get_pos():
                    snake.grow()
                    self.score_manager.add_score(10)
                    food.respawn(snake.get_all())
                    
                    # Update speed levels
                    speed_delay = max(0.04, base_speed - (self.score_manager.level - 1) * 0.02)

                self.renderer.render_board(snake, food, self.score_manager.score, self.score_manager.high_score, self.score_manager.level, speed_delay, status)

            time.sleep(0.01)

    def run(self):
        try:
            self.renderer.hide_cursor()
            while self.running:
                if self.state == 'MENU':
                    self.state = self.show_menu()
                elif self.state == 'PLAY':
                    self.state = self.play_game()
                elif self.state == 'GAMEOVER':
                    self.state = self.show_gameover()
                elif self.state == 'QUIT':
                    self.running = False
        except KeyboardInterrupt:
            pass
        finally:
            self.renderer.show_cursor()
            self.renderer.cls()
            print(GREEN + "Thanks for playing Snake! Goodbye." + RESET)


# ─── MAIN ENTRYPOINT ──────────────────────────────────────────────
def main():
    game = Game()
    game.run()

if __name__ == '__main__':
    main()
