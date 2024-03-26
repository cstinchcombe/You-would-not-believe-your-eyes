#!/usr/bin/env python
# coding: utf-8

# In[382]:


import pygame
import sys
import time
import subprocess


# Initialize Pygame
pygame.init()

# Initialize Pygame mixer
pygame.mixer.init(frequency=44100, size=-16, channels=1)


# Screen setup
screen_width, screen_height = 600, 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Ball Dropping')


# In[383]:


def interpolate_color(color_start, color_end, factor):
    """Interpolates between two colors with a given factor (0.0 to 1.0)."""
    red = color_start[0] + (color_end[0] - color_start[0]) * factor
    green = color_start[1] + (color_end[1] - color_start[1]) * factor
    blue = color_start[2] + (color_end[2] - color_start[2]) * factor
    return int(red), int(green), int(blue)


# Define a list of colors to cycle through
cycle_colors = [
    (255, 255, 224),  # Light Yellow
    (144, 238, 144),  # Light Green
    (255, 239, 213),  # Papaya Whip
    (224, 255, 255),  # Light Cyan
]

# Use current_glow_color for drawing the glow effect around the ball or circle


# In[384]:


def generate_tone(frequency, duration, volume=0.5, sample_rate=44100):
    # Generate the time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate the tone
    tone = np.sin(frequency * t * 2 * np.pi)
    
    # Apply volume
    tone *= volume * 32767 / np.max(np.abs(tone))
    
    # Apply a fade in and fade out
    fade_in_duration = int(sample_rate * 0.01)  # 0.01 seconds fade in
    fade_out_duration = int(sample_rate * 0.01)  # 0.01 seconds fade out
    
    # Ensure the fade durations are not longer than the tone itself
    fade_in_duration = min(fade_in_duration, len(tone) // 2)
    fade_out_duration = min(fade_out_duration, len(tone) // 2)
    
    # Apply fade in
    for i in range(fade_in_duration):
        tone[i] *= (i / fade_in_duration)
    
    # Apply fade out
    for i in range(fade_out_duration):
        tone[-i - 1] *= (i / fade_out_duration)
    
    # Convert to bytes
    tone = tone.astype(np.int16).tobytes()
    
    # Create and return the Pygame sound object
    return pygame.mixer.Sound(buffer=tone)


frequencies = [116.541, 233.082, 587.33, 116.541,233.082,466.16, 233.082,311.13, 
               155.563, 233.082, 349.23, 311.13, 349.23, 466.16, 349.23, 311.13, 
               103.826, 155.563, 261.626,233.082,261.626,311.13, 155.563,103.826,
               155.563, 207.652, 261.626,233.082,130.8,  233.082,311.13, 349.23
              ] #First 4 bars of Owl City - Fireflies



glow_colors = [
    (255, 255, 224),  # Light Yellow
    (255, 255, 153),  # Soft Yellow
    (255, 250, 205),  # Lemon Chiffon
    (240, 230, 140),  # Khaki
    (255, 239, 213),  # Papaya Whip
    (255, 255, 240),  # Ivory
    (224, 255, 255),  # Light Cyan, for a slightly different glow
    (144, 238, 144),  # Light Green, for a greenish glow
    (152, 251, 152),  # Pale Green, for subtle variations in the green glow
    (173, 255, 47),   # Green Yellow, for a vibrant glow
]

freq_index=0
colors_index =0


# In[ ]:


# Colors
screen_color = (0,0,0)     #black
color = circle_color = ball_color = (255,255,255)

# Ball setup
ball_radius = 10
ball_pos = [screen_width // 2, ball_radius]  # Start at the top middle of the screen
ball_velocity = [0.25,-0.25]  # Initial velocity
gravity = 0.5  # Acceleration due to gravity

# Circle setup
circle_center = (screen_width // 2, screen_height // 2)
circle_radius = screen_height//2


# Clock to control frame rate
clock = pygame.time.Clock()


# In[387]:


speed_increase_factor = 1.0075
glow_duration = 10  # Number of frames to display the glow effect
glowing = False  # Initial state of the glow effect

# Initialize variables for color cycling
current_color_index = 0
transition_duration = 5  # Duration of each transition in seconds
start_time = time.time()

contact_points = []

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Physics: Update ball velocity and position
    ball_velocity[1] += gravity
    ball_pos[1] += ball_velocity[1]
    ball_pos[0] += ball_velocity[0]
    
    # Calculate distance from ball to the center of the circle
    dx = ball_pos[0] - circle_center[0]
    dy = ball_pos[1] - circle_center[1]
    dist_to_center = math.sqrt(dx**2 + dy**2)
    
    # Prevent the ball from falling off the screen
    if dist_to_center + ball_radius >= circle_radius:
        # Calculate normal vector at the collision point
        nx = dx / dist_to_center
        ny = dy / dist_to_center
        
        # Reflect the ball's velocity
        dot = ball_velocity[0] * nx + ball_velocity[1] * ny
        ball_velocity[0] -= 2 * dot * nx
        ball_velocity[1] -= 2 * dot * ny
        
        # Increase speed after bounce
        ball_velocity[0] *= speed_increase_factor
        ball_velocity[1] *= speed_increase_factor
        
        # Correct ball position to prevent it from getting stuck
        overlap = dist_to_center + ball_radius - circle_radius
        ball_pos[0] -= overlap * nx
        ball_pos[1] -= overlap * ny
        
        # Play tone
        frequency=frequencies[freq_index]
        tone = generate_tone(frequency, duration=0.25, volume=0.5, sample_rate=44100)
        tone.play()
        pygame.time.wait(int(0.25 * 30))
        freq_index = (freq_index + 1) % len(frequencies)  # Loop back to the start of the list
        
        
        # Add contact point to contact_points(list)
        # Normalize the direction vector from circle center to ball position
        direction_norm = (dx / dist_to_center, dy / dist_to_center)
        # Scale by the circle's radius to find the point on the circle
        contact_point = (circle_center[0] + direction_norm[0] * circle_radius, 
                         circle_center[1] + direction_norm[1] * circle_radius)
        contact_points.append(contact_point)


    
    # Transition colors
    elapsed_time = time.time() - start_time
    # Calculate the current position in the color cycle
    cycle_position = (elapsed_time / transition_duration) % len(cycle_colors)

    # Determine the current and next color indices
    current_color_index = int(cycle_position)
    next_color_index = (current_color_index + 1) % len(cycle_colors)

    # Calculate the interpolation factor
    factor = cycle_position - current_color_index

    # Interpolate to get the current color
    current_glow_color = interpolate_color(cycle_colors[current_color_index], cycle_colors[next_color_index], factor)
    color = ball_color=circle_color=current_glow_color
    
    screen.fill(screen_color)

    
    # Draw lines from contact points to the ball
    for point in contact_points:
        pygame.draw.line(screen, color, point, ball_pos, 1)
    # Draw the circle with a glow effect
    pygame.draw.circle(screen, circle_color, circle_center, circle_radius, 5)

    # Finally, draw the ball on top
    pygame.draw.circle(screen, ball_color, ball_pos, ball_radius)
       

    

        
    
    # Update the display
    pygame.display.flip()
    
    # Capture the screen buffer directly from Pygame and write it to the FFmpeg process

    
    # Cap the frame rate to 60 frames per second
    clock.tick(60)



pygame.quit()
sys.exit()


# In[ ]:




