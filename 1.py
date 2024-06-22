import pygame
import random
import math
import time
import matplotlib.pyplot as plt

# Initialize Pygame1
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
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        return (int(joystick.get_axis(0) * distance + center[0]), int(joystick.get_axis(1) * distance + center[1]))
    else:
        return center

def apply_rotation(pos, angle):
    angle_rad = math.radians(angle)
    x, y = pos
    x -= center[0]
    y -= center[1]
    rotated_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
    rotated_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)
    return (rotated_x + center[0], rotated_y + center[1])

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

def calculate_directional_error(target_pos, reversal_pos):
    target_vector = (target_pos[0] - center[0], target_pos[1] - center[1])
    reversal_vector = (reversal_pos[0] - center[0], reversal_pos[1] - center[1])
    target_angle = math.atan2(target_vector[1], target_vector[0])
    reversal_angle = math.atan2(reversal_vector[1], reversal_vector[0])
    error = math.degrees(abs(target_angle - reversal_angle))
    return error

def visuomotor_task():
    clock = pygame.time.Clock()
    trial_count = 0
    max_trials = [20, 60, 20]
    blocks = [1, 2, 3]
    block_index = 0
    rotation_angle = -45  # Counterclockwise rotation

    errors = []

    while block_index < len(blocks):
        block_type = blocks[block_index]
        print(block_type)

        while trial_count < max_trials[block_type-1]:
            screen.fill(black)
            pygame.draw.circle(screen, blue, center, start_circle_radius)
            target_index = random.randint(0, 7)
            neighboring_indices = [(target_index - 1) % 8, (target_index + 1) % 8]

            draw_screen(target_index, neighboring_indices, center)

            waiting_for_start = True
            cursor_pos = list(center)
            movement_started = False

            movement_start_time = time.time()
            previous_pos = cursor_pos
            moving = False

            while not moving:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return

                cursor_pos = get_joystick_position()
                if block_type == 2:
                    cursor_pos = apply_rotation(cursor_pos, rotation_angle)
                speed = math.hypot(cursor_pos[0] - previous_pos[0], cursor_pos[1] - previous_pos[1])
                previous_pos = cursor_pos

                if speed > 1:
                    moving = True
                    movement_start_time = time.time()

                draw_screen(target_index, neighboring_indices, cursor_pos)

            while moving:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return

                cursor_pos = get_joystick_position()

                if block_type == 2:
                    cursor_pos = apply_rotation(cursor_pos, rotation_angle)

                draw_screen(target_index, neighboring_indices, cursor_pos)

                if time.time() - movement_start_time > 0.1:
                    moving = False

            draw_screen(target_index, neighboring_indices, cursor_pos)
            pygame.draw.rect(screen, white, (cursor_pos[0] - 5, cursor_pos[1] - 5, 10, 10))
            pygame.display.flip()

            error = calculate_directional_error(targets[target_index], cursor_pos)
            errors.append((block_type, trial_count + 1, error))

            pygame.time.wait(1500)
            trial_count += 1

        trial_count = 0
        block_index += 1

    pygame.quit()

    # Plot the errors
    baseline_errors = [e[2] for e in errors if e[0] == 1]
    rotation_errors = [e[2] for e in errors if e[0] == 2]
    aftereffect_errors = [e[2] for e in errors if e[0] == 3]

    plt.figure(figsize=(10, 6))
    plt.plot(range(1, max_trials[0] + 1), baseline_errors, label='Baseline')
    plt.plot(range(1, max_trials[1] + 1), rotation_errors, label='Rotation')
    plt.plot(range(1, max_trials[2] + 1), aftereffect_errors, label='Aftereffect')
    plt.xlabel('Trial Number')
    plt.ylabel('Directional Error (degrees)')
    plt.title('Directional Error Across Trials')
    plt.legend()
    plt.grid(True)
    plt.show()

# Run the task
visuomotor_task()
