"""
Catch the Falling Objects
A simple 2D game built with Pygame demonstrating core Python concepts.
"""

import pygame
import random

# ─────────────────────────────────────────
# INITIALISE PYGAME
# ─────────────────────────────────────────
pygame.init()

# ── Window settings ──────────────────────
WINDOW_WIDTH  = 600
WINDOW_HEIGHT = 500
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Catch the Falling Objects")

# ── Clock to control FPS ─────────────────
clock = pygame.time.Clock()
FPS = 60

# ── Fonts ─────────────────────────────────
font_large  = pygame.font.SysFont("Arial", 38, bold=True)
font_medium = pygame.font.SysFont("Arial", 24, bold=True)
font_small  = pygame.font.SysFont("Arial", 18)

# ─────────────────────────────────────────
# COLOURS  (tuples of RGB values)
# ─────────────────────────────────────────
WHITE      = (255, 255, 255)
BLACK      = (  0,   0,   0)
DARK_BG    = ( 15,  15,  35)
BASKET_COL = ( 80, 160, 255)
BASKET_RIM = (140, 200, 255)
RED        = (220,  50,  50)
GREEN      = ( 50, 205,  50)
YELLOW     = (255, 215,   0)
ORANGE     = (255, 140,   0)
CYAN       = (  0, 220, 220)
PURPLE     = (180,  80, 220)
PINK       = (255, 105, 180)
SCORE_COL  = (100, 255, 180)
LIVES_COL  = (255,  90,  90)
LEVEL_COL  = (255, 215,   0)
GRAY       = ( 80,  80,  80)
DARK_GRAY  = ( 30,  30,  50)

# Pool of colours an object can randomly pick from
OBJECT_COLOURS = [RED, GREEN, YELLOW, ORANGE, CYAN, PURPLE, PINK]

# ─────────────────────────────────────────
# BASKET constants
# ─────────────────────────────────────────
BASKET_WIDTH  = 80
BASKET_HEIGHT = 22
BASKET_SPEED  = 7
BASKET_Y      = WINDOW_HEIGHT - 50      # fixed vertical position

# ─────────────────────────────────────────
# SPAWN TIMING
# ─────────────────────────────────────────
SPAWN_INTERVAL_MS = 1200                # milliseconds between new objects

# ─────────────────────────────────────────
# HELPER — build a fresh game_state dict
# ─────────────────────────────────────────
def make_game_state() -> dict:
    """
    DICTIONARY game_state:
    Stores all the mutable runtime data for one game session.
    Keys and their types:
        score      (int)   – current player score
        lives      (int)   – remaining lives (starts at 3)
        level      (int)   – current difficulty level
        fall_speed (float) – pixels the objects drop each frame
        game_over  (bool)  – flag that stops the update logic
    """
    return {
        "score":      0,
        "lives":      3,
        "level":      1,
        "fall_speed": 2.5,
        "game_over":  False,
    }

# ─────────────────────────────────────────
# HELPER — spawn one falling object
# ─────────────────────────────────────────
def spawn_object() -> dict:
    """
    LIST of objects:
    Each falling object is a dictionary stored inside the list `falling_objects`.
    Keys:
        x     (int)   – horizontal centre position
        y     (float) – vertical top position (float for smooth movement)
        size  (int)   – radius in pixels
        color (tuple) – RGB colour tuple
    """
    size = random.randint(12, 22)
    return {
        "x":     random.randint(size, WINDOW_WIDTH - size),
        "y":     float(-size),          # start just above the screen
        "size":  size,
        "color": random.choice(OBJECT_COLOURS),
    }

# ─────────────────────────────────────────
# HELPER — reset everything for a new game
# ─────────────────────────────────────────
def reset_game():
    """Return a fresh game_state dict, an empty objects list, and spawn timer."""
    return make_game_state(), [], 0

# ─────────────────────────────────────────
# DRAWING HELPERS
# ─────────────────────────────────────────
def draw_background():
    """Fill the window and draw a subtle gradient-like floor stripe."""
    screen.fill(DARK_BG)
    # Floor stripe
    pygame.draw.rect(screen, DARK_GRAY, (0, WINDOW_HEIGHT - 8, WINDOW_WIDTH, 8))

