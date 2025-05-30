import pygame
import sys
from game.game_manager import GameManager
from game.assets.background.create_placeholder import create_placeholder_image
from game.assets.sound.create_placeholder_sounds import create_placeholder_menu_music, create_placeholder_alert_sound, create_placeholder_game_music
from game.cutscenes.room1_intro import run_cutscene_room1

def show_loading_screen(screen, text="Please Wait..."):
    """Menampilkan layar loading dengan teks yang diberikan"""
    # Setup font
    font = pygame.font.SysFont(None, 48)
    
    # Bersihkan layar dengan warna hitam
    screen.fill((0, 0, 0))
    
    # Render teks
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    
    # Tampilkan teks
    screen.blit(text_surface, text_rect)
    
    # Tambahkan teks loading kecil yang berkedip
    small_font = pygame.font.SysFont(None, 24)
    loading_text = small_font.render("Loading assets...", True, (200, 200, 200))
    loading_rect = loading_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
    screen.blit(loading_text, loading_rect)
    
    # Update layar
    pygame.display.flip()

def run_gameplay():
    """
    Fungsi ini dipanggil dari menu.py untuk memulai gameplay.
    Fungsi ini membuat instance GameManager dan menjalankannya.
    """
    # Setup layar untuk loading screen
    screen = pygame.display.set_mode((1000, 800))
    pygame.display.set_caption("Whitehouse Heist - Loading")
    
    # Tampilkan layar loading
    show_loading_screen(screen, "Mempersiapkan Permainan...")
    
    # Buat gambar dan suara placeholder jika belum ada
    create_placeholder_image()
    create_placeholder_menu_music()
    create_placeholder_alert_sound()
    create_placeholder_game_music()
    
    # Tampilkan pesan loading lagi dengan pesan berbeda
    show_loading_screen(screen, "Memuat Aset Game...")
    
    # Beri waktu untuk loading (simulasi)
    pygame.time.delay(500)  # Delay 500ms untuk simulasi loading
    
    # Tampilkan cutscene room1 sebelum memulai gameplay
    run_cutscene_room1()
    
    # Buat dan jalankan game manager
    game_manager = GameManager()
    game_manager.run()
