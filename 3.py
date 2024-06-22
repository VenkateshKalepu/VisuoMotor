import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Visuomotor Task")

# Hide the mouse cursor
pygame.mouse.set_visible(False)

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)

# Circle parameters
start_circle_radius = 25
target_radius = 20
bullseye_radius = 15
distance = 200
center = (width // 2, height // 2)

# Generate target positions
angles = [i * 45 for i in range(8)]
targets = [(center[0] + distance * math.cos(math.radians(angle)),
            center[1] - distance * math.sin(math.radians(angle))) for angle in angles]

# Function to get joystick input
def get_joystick_position():
    # Check if there is any joystick available
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        # Get joystick position
        return (int(joystick.get_axis(0) * distance + center[0]), int(joystick.get_axis(1) * distance + center[1]))
    else:
        return center  # Return center if no joystick found

def draw_screen(target_index, neighboring_indices, cursor_pos):
    screen.fill(black)
    pygame.draw.circle(screen, blue, center, start_circle_radius)
    for i, (x, y) in enumerate(targets):
        if i == target_index:
            pygame.draw.circle(screen, red, (int(x), int(y)), target_radius)
            pygame.draw.circle(screen, white, (int(x), int(y)), bullseye_radius)
        elif i in neighboring_indices:
            pygame.draw.circle(screen, white, (int(x), int(y)), target_radius, 1)

    pygame.draw.circle(screen, green, cursor_pos, 10)
    pygame.display.flip()

# Main function
def visuomotor_task():
    clock = pygame.time.Clock()
    trial_count = 0
    max_trials = 20

    while trial_count < max_trials:
        screen.fill(black)

        # Draw start circle
        pygame.draw.circle(screen, blue, center, start_circle_radius)

        # Select target and neighboring targets
        target_index = random.randint(0, 7)
        neighboring_indices = [(target_index - 1) % 8, (target_index + 1) % 8]

        draw_screen(target_index, neighboring_indices, center)

        # Play tone (beep sound)
        # pygame.mixer.Sound('beep.wav').play()

        # Wait for the subject to click within the start circle
        waiting_for_start = True
        cursor_pos = list(center)
        movement_started = False


        # Movement phase
        movement_start_time = time.time()
        previous_pos = cursor_pos
        moving = False

        while not moving:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            cursor_pos = get_joystick_position()
            speed = math.hypot(cursor_pos[0] - previous_pos[0], cursor_pos[1] - previous_pos[1])
            previous_pos = cursor_pos

            if speed > 1:  # Threshold speed to start moving
                moving = True
                movement_start_time = time.time()

            draw_screen(target_index, neighboring_indices, cursor_pos)

        # Freeze cursor 100 ms after movement onse
        while moving:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            cursor_pos = get_joystick_position()

            draw_screen(target_index, neighboring_indices, cursor_pos)

            if time.time() - movement_start_time > 0.1:
                moving = False

        # Display white square at the movement reversal point
        draw_screen(target_index, neighboring_indices, cursor_pos)
        pygame.draw.rect(screen, white, (cursor_pos[0] - 5, cursor_pos[1] - 5, 10, 10))
        pygame.display.flip()

        # Wait for a brief moment before the next trial
        pygame.time.wait(1000)
        trial_count += 1

    pygame.quit()

# Run the task
visuomotor_task()
