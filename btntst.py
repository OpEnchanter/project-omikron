import pygame

pygame.init()
pygame.joystick.init()

joy = pygame.joystick.Joystick(0)

win = pygame.display.set_mode((500,500))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.JOYBUTTONDOWN:
            print(event.button)
pygame.quit()