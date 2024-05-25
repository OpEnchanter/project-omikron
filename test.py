import pygame
import sys
import math
from pygame.locals import *

pygame.init()

# Set up the display
WIDTH, HEIGHT = 400, 400
CENTER = (WIDTH // 2, HEIGHT // 2)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rotate Surface")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Create a surface
surface = pygame.Surface((100, 100), pygame.SRCALPHA)
surface.fill(WHITE)
rect = surface.get_rect(center=CENTER)

# Main loop
angle = 0
clock = pygame.time.Clock()
while True:
    mx, my = pygame.mouse.get_pos()
    vx = mx - CENTER[0]
    vy = my - CENTER[1]
    
    angle_rad = math.atan2(vy, vx)
    # Convert radians to degrees
    angle_deg = math.degrees(angle_rad)
    # Adjust angle to be within the range [0, 360)
    angle_deg = (angle_deg + 360) % 360

    screen.fill(BLACK)
    
    # Rotate the surface
    rotated_surface = pygame.transform.rotate(surface, -angle_deg)
    rotated_rect = rotated_surface.get_rect(center=rect.center)
    
    # Draw the rotated surface to the screen
    screen.blit(rotated_surface, rotated_rect.topleft)
    
    # Draw the original surface (just for reference)
    pygame.draw.rect(screen, WHITE, rect, 2)
    
    pygame.display.flip()
    
    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
    # Increment angle
    angle += 1
    if angle >= 360:
        angle = 0
    
    clock.tick(60)
