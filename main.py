import pygame
import sys
from game.menu import main_menu
from game.maps.gameplay import run_gameplay
from game.cutscenes.intro_mission import run_cutscene_intro_mission

if __name__ == "__main__":
    pygame.init()
    
    # Inisialisasi mixer untuk suara
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    
    main_menu()  # Panggil menu utama
    # Atau bisa langsung panggil run_gameplay() untuk testing
    # run_gameplay()
    pygame.quit()
    sys.exit()