def draw_basket(x: int):
    """
    Draw a simple basket shape at the given x centre, fixed at BASKET_Y.
    Uses pygame.draw.rect and pygame.draw.arc for a bowl appearance.
    """
    bx = x - BASKET_WIDTH // 2
    by = BASKET_Y

    # Body of the basket
    pygame.draw.rect(screen, BASKET_COL, (bx, by, BASKET_WIDTH, BASKET_HEIGHT), border_radius=6)
    # Rim highlight
    pygame.draw.rect(screen, BASKET_RIM, (bx, by, BASKET_WIDTH, 5), border_radius=4)
    # Side legs
    pygame.draw.rect(screen, BASKET_COL, (bx + 5,       by + BASKET_HEIGHT, 8, 10), border_radius=3)
    pygame.draw.rect(screen, BASKET_COL, (bx + BASKET_WIDTH - 13, by + BASKET_HEIGHT, 8, 10), border_radius=3)

def draw_object(obj: dict):
    """Draw a single falling object as a filled circle with a bright outline."""
    cx = int(obj["x"])
    cy = int(obj["y"])
    r  = obj["size"]
    pygame.draw.circle(screen, obj["color"], (cx, cy), r)
    pygame.draw.circle(screen, WHITE,        (cx, cy), r, 2)

