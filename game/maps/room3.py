import pygame
import random
import math
from game.utils.constants import *
from game.utils.asset_loader import load_and_transform, get_frames
from game.maps.base_room import BaseRoom, HidingSpot, CollectibleItem
from game.entities.laser import Laser

class Room3(BaseRoom):
    def load_assets(self):
        # Load tiles (same as Room2)
        self.tiles = {
            0: load_and_transform("game/assets/ruangan3/walls/floor.png", (TILE_SIZE, TILE_SIZE)),
            1: load_and_transform("game/assets/ruangan3/walls/wall-kiri.png", (TILE_SIZE, TILE_SIZE)),
            1.5: load_and_transform("game/assets/ruangan3/walls/wall-kanan.png", (TILE_SIZE, TILE_SIZE)),
            2: load_and_transform("game/assets/ruangan3/walls/wall-atas.png", (TILE_SIZE, TILE_SIZE)),
            2.5: load_and_transform("game/assets/ruangan3/walls/wall-bawah.png", (TILE_SIZE, TILE_SIZE)),
            7: load_and_transform("game/assets/objects/pintu/tiang.png", (TILE_SIZE, TILE_SIZE)),
            96: load_and_transform("game/assets/ruangan3/walls/wall-kiri-atas.png", (int(TILE_SIZE * 3.4), int(TILE_SIZE * 3.4))),
            97: load_and_transform("game/assets/ruangan3/walls/wall-sudut.png", (TILE_SIZE, TILE_SIZE), flip_x=True),
            98: load_and_transform("game/assets/ruangan3/walls/wall-sudut.png", (TILE_SIZE, TILE_SIZE), rotate_angle=90),
            99: load_and_transform("game/assets/ruangan3/walls/wall-sudut.png", (TILE_SIZE, TILE_SIZE), rotate_angle=180),
            100: pygame.Surface((TILE_SIZE, TILE_SIZE))
        }

        # Load objects (same as Room2)
        self.objects = {
            "tanaman": load_and_transform("game/assets/ruangan1/objects/tanaman.png", (TILE_SIZE, TILE_SIZE)),
            "tanaman2": load_and_transform("game/assets/ruangan1/objects/tanaman2.png", (TILE_SIZE, TILE_SIZE)),
           
        }
        
        # Inisialisasi variabel pencahayaan
        self.light_radius = 120  # Radius cahaya di sekitar player (lebih kecil dari ruangan2)
        self.ambient_light = 60  # Tingkat cahaya ambient (0-255, 0 = gelap total) (lebih gelap dari ruangan2)
        
        # Buat surface untuk efek pencahayaan
        self.light_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Variabel untuk laser bergerak
        self.moving_lasers = []
        self.laser_timer = 0
    
    def setup_room(self):
        # Setup tilemap (layout mirip dengan room2 tapi dengan beberapa perbedaan)
        self.tilemap = [
            [98,2,2,2,2,2,2,2,7,0,7,2,2,2,2,2,2,2,2,99],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [98,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5]
        ]
        
        # Tilemap with door at bottom (for exiting room 3)
        self.tilemap_with_door = [
            [98,2,2,2,2,2,2,2,7,0,7,2,2,2,2,2,2,2,2,99],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1.5],
            [98,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,7,0,7]
        ]
        
        # Setup object positions (layout yang lebih kompleks untuk ruangan3)
        self.object_positions = [
            {"img": self.objects["tanaman"], "x": 15, "y": 1},
            {"img": self.objects["tanaman2"], "x": 13, "y": 10},
            {"img": self.objects["tanaman2"], "x": 3, "y": 1},
            {"img": self.objects["tanaman2"], "x": 2, "y": 10},
        
        ]
        
        # Setup colliders
        self.colliders = []
        for obj in self.object_positions:
            img = obj["img"]
            rect = img.get_rect()
            rect.topleft = (obj["x"] * TILE_SIZE, obj["y"] * TILE_SIZE)
            self.colliders.append(rect)
        
        # Add colliders for wall tiles
        solid_tile_ids = [1, 2, 2.5, 1.5, 7, 96, 97, 98, 99]
        for y, row in enumerate(self.tilemap):
            for x, tile_id in enumerate(row):
                if tile_id in solid_tile_ids:
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    self.colliders.append(rect)
        
        # Setup hiding spots
        self.hiding_spots = [
            HidingSpot(pygame.Rect(15 * TILE_SIZE - 10, 1 * TILE_SIZE - 10, TILE_SIZE + 20, TILE_SIZE + 20), "tanaman1"),
            HidingSpot(pygame.Rect(13 * TILE_SIZE - 10, 10 * TILE_SIZE - 10, TILE_SIZE + 20, TILE_SIZE + 20), "tanaman2"),
            HidingSpot(pygame.Rect(3 * TILE_SIZE - 10, 1 * TILE_SIZE - 10, TILE_SIZE + 20, TILE_SIZE + 20), "tanaman3"),
            HidingSpot(pygame.Rect(2 * TILE_SIZE - 10, 10 * TILE_SIZE - 10, TILE_SIZE + 20, TILE_SIZE + 20), "tanaman4"),
        ]
        
        # Setup patrol routes (lebih kompleks untuk ruangan3)
        patrol_routes = [
    [(15, 8), (15, 3), (5, 3), (5, 8)],  # Rute patroli penjaga 1 (starts far from entrance)
    [(10, 9), (10, 2), (16, 2), (16, 9)],  # Rute patroli penjaga 2
    [(18, 5), (12, 5), (12, 8), (18, 8)],  # Rute patroli penjaga 3 (stays on right side)
    [(8, 8), (8, 3), (15, 3), (15, 8), (8, 8)]  # Rute patroli penjaga 4 (stays away from entrance)
]
        
        # Setup guards
        from game.entities.guard import Guard
        
        guard_types = {
            "ariana": {
                "sprite_sheet": pygame.image.load("game/assets/guard_img/ariana.png").convert_alpha(),
                "speed": GUARD_SPEED,
                "vision_range": 200,
                "color": (61, 52, 235)
            },
            "aristocrate": {
                "sprite_sheet": pygame.image.load("game/assets/guard_img/aristocrate.png").convert_alpha(),
                "speed": GUARD_SPEED * 1.2,
                "vision_range": 180,
                "color": (255, 0, 0)
            },
            "rapper": {
                "sprite_sheet": pygame.image.load("game/assets/guard_img/rapper.png").convert_alpha(),
                "speed": GUARD_SPEED * 1.2,
                "vision_range": 180,
                "color": (203, 219, 26)
            },
            "nia": {
                "sprite_sheet": pygame.image.load("game/assets/guard_img/nia.png").convert_alpha(),
                "speed": GUARD_SPEED * 1.2,
                "vision_range": 180,
                "color": (245, 29, 220)
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
        
        # Buat 4 penjaga dengan tipe dan rute berbeda
        self.guards = [
    Guard(15 * TILE_SIZE, 8 * TILE_SIZE, "ariana", patrol_routes[0], guard_frames["ariana"], guard_types["ariana"], self.colliders),
    Guard(10 * TILE_SIZE, 9 * TILE_SIZE, "aristocrate", patrol_routes[1], guard_frames["aristocrate"], guard_types["aristocrate"], self.colliders),
    Guard(18 * TILE_SIZE, 5 * TILE_SIZE, "rapper", patrol_routes[2], guard_frames["rapper"], guard_types["rapper"], self.colliders),
    Guard(8 * TILE_SIZE, 8 * TILE_SIZE, "nia", patrol_routes[3], guard_frames["nia"], 
         {"sprite_sheet": guard_types["aristocrate"]["sprite_sheet"], 
          "speed": GUARD_SPEED * 1.3,  # Penjaga ini lebih cepat
          "vision_range": 220,  # Dan melihat lebih jauh
          "color": (255, 0, 0)}, 
         self.colliders)
]
        
        # Setup laser statis
        self.lasers = [
            Laser(4 * TILE_SIZE, 3 * TILE_SIZE, 8 * TILE_SIZE, 3 * TILE_SIZE, color=(255, 0, 0), thickness=2),
            Laser(12 * TILE_SIZE, 3 * TILE_SIZE, 16 * TILE_SIZE, 3 * TILE_SIZE, color=(255, 0, 0), thickness=2),
            Laser(8 * TILE_SIZE, 8 * TILE_SIZE, 12 * TILE_SIZE, 8 * TILE_SIZE, color=(255, 0, 0), thickness=2),
            Laser(4 * TILE_SIZE, 9 * TILE_SIZE, 4 * TILE_SIZE, 5 * TILE_SIZE, color=(255, 0, 0), thickness=2),
            Laser(16 * TILE_SIZE, 9 * TILE_SIZE, 16 * TILE_SIZE, 5 * TILE_SIZE, color=(255, 0, 0), thickness=2),
            # Tambahan laser untuk ruangan3 (dengan pengurangan di dekat pintu)
            Laser(2 * TILE_SIZE, 6 * TILE_SIZE, 6 * TILE_SIZE, 6 * TILE_SIZE, color=(255, 0, 0), thickness=2),
            Laser(14 * TILE_SIZE, 6 * TILE_SIZE, 18 * TILE_SIZE, 6 * TILE_SIZE, color=(255, 0, 0), thickness=2),
            # Laser di dekat pintu atas dihapus: Laser(10 * TILE_SIZE, 1 * TILE_SIZE, 10 * TILE_SIZE, 3 * TILE_SIZE, color=(255, 0, 0), thickness=2),
            # Laser di dekat pintu bawah dimodifikasi agar tidak menghalangi pintu
            Laser(3 * TILE_SIZE, 10 * TILE_SIZE, 7 * TILE_SIZE, 10 * TILE_SIZE, color=(255, 0, 0), thickness=2),
            Laser(13 * TILE_SIZE, 10 * TILE_SIZE, 17 * TILE_SIZE, 10 * TILE_SIZE, color=(255, 0, 0), thickness=2),
        ]
        
        # Setup laser bergerak
        self.setup_moving_lasers()
        
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
        
        # Setup satu item curian di lokasi terjauh
        self.setup_collectible_item()
    
    def setup_moving_lasers(self):
        # Laser yang bergerak horizontal
        self.moving_lasers = [
            {
                "laser": Laser(2 * TILE_SIZE, 4 * TILE_SIZE, 6 * TILE_SIZE, 4 * TILE_SIZE, color=(255, 50, 50), thickness=3),
                "start_x1": 2 * TILE_SIZE,
                "start_y1": 4 * TILE_SIZE,
                "start_x2": 6 * TILE_SIZE,
                "start_y2": 4 * TILE_SIZE,
                "end_x1": 14 * TILE_SIZE,
                "end_y1": 4 * TILE_SIZE,
                "end_x2": 18 * TILE_SIZE,
                "end_y2": 4 * TILE_SIZE,
                "progress": 0,
                "speed": 0.001,
                "direction": 1  # 1 = forward, -1 = backward
            },
            {
                "laser": Laser(14 * TILE_SIZE, 7 * TILE_SIZE, 18 * TILE_SIZE, 7 * TILE_SIZE, color=(255, 50, 50), thickness=3),
                "start_x1": 14 * TILE_SIZE,
                "start_y1": 7 * TILE_SIZE,
                "start_x2": 18 * TILE_SIZE,
                "start_y2": 7 * TILE_SIZE,
                "end_x1": 2 * TILE_SIZE,
                "end_y1": 7 * TILE_SIZE,
                "end_x2": 6 * TILE_SIZE,
                "end_y2": 7 * TILE_SIZE,
                "progress": 0,
                "speed": 0.0015,
                "direction": 1
            },
            # Laser yang bergerak vertikal
            {
                "laser": Laser(8 * TILE_SIZE, 1 * TILE_SIZE, 8 * TILE_SIZE, 3 * TILE_SIZE, color=(255, 50, 50), thickness=3),
                "start_x1": 8 * TILE_SIZE,
                "start_y1": 1 * TILE_SIZE,
                "start_x2": 8 * TILE_SIZE,
                "start_y2": 3 * TILE_SIZE,
                "end_x1": 8 * TILE_SIZE,
                "end_y1": 8 * TILE_SIZE,
                "end_x2": 8 * TILE_SIZE,
                "end_y2": 10 * TILE_SIZE,
                "progress": 0,
                "speed": 0.0012,
                "direction": 1
            },
            {
                "laser": Laser(12 * TILE_SIZE, 8 * TILE_SIZE, 12 * TILE_SIZE, 10 * TILE_SIZE, color=(255, 50, 50), thickness=3),
                "start_x1": 12 * TILE_SIZE,
                "start_y1": 8 * TILE_SIZE,
                "start_x2": 12 * TILE_SIZE,
                "start_y2": 10 * TILE_SIZE,
                "end_x1": 12 * TILE_SIZE,
                "end_y1": 1 * TILE_SIZE,
                "end_x2": 12 * TILE_SIZE,
                "end_y2": 3 * TILE_SIZE,
                "progress": 0,
                "speed": 0.0008,
                "direction": 1
            }
        ]
    
    def setup_collectible_item(self):
        # Define valid areas for items (avoid walls and objects)
        valid_item_positions = []
        for x in range(1, MAP_WIDTH - 1):
            for y in range(1, MAP_HEIGHT - 1):
                test_rect = pygame.Rect(x * TILE_SIZE + TILE_SIZE//4, y * TILE_SIZE + TILE_SIZE//4, 
                                       TILE_SIZE//2, TILE_SIZE//2)
                
                if not any(test_rect.colliderect(c) for c in self.colliders):
                    valid_item_positions.append((x * TILE_SIZE + TILE_SIZE//4, y * TILE_SIZE + TILE_SIZE//4))
        
        # Shuffle valid positions and pick some for items
        random.shuffle(valid_item_positions)
        
        # Create 5 collectible items at strategic locations
        self.collectible_items = []
        
        # Define specific strategic locations for items
        strategic_locations = [
            (18 * TILE_SIZE - 16, 1 * TILE_SIZE + 16),  # Top right corner
            (2 * TILE_SIZE + 16, 2 * TILE_SIZE + 16),   # Top left area
            (5 * TILE_SIZE + 16, 9 * TILE_SIZE - 16),   # Bottom left area
            (15 * TILE_SIZE - 16, 9 * TILE_SIZE - 16),  # Bottom right area
            (10 * TILE_SIZE, 6 * TILE_SIZE)             # Center of the room
        ]
        
        # List of shapes and colors for items
        item_shapes = ["circle", "square", "diamond", "triangle", "star"]
        item_colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255)   # Magenta
        ]
        
        # Create collectible items with different shapes and colors at strategic locations
        for i in range(5):
            x, y = strategic_locations[i]
            shape = item_shapes[i]
            color = item_colors[i]
            value = 30 if shape == "star" else 20 if shape == "diamond" else 10
            
            # Make the last item (center of room) more valuable
            if i == 4:
                value = 50
                shape = "star"
                color = (255, 215, 0)  # Gold color for the special item
            
            item = CollectibleItem(x, y, "regular", shape, color, value)
            
            # Make the special item slightly larger
            if i == 4:
                item.width = 24
                item.height = 24
            
            self.collectible_items.append(item)
    
    def spawn_key(self):
        # Cari lokasi terjauh dari posisi player saat ini
        player_x = self.player.x + self.player.width // 2
        player_y = self.player.y + self.player.height // 2
        
        # Daftar kandidat lokasi untuk kunci
        key_locations = [
            (1 * TILE_SIZE + 16, 1 * TILE_SIZE + 16),  # Pojok kiri atas
            (18 * TILE_SIZE - 16, 1 * TILE_SIZE + 16),  # Pojok kanan atas
            (1 * TILE_SIZE + 16, 10 * TILE_SIZE - 16),  # Pojok kiri bawah
            (18 * TILE_SIZE - 16, 10 * TILE_SIZE - 16)  # Pojok kanan bawah
        ]
        
        # Cari lokasi terjauh
        max_distance = 0
        farthest_location = key_locations[0]
        
        for loc in key_locations:
            dx = loc[0] - player_x
            dy = loc[1] - player_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > max_distance:
                max_distance = distance
                farthest_location = loc
        
        # Spawn kunci di lokasi terjauh
        key_x, key_y = farthest_location
        
        key_item = CollectibleItem(key_x, key_y, "key", "star", (255, 215, 0), 50)
        key_item.width = 24
        key_item.height = 24
        self.collectible_items.append(key_item)
        
        # Tambahkan efek visual
        self.add_collection_effect(key_x + 12, key_y + 12, (255, 215, 0))
        
        # Tambahkan notifikasi
        self.add_notification("Kunci muncul di lokasi terjauh!", (255, 215, 0), SCREEN_WIDTH // 2, 100, duration=3000, velocity=0)
    
    def open_door(self):
        # Replace tilemap with version that has open door
        self.tilemap = self.tilemap_with_door
        
        # Remove collider for door
        self.colliders = [c for c in self.colliders if not (c.left == 9 * TILE_SIZE and c.top == 11 * TILE_SIZE)]
    
    def update(self, dt, mouse_held, mouse_pos):
        # Update base room elements
        super().update(dt, mouse_held, mouse_pos)
        
        # Update laser statis
        laser_triggered = False
        for laser in self.lasers:
            if laser.update(dt, self.player):
                laser_triggered = True
        
        # Update laser bergerak
        self.update_moving_lasers(dt)
        for moving_laser in self.moving_lasers:
            if moving_laser["laser"].update(dt, self.player):
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
    
    def update_moving_lasers(self, dt):
        for laser_data in self.moving_lasers:
            # Update progress
            laser_data["progress"] += laser_data["speed"] * dt * laser_data["direction"]
            
            # Reverse direction if needed
            if laser_data["progress"] >= 1:
                laser_data["direction"] = -1
            elif laser_data["progress"] <= 0:
                laser_data["direction"] = 1
            
            # Clamp progress between 0 and 1
            laser_data["progress"] = max(0, min(1, laser_data["progress"]))
            
            # Calculate current position using easing function
            t = self.ease_in_out_sine(laser_data["progress"])
            
            # Update laser position
            x1 = laser_data["start_x1"] + (laser_data["end_x1"] - laser_data["start_x1"]) * t
            y1 = laser_data["start_y1"] + (laser_data["end_y1"] - laser_data["start_y1"]) * t
            x2 = laser_data["start_x2"] + (laser_data["end_x2"] - laser_data["start_x2"]) * t
            y2 = laser_data["start_y2"] + (laser_data["end_y2"] - laser_data["start_y2"]) * t
            
            # Update laser coordinates
            laser_data["laser"].x1 = x1
            laser_data["laser"].y1 = y1
            laser_data["laser"].x2 = x2
            laser_data["laser"].y2 = y2
            
            # Recalculate laser rect
            laser_data["laser"].rect = laser_data["laser"]._calculate_rect()
    
    def ease_in_out_sine(self, x):
        return -(math.cos(math.pi * x) - 1) / 2
    
    def check_room_transition(self):
        # Check if player is at exit door (top of room) - lebih ketat
        if (self.player.y < TILE_SIZE // 2 and  # Harus sangat dekat dengan tepi atas
            self.player.x > 8.5 * TILE_SIZE and self.player.x < 10.5 * TILE_SIZE):  # Area pintu lebih sempit
            # Transition back to room 2
            self.game_manager.transition_to_room(1)
        
            # Position player at exit door of room 2
            self.player.x = 9 * TILE_SIZE
            self.player.y = 10 * TILE_SIZE
        
        # Check if player is at bottom exit door (if door is open) - lebih ketat
        if (self.door_opened and 
            self.player.y > SCREEN_HEIGHT - TILE_SIZE // 2 and  # Harus sangat dekat dengan tepi bawah
            self.player.x > 8.5 * TILE_SIZE and self.player.x < 10.5 * TILE_SIZE):  # Area pintu lebih sempit
            # Transition to room 4
            self.game_manager.transition_to_room(3)
        
            # Position player at entrance of room 4
            self.player.x = 2 * TILE_SIZE
            self.player.y = 5 * TILE_SIZE
    
    def draw(self):
        # Gambar latar belakang dan objek dasar
        self.draw_tilemap()
        self.draw_objects()
        self.draw_items()
        
        # Gambar laser statis
        for laser in self.lasers:
            laser.draw(self.screen)
        
        # Gambar laser bergerak
        for laser_data in self.moving_lasers:
            laser_data["laser"].draw(self.screen)
        
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
