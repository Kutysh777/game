import pygame
import random

# start pygame
pygame.init()

# screen size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# colors (tuples with RGB values)
WHITE  = (255, 255, 255)
BLACK  = (  0,   0,   0)
RED    = (220,  50,  50)
GREEN  = ( 50, 180,  50)
BLUE   = ( 50, 100, 220)
YELLOW = (240, 200,  50)
ORANGE = (255, 140,   0)
PURPLE = (160,  80, 220)

# list of colors that objects can have
COLORS = [RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE]

# game state dictionary - stores all important game info
game_state = {
    "score": 0,
    "lives": 3,
    "level": 1,
    "game_over": False,
    "fall_speed": 3
}

# basket settings
basket_width  = 120
basket_height = 20
basket_x      = SCREEN_WIDTH // 2 - basket_width // 2
basket_y      = SCREEN_HEIGHT - 50
basket_speed  = 8

# list to store all falling objects
falling_objects = []

# setup screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Catch the Falling Objects")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 50, bold=True)

# frame counter for spawning
frame_count = 0
spawn_rate  = 30


# function to create a new falling object
# returns a dictionary with x, y, color, size
def create_object():
    size  = random.randint(12, 20)
    x     = random.randint(size, SCREEN_WIDTH - size)
    color = random.choice(COLORS)
    # every new object starts at the top of the screen
    return {"x": x, "y": 0, "color": color, "size": size}


# function to reset everything when player restarts
def reset_game():
    global basket_x, frame_count, falling_objects

    # reset all values in the dictionary
    game_state["score"]      = 0
    game_state["lives"]      = 3
    game_state["level"]      = 1
    game_state["game_over"]  = False
    game_state["fall_speed"] = 3

    # clear the list and put basket back to center
    falling_objects = []
    basket_x        = SCREEN_WIDTH // 2 - basket_width // 2
    frame_count     = 0


# main game loop
running = True

while running:

    clock.tick(60)  # 60 frames per second

    # --- handle events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # keyboard press events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            # press R to restart after game over
            if event.key == pygame.K_r and game_state["game_over"]:
                reset_game()

    # --- update (only if game is not over) ---
    if not game_state["game_over"]:

        # move basket left or right with arrow keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            basket_x -= basket_speed
        if keys[pygame.K_RIGHT]:
            basket_x += basket_speed

        # make sure basket doesnt go outside the screen
        if basket_x < 0:
            basket_x = 0
        if basket_x + basket_width > SCREEN_WIDTH:
            basket_x = SCREEN_WIDTH - basket_width

        # spawn a new object every spawn_rate frames
        frame_count += 1
        if frame_count % spawn_rate == 0:
            falling_objects.append(create_object())

        # move all objects down using a for loop
        for obj in falling_objects:
            obj["y"] += game_state["fall_speed"]

        # check collisions - build a new list of objects to keep
        # i dont remove from list while looping, that can break things
        keep = []

        for obj in falling_objects:
            obj_bottom = obj["y"] + obj["size"]
            obj_center = obj["x"]

            # collision detection using if statement
            # object is caught if it hits the basket area
            if (obj_bottom >= basket_y
                    and obj_bottom <= basket_y + basket_height + 10
                    and obj_center >= basket_x
                    and obj_center <= basket_x + basket_width):

                # player caught the object, add score
                game_state["score"] += 1

                # increase level and speed every 5 points
                if game_state["score"] % 5 == 0:
                    game_state["level"]      += 1
                    game_state["fall_speed"] += 0.6

            elif obj_bottom > SCREEN_HEIGHT:
                # object reached the bottom without being caught
                game_state["lives"] -= 1

                # check if player has no lives left
                if game_state["lives"] <= 0:
                    game_state["lives"]     = 0
                    game_state["game_over"] = True

            else:
                # object is still falling, keep it in the list
                keep.append(obj)

        # update the list with only surviving objects
        falling_objects = keep

    # --- draw everything ---
    screen.fill(BLACK)

    # draw all falling objects using for loop
    for obj in falling_objects:
        pygame.draw.circle(screen, obj["color"], (int(obj["x"]), int(obj["y"])), obj["size"])
        pygame.draw.circle(screen, WHITE,        (int(obj["x"]), int(obj["y"])), obj["size"], 2)

    # draw the basket (player)
    pygame.draw.rect(screen, BLUE, (basket_x, basket_y, basket_width, basket_height), border_radius=5)

    # show score, lives and level on screen
    score_text = font.render("Score: " + str(game_state["score"]), True, WHITE)
    lives_text = font.render("Lives: " + str(game_state["lives"]), True, RED)
    level_text = font.render("Level: " + str(game_state["level"]), True, YELLOW)

    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (SCREEN_WIDTH // 2 - 60, 10))
    screen.blit(level_text, (SCREEN_WIDTH - 150, 10))

    # show game over screen when lives = 0
    if game_state["game_over"]:
        over_text   = big_font.render("GAME OVER", True, RED)
        score_text2 = font.render("Your score: " + str(game_state["score"]), True, WHITE)
        hint_r      = font.render("Press R to restart", True, GREEN)
        hint_q      = font.render("Press Q to quit",    True, WHITE)

        screen.blit(over_text,   (SCREEN_WIDTH // 2 - over_text.get_width()   // 2, 200))
        screen.blit(score_text2, (SCREEN_WIDTH // 2 - score_text2.get_width() // 2, 270))
        screen.blit(hint_r,      (SCREEN_WIDTH // 2 - hint_r.get_width()      // 2, 330))
        screen.blit(hint_q,      (SCREEN_WIDTH // 2 - hint_q.get_width()      // 2, 370))

    # update the display
    pygame.display.flip()

# quit pygame when loop ends
pygame.quit()
