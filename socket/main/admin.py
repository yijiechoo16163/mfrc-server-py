import pygame
import socket

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 600
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')

# Create the input box
input_box = pygame.Rect(100, 100, 140, 32)

# Set up some variables
color = color_inactive
text = ''
active = False
font = pygame.font.Font(None, 32)

# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Create the socket
client_socket = socket.socket()
client_socket.connect(("192.168.100.20", 5000))

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = not active
            else:
                active = False
            color = color_active if active else color_inactive
        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    client_socket.send(text.encode())
                    text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

    screen.fill((30, 30, 30))
    txt_surface = font.render(text, True, color)
    screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
    pygame.draw.rect(screen, color, input_box, 2)
    pygame.display.flip()

pygame.quit()