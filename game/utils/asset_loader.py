import pygame

def load_and_transform(path, size=None, flip_x=False, flip_y=False, rotate_angle=0):
    image = pygame.image.load(path).convert_alpha()
    if size:
        image = pygame.transform.smoothscale(image, size)
    if flip_x or flip_y:
        image = pygame.transform.flip(image, flip_x, flip_y)
    if rotate_angle != 0:
        image = pygame.transform.rotate(image, rotate_angle)
    return image

def get_frames(sheet, row, count, frame_width, frame_height, scale=2):
    frames = []
    for i in range(count):
        frame = sheet.subsurface(pygame.Rect(i * frame_width, row * frame_height, frame_width, frame_height))
        frame = pygame.transform.scale(frame, (frame_width * scale, frame_height * scale))
        frames.append(frame)
    return frames
