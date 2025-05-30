import pygame
import random
import math
from game.utils.constants import *
from game.utils.asset_loader import load_and_transform, get_frames
from game.maps.base_room import BaseRoom, HidingSpot, CollectibleItem
from game.entities.laser import Laser

class Room2(BaseRoom):
    def load_assets(self):
        # Load tiles (same as Room1 or can be different)
        self.tiles = {
            0: load_and_transform("game/assets/ruangan2/walls/floor.png", (TILE_SIZE, TILE_SIZE)),
            1: load_and_transform("game/assets/ruangan2/walls/wall-kiri-kanan.png", (TILE_SIZE, TILE_SIZE)),
            2: load_and_transform("game/assets/ruangan2/walls/wall-atas-bawah.png", (TILE_SIZE, TILE_SIZE)),
            7: load_and_transform("game/assets/objects/pintu/tiang.png", (TILE_SIZE, TILE_SIZE)),
            96: load_and_transform("game/assets/ruangan2/walls/wall-kiri-atas.png", (int(TILE_SIZE * 3.4), int(TILE_SIZE * 3.4))),
            97: load_and_transform("game/assets/ruangan2/walls/wall-sudut.png", (TILE_SIZE, TILE_SIZE), flip_x=True),
            98: load_and_transform("game/assets/ruangan2/walls/wall-sudut.png", (TILE_SIZE, TILE_SIZE), rotate_angle=90),
            99: load_and_transform("game/assets/ruangan2/walls/wall-sudut.png", (TILE_SIZE, TILE_SIZE), rotate_angle=180),
            100: pygame.Surface((TILE_SIZE, TILE_SIZE))
        }

        # Load objects (same as Room1 or can be different)
        self.objects = {
            "tanaman": load_and_transform("game/assets/ruangan1/objects/tanaman.png", (TILE_SIZE, TILE_SIZE)),
            "tanaman2": load_and_transform("game/assets/ruangan1/objects/tanaman2.png", (TILE_SIZE, TILE_SIZE)),
            "sofa": load_and_transform("game/assets/ruangan1/objects/sofa.png", (TILE_SIZE, TILE_SIZE)),
           
        }
        
        # Inisialisasi variabel pencahayaan
        self.light_radius = 150  # Radius cahaya di sekitar player
        self.ambient_light = 80  # Tingkat cahaya ambient (0-255, 0 = gelap total)
        
        # Buat surface untuk efek pencahayaan
        self.light_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    def setup_room(self):
        # Setup tilemap (different layout for room 2)
        self.tilemap = [
            [96,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,97],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [98,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,99]
        ]
        
        # Tilemap with door at bottom (for exiting room 2)
        self.tilemap_with_door = [
            [96,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,97],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [98,2,2,2,2,2,2,2,7,0,7,2,2,2,2,2,2,2,2,99]
        ]
        
        # Setup object positions (different layout for room 2)
        self.object_positions = [
            {"img": self.objects["tanaman"], "x": 15, "y": 1},
            {"img": self.objects["tanaman2"], "x": 13, "y": 10},
            {"img": self.objects["sofa"], "x": 3, "y": 1},
            {"img": self.objects["sofa"], "x": 4, "y": 1},
        ]
        
        # Setup colliders
        self.colliders = []
        for obj in self.object_positions:
            img = obj["img"]
            rect = img.get_rect()
            rect.topleft = (obj["x"] * TILE_SIZE, obj["y"] * TILE_SIZE)
            self.colliders.append(rect)
        
        # Add colliders for wall tiles
        solid_tile_ids = [1, 2, 7, 96, 97, 98, 99]
        for y, row in enumerate(self.tilemap):
            for x, tile_id in enumerate(row):
                if tile_id in solid_tile_ids:
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    self.colliders.append(rect)
        
        # Setup hiding spots
        self.hiding_spots = [
            HidingSpot(pygame.Rect(15 * TILE_SIZE - 10, 1 * TILE_SIZE - 10, TILE_SIZE + 20, TILE_SIZE + 20), "tanaman1"),
            HidingSpot(pygame.Rect(13 * TILE_SIZE - 10, 10 * TILE_SIZE - 10, TILE_SIZE + 20, TILE_SIZE + 20), "tanaman2"),
        ]
        
        # Setup patrol routes
        patrol_routes = [
            [(5, 3), (5, 8), (15, 8), (15, 3)],
            [(10, 2), (10, 9), (10, 9), (10, 2)],
            [(2,2),(10,5), (10,2), (2,2)]
        ]
        
        # Setup guards
        from game.entities.guard import Guard
        
        guard_types = {
            "ranger": {
                "sprite_sheet": pygame.image.load("game/assets/guard_img/rangerr.png").convert_alpha(),
                "speed": GUARD_SPEED,
                "vision_range": 300,
                "color": (5, 165, 245)
            },
            "aristocrate": {
                "sprite_sheet": pygame.image.load("game/assets/guard_img/aristocrate.png").convert_alpha(),
                "speed": GUARD_SPEED * 1.2,
                "vision_range": 250,
                "color": (5, 245, 157)
            },
            "kakek": {
                "sprite_sheet": pygame.image.load("game/assets/guard_img/kakek1.png").convert_alpha(),
                "speed": GUARD_SPEED * 0.5,
                "vision_range": 120,
                "color": (84, 92, 85)
            }
        }
        
        # Generate frames for each guard type
        guard_frames = {}
        for guard_type, data in guard_types.items():
            guard_frames[guard_type] = {
                'down': get_frames(data["sprite_sheet"], 2, 3, 24, 32),
                'left': get_frames(data["sprite_sheet"], 3, 3, 24, 32),
                'right': get_frames(data["sprite_sheet"], 1, 3, 24, 32),
                'up': get_frames(data["sprite_sheet"], 0, 3, 24, 32)
            }
        
        self.guards = [
            Guard(5 * TILE_SIZE, 3 * TILE_SIZE, "ranger", patrol_routes[0], guard_frames["ranger"], guard_types["ranger"], self.colliders),
            Guard(10 * TILE_SIZE, 2 * TILE_SIZE, "aristocrate", patrol_routes[1], guard_frames["aristocrate"], guard_types["aristocrate"], self.colliders),
            Guard(2 * TILE_SIZE, 2 * TILE_SIZE, "kakek", patrol_routes[2], guard_frames["kakek"], guard_types["kakek"], self.colliders)
        ]
        
        # Setup collectible items
        self.setup_collectible_items()
        
        # Setup laser traps
        self.lasers = [
            Laser(4 * TILE_SIZE, 3 * TILE_SIZE, 8 * TILE_SIZE, 3 * TILE_SIZE, color=(255, 0, 0), thickness=2),
            Laser(12 * TILE_SIZE, 3 * TILE_SIZE, 16 * TILE_SIZE, 3 * TILE_SIZE, color=(255, 0, 0), thickness=2),
            Laser(8 * TILE_SIZE, 8 * TILE_SIZE, 12 * TILE_SIZE, 8 * TILE_SIZE, color=(255, 0, 0), thickness=2),
            Laser(4 * TILE_SIZE, 9 * TILE_SIZE, 4 * TILE_SIZE, 5 * TILE_SIZE, color=(255, 0, 0), thickness=2),
            Laser(16 * TILE_SIZE, 9 * TILE_SIZE, 16 * TILE_SIZE, 5 * TILE_SIZE, color=(255, 0, 0), thickness=2)
        ]
        
        # Variabel untuk alarm
        self.alarm_triggered = False
        self.alarm_timer = 0
        self.alarm_duration = 5000  # 5 detik
        self.alarm_sound_played = False
        self.alarm_sound = None
        self.alarm_sound_channel = None  # Track the sound channel
        try:
            self.alarm_sound = pygame.mixer.Sound("game/assets/sound/alert.wav")
            self.alarm_sound.set_volume(0.7)
        except pygame.error as e:
            print(f"Tidak dapat memuat file suara alarm: {e}")
    
    def setup_collectible_items(self):
        # Same as Room1, but with different positions
        valid_item_positions = []
        for x in range(1, MAP_WIDTH - 1):
            for y in range(1, MAP_HEIGHT - 1):
                test_rect = pygame.Rect(x * TILE_SIZE + TILE_SIZE//4, y * TILE_SIZE + TILE_SIZE//4, 
                                       TILE_SIZE//2, TILE_SIZE//2)
                
                if not any(test_rect.colliderect(c) for c in self.colliders):
                    valid_item_positions.append((x * TILE_SIZE + TILE_SIZE//4, y * TILE_SIZE + TILE_SIZE//4))
        
        random.shuffle(valid_item_positions)
        num_items = min(15, len(valid_item_positions))
        
        item_shapes = ["circle", "square", "diamond", "triangle", "star"]
        item_colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 165, 0),  # Orange
            (128, 0, 128)   # Purple
        ]
        
        for i in range(num_items):
            x, y = valid_item_positions[i]
            shape = random.choice(item_shapes)
            color = random.choice(item_colors)
            value = 30 if shape == "star" else 20 if shape == "diamond" else 10
            
            self.collectible_items.append(CollectibleItem(x, y, "regular", shape, color, value))
    
    def spawn_key(self):
        key_x = SCREEN_WIDTH // 2 - 8
        key_y = SCREEN_HEIGHT // 2 - 8
        
        key_item = CollectibleItem(key_x, key_y, "key", "star", (255, 215, 0), 50)
        key_item.width = 24
        key_item.height = 24
        self.collectible_items.append(key_item)
        
        self.add_collection_effect(key_x + 12, key_y + 12, (255, 215, 0))
    
    def open_door(self):
        # Replace tilemap with version that has open door
        self.tilemap = self.tilemap_with_door
        
        # Remove collider for door
        self.colliders = [c for c in self.colliders if not (c.left == 9 * TILE_SIZE and c.top == 11 * TILE_SIZE)]
    
    def update(self, dt, mouse_held, mouse_pos):
        # Update base room elements
        super().update(dt, mouse_held, mouse_pos)
        
        # Update lasers
        laser_triggered = False
        for laser in self.lasers:
            if laser.update(dt, self.player):
                laser_triggered = True
        
        # Jika laser dipicu dan alarm belum aktif, aktifkan alarm
        if laser_triggered and not self.alarm_triggered:
            self.alarm_triggered = True
            self.alarm_timer = 0
            self.alarm_sound_played = False
        
            # Buat semua guard mengejar player
            for guard in self.guards:
                guard.state = "chase"
                guard.alert_level = 100
                guard.last_known_player_pos = (self.player.x + self.player.width // 2, 
                                              self.player.y + self.player.height // 2)
            
            # Tampilkan emote alert
            guard.show_emote = True
            guard.emote_type = "alert"
            guard.emote_timer = 0
    
        # Update alarm timer
        if self.alarm_triggered:
            # Mainkan suara alarm jika belum diputar
            if not self.alarm_sound_played and self.alarm_sound:
                # Hentikan suara alarm sebelumnya jika masih diputar
                pygame.mixer.stop()
                self.alarm_sound_channel = self.alarm_sound.play()
                self.alarm_sound_played = True
        
            self.alarm_timer += dt
            if self.alarm_timer >= self.alarm_duration:
                self.alarm_triggered = False
                # Hentikan suara alarm
                if self.alarm_sound_played:
                    pygame.mixer.stop()
                    self.alarm_sound_played = False
            
                # Cek apakah player masih terlihat oleh guard
                player_visible = False
                for guard in self.guards:
                    if guard.can_see_player(self.player):
                        player_visible = True
                        break
            
                # Jika player tidak terlihat, kembalikan guard ke patroli
                if not player_visible:
                    for guard in self.guards:
                        if guard.state == "chase":
                            guard.state = "return"
                            guard.find_closest_patrol_point()
    
        # Cek jika player berhasil sembunyi atau kabur dari guard
        if self.alarm_triggered and self.player_is_hidden:
            # Jika player berhasil sembunyi, hentikan alarm
            if self.alarm_sound_played:
                pygame.mixer.stop()
                self.alarm_sound_played = False
        
            # Jangan langsung matikan alarm, biarkan timer berjalan
            # tapi suara alarm dihentikan
    
    def check_room_transition(self):
        # Check if player is at exit door (left side of room) - lebih ketat
        if (self.player.x < TILE_SIZE // 2 and  # Harus sangat dekat dengan tepi kiri
            self.player.y > 4.5 * TILE_SIZE and self.player.y < 6.5 * TILE_SIZE):  # Area pintu lebih sempit
            # Transition back to room 1
            self.game_manager.transition_to_room(0)
            
            # Position player at exit door of room 1
            self.player.x = SCREEN_WIDTH - TILE_SIZE * 2
            self.player.y = 5 * TILE_SIZE
        
        # Check if player is at bottom exit door (if door is open) - lebih ketat
        if (self.door_opened and 
            self.player.y > SCREEN_HEIGHT - TILE_SIZE // 2 and  # Harus sangat dekat dengan tepi bawah
            self.player.x > 8.5 * TILE_SIZE and self.player.x < 10.5 * TILE_SIZE):  # Area pintu lebih sempit
            # Transition to room 3 (if exists)
            if len(self.game_manager.rooms) > 2:
                self.game_manager.transition_to_room(2)
            else:
                # Game completed if no more rooms
                self.game_manager.game_completed = True
    
    def draw(self):
        # Gambar latar belakang dan objek dasar
        self.draw_tilemap()
        self.draw_objects()
        self.draw_items()
        
        # Gambar laser
        for laser in self.lasers:
            laser.draw(self.screen)
        
        # Gambar guard
        for guard in self.guards:
            guard.draw(self.screen)
        
        # Gambar player (hanya jika tidak bersembunyi)
        if not self.player_is_hidden:
            self.player.draw(self.screen)
            self.player.draw_stamina_bar(self.screen)
        
        # Gambar efek koleksi
        self.draw_collection_effects()
        
        # Gambar notifikasi
        self.draw_notifications()
        
        # Gambar indikator bersembunyi jika player sedang bersembunyi
        if self.player_is_hidden and self.current_hiding_spot:
            self.draw_hiding_indicator()
        
        # Gambar skor
        score_text = self.font.render(f"Score: {self.game_manager.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Gambar info debug jika diaktifkan
        if self.show_debug:
            self.draw_debug_info()
        
        # Terapkan efek pencahayaan
        self.apply_lighting_effect()
        
        # Gambar efek alarm jika aktif
        if self.alarm_triggered:
            self.draw_alarm_effect()
    
    def apply_lighting_effect(self):
        # Buat surface untuk efek pencahayaan
        self.light_surface.fill((0, 0, 0, 255 - self.ambient_light))
        
        # Buat lingkaran cahaya di sekitar player jika tidak bersembunyi
        if not self.player_is_hidden:
            player_center_x = int(self.player.x + self.player.width // 2)
            player_center_y = int(self.player.y + self.player.height // 2)
            
            # Buat gradient cahaya
            for radius in range(self.light_radius, 0, -1):
                alpha = int(255 * (1 - radius / self.light_radius))
                pygame.draw.circle(self.light_surface, (0, 0, 0, alpha), 
                                  (player_center_x, player_center_y), radius, 1)
        
        # Terapkan efek pencahayaan ke layar
        self.screen.blit(self.light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    
    def draw_alarm_effect(self):
        # Buat efek kedip merah untuk alarm
        if (self.alarm_timer // 200) % 2 == 0:  # Kedip setiap 200ms
            alarm_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alarm_surface.fill((255, 0, 0, 30))  # Merah transparan
            self.screen.blit(alarm_surface, (0, 0))
            
            # Gambar teks alarm
            alarm_font = pygame.font.SysFont(None, 48)
            alarm_text = alarm_font.render("! ALARM !", True, (255, 0, 0))
            text_rect = alarm_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
            self.screen.blit(alarm_text, text_rect)

    def cleanup(self):
        """Metode untuk membersihkan resources saat keluar dari ruangan"""
        # Hentikan suara alarm jika masih diputar
        if hasattr(self, 'alarm_sound_played') and self.alarm_sound_played:
            pygame.mixer.stop()
            self.alarm_sound_played = False
