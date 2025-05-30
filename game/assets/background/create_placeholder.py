import pygame
import os

def create_placeholder_image():
    # Periksa apakah gambar cutscene sudah ada
    if not os.path.exists("game/assets/background/cutscene_ruangan1.png"):
        # Buat gambar placeholder
        width, height = 1000, 800
        image = pygame.Surface((width, height))
        
        # Isi dengan latar belakang biru gelap
        image.fill((20, 30, 50))
        
        # Gambar beberapa elemen dekoratif
        pygame.draw.rect(image, (40, 60, 100), (50, 50, width-100, height-100), 5)
        pygame.draw.rect(image, (60, 90, 150), (100, 100, width-200, height-200), 3)
        
        # Tambahkan teks
        font = pygame.font.SysFont(None, 48)
        text = font.render("Cutscene Ruangan 1", True, (200, 200, 255))
        text_rect = text.get_rect(center=(width//2, height//2))
        image.blit(text, text_rect)
        
        # Simpan gambar
        pygame.image.save(image, "game/assets/background/cutscene_ruangan1.png")
        print("Berhasil membuat gambar cutscene placeholder")

if __name__ == "__main__":
    pygame.init()
    create_placeholder_image()
    pygame.quit()