def draw_hud(gs: dict):
    """Render score, lives, and level at the top of the screen."""
    score_surf = font_medium.render(f"Score: {gs['score']}", True, SCORE_COL)
    lives_surf = font_medium.render(f"Lives: {gs['lives']}",  True, LIVES_COL)
    level_surf = font_medium.render(f"Level: {gs['level']}",  True, LEVEL_COL)

    screen.blit(score_surf, (10, 8))
    screen.blit(lives_surf, (WINDOW_WIDTH // 2 - lives_surf.get_width() // 2, 8))
    screen.blit(level_surf, (WINDOW_WIDTH - level_surf.get_width() - 10, 8))

    # Thin divider below HUD
    pygame.draw.line(screen, GRAY, (0, 38), (WINDOW_WIDTH, 38), 1)

def draw_game_over(gs: dict):
    """Overlay the game-over message on top of the last frame."""
    # Semi-transparent dark panel
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    go_surf  = font_large.render("GAME  OVER",          True, RED)
    sc_surf  = font_medium.render(f"Final Score: {gs['score']}  |  Level: {gs['level']}", True, WHITE)
    hint_r   = font_small.render("Press  R  to Restart", True, GREEN)
    hint_q   = font_small.render("Press  Q  to Quit",    True, LIVES_COL)

    cx = WINDOW_WIDTH  // 2
    cy = WINDOW_HEIGHT // 2

    screen.blit(go_surf,  (cx - go_surf.get_width()  // 2, cy - 80))
    screen.blit(sc_surf,  (cx - sc_surf.get_width()  // 2, cy - 20))
    screen.blit(hint_r,   (cx - hint_r.get_width()   // 2, cy + 40))
    screen.blit(hint_q,   (cx - hint_q.get_width()   // 2, cy + 70))

# ─────────────────────────────────────────
# LEVEL-UP CHECK
# ─────────────────────────────────────────
def check_level_up(gs: dict):
    """Increase level and fall_speed every 5 points."""
    new_level = gs["score"] // 5 + 1
    if new_level > gs["level"]:
        gs["level"]      = new_level
        gs["fall_speed"] = 2.5 + (new_level - 1) * 0.6   # speed grows with level

# ─────────────────────────────────────────
# COLLISION DETECTION
# ─────────────────────────────────────────
def check_collision(obj: dict, basket_x: int) -> bool:
    """
    COLLISION DETECTION using if statement:
    An object is 'caught' when its bottom edge overlaps vertically with the
    basket top, AND its horizontal centre is within the basket's width.

    Vertical check : object bottom  >= basket top  AND  object centre <= basket bottom
    Horizontal check: object centre is within [basket_left, basket_right]
    """
    obj_bottom   = obj["y"] + obj["size"]
    obj_cx       = obj["x"]

    basket_left  = basket_x - BASKET_WIDTH  // 2
    basket_right = basket_x + BASKET_WIDTH  // 2
    basket_top   = BASKET_Y
    basket_bot   = BASKET_Y + BASKET_HEIGHT

    # if the object is inside the basket rectangle → collision!
    if (obj_bottom >= basket_top and obj_bottom <= basket_bot + 10
            and obj_cx >= basket_left and obj_cx <= basket_right):
        return True

    return False

# ─────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────
def main():
    # ── Initialise game state ─────────────
    game_state, falling_objects, spawn_timer = reset_game()

    basket_x = WINDOW_WIDTH // 2    # horizontal centre of the basket

    running = True  # outer flag — set False only when the player quits entirely

    # ════════════════════════════════════════════════════════════════════════
    # GAME LOOP
    # The while loop runs once per frame (≈60 times per second).
    # Each iteration:
    #   1. Handle events  (keyboard / window close)
    #   2. Update state   (move objects, check collisions)
    #   3. Draw frame     (background, objects, basket, HUD)
    # ════════════════════════════════════════════════════════════════════════
    while running:

        # ── Δt in milliseconds since last frame ──
        dt = clock.tick(FPS)

        # ── 1. EVENT HANDLING ─────────────────────────────────────────────
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False

                if event.key == pygame.K_r and game_state["game_over"]:
                    # Restart: rebuild everything from scratch
                    game_state, falling_objects, spawn_timer = reset_game()
                    basket_x = WINDOW_WIDTH // 2

        # ── 2. UPDATE ─────────────────────────────────────────────────────
        if not game_state["game_over"]:

            # — Keyboard movement (held-down keys) ————————————————————————
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                basket_x -= BASKET_SPEED
            if keys[pygame.K_RIGHT]:
                basket_x += BASKET_SPEED

            # Keep basket fully inside the window
            half = BASKET_WIDTH // 2
            if basket_x - half < 0:
                basket_x = half
            if basket_x + half > WINDOW_WIDTH:
                basket_x = WINDOW_WIDTH - half

            # — Spawn new objects on a time interval ──────────────────────
            spawn_timer += dt
            if spawn_timer >= SPAWN_INTERVAL_MS:
                falling_objects.append(spawn_object())     # add to LIST
                spawn_timer = 0

            # — Move every object downward ────────────────────────────────
            # LIST iteration: for loop walks through every dict in the list
            for obj in falling_objects:
                obj["y"] += game_state["fall_speed"]

            # — Check catches and misses ──────────────────────────────────
            # We build a new list keeping only objects still in play.
            surviving = []
            for obj in falling_objects:

                # COLLISION DETECTION
                if check_collision(obj, basket_x):
                    # Object caught → award a point
                    game_state["score"] += 1
                    check_level_up(game_state)
                    # Object is NOT added to surviving → it disappears

                elif obj["y"] - obj["size"] > WINDOW_HEIGHT:
                    # Object fell past the bottom → lose a life
                    game_state["lives"] -= 1

                    # Check game-over condition
                    if game_state["lives"] <= 0:
                        game_state["lives"]     = 0
                        game_state["game_over"] = True   # bool flag set to True

                else:
                    # Object is still on screen and not caught → keep it
                    surviving.append(obj)

            falling_objects = surviving   # replace list with filtered version

        # ── 3. DRAW ───────────────────────────────────────────────────────
        draw_background()

        # Draw every falling object (for loop over the list)
        for obj in falling_objects:
            draw_object(obj)

        draw_basket(basket_x)
        draw_hud(game_state)

        if game_state["game_over"]:
            draw_game_over(game_state)

        pygame.display.flip()   # push the finished frame to the screen

    # ── Exit cleanly ──────────────────────────────────────────────────────
    pygame.quit()

# ─────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────
if __name__ == "__main__":
    main()       