import pygame
from PIL import Image, ImageSequence

# Charger le GIF avec Pillow
gif_path = "../asset/GIF/Cactus.gif"
img = Image.open(gif_path)

# Extraire toutes les frames
frames = [pygame.image.fromstring(frame.convert("RGBA").tobytes(), frame.size, "RGBA")
          for frame in ImageSequence.Iterator(img)]

# Initialisation de Pygame
pygame.init()

# Définir la taille de la fenêtre en fonction du GIF
screen = pygame.display.set_mode(img.size)
clock = pygame.time.Clock()

running = True
frame_index = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Afficher la frame actuelle
    screen.blit(frames[frame_index], (0, 0))
    pygame.display.flip()

    # On efface l'écran poour éviter la superposition de frames
    screen.fill((0,0,0))

    # Passer à la frame suivante
    frame_index = (frame_index + 1) % len(frames)

    # Définir la vitesse d'animation (ajustez selon le GIF)
    clock.tick(10)  # 10 FPS

pygame.quit()