import pygame
import random
import math
from game.utils.constants import *
from game.utils.asset_loader import load_and_transform, get_frames
from game.maps.base_room import BaseRoom, HidingSpot, CollectibleItem

class Room1(BaseRoom):
    def load_assets(self):
        # Load tiles
        self.tiles = {
            0: load_and_transform("game/assets/ruangan1/walls/floor.png", (TILE_SIZE, TILE_SIZE)),
            1: load_and_transform("game/assets/ruangan1/walls/wall-kiri-kanan.png", (TILE_SIZE, TILE_SIZE)),
            2: load_and_transform("game/assets/ruangan1/walls/wall-atas-bawah.png", (TILE_SIZE, TILE_SIZE)),
            7: load_and_transform("game/assets/objects/pintu/tiang.png", (TILE_SIZE, TILE_SIZE)),
            96: load_and_transform("game/assets/ruangan1/walls/wall-kiri-atas.png", (int(TILE_SIZE * 3.4), int(TILE_SIZE * 3.4))),
            97: load_and_transform("game/assets/ruangan1/walls/wall-sudut.png", (TILE_SIZE, TILE_SIZE), flip_x=True),
            98: load_and_transform("game/assets/ruangan1/walls/wall-sudut.png", (TILE_SIZE, TILE_SIZE), rotate_angle=90),
            99: load_and_transform("game/assets/ruangan1/walls/wall-sudut.png", (TILE_SIZE, TILE_SIZE), rotate_angle=180),
            100: pygame.Surface((TILE_SIZE, TILE_SIZE))
        }

        # Load objects
        self.objects = {
            "bed_big": load_and_transform("game/assets/ruangan1/objects/kasur.png", (TILE_SIZE * 2, TILE_SIZE * 2)),
            "tanaman": load_and_transform("game/assets/ruangan1/objects/tanaman.png", (TILE_SIZE, TILE_SIZE)),
            "tanaman2": load_and_transform("game/assets/ruangan1/objects/tanaman2.png", (TILE_SIZE, TILE_SIZE)),
            "sofa": load_and_transform("game/assets/ruangan1/objects/sofa.png", (TILE_SIZE, TILE_SIZE)),
            "meja_bundar": load_and_transform("game/assets/ruangan1/objects/meja-bundar.png", (160, 108)),
            "meja_kotak": load_and_transform("game/assets/ruangan1/objects/meja-kotak.png", (132, 108)),
            "kursi-atas": load_and_transform("game/assets/ruangan1/objects/kursi-atas.png", (int(TILE_SIZE / 1.5), int(TILE_SIZE / 1.5))),
            "kursi-kanan": load_and_transform("game/assets/ruangan1/objects/kursi-kanan.png", (int(TILE_SIZE / 1.5), int(TILE_SIZE / 1.5))),
            "kursi-kiri": load_and_transform("game/assets/ruangan1/objects/kursi-kiri.png", (int(TILE_SIZE / 1.5), int(TILE_SIZE / 1.5))),
            "kursi-bawah": load_and_transform("game/assets/ruangan1/objects/kursi-bawah.png", (int(TILE_SIZE / 1.5), int(TILE_SIZE / 1.5))),
        }
    
    def setup_room(self):
        # Setup tilemap
        self.tilemap = [
            [96,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,97],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [98,2,2,2,2,2,2,2,7,0,7,2,2,2,2,2,2,2,2,99]
        ]
        
        # Tilemap with door on right side
        self.tilemap_with_door = [
            [96,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,97],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [98,2,2,2,2,2,2,2,7,0,7,2,2,2,2,2,2,2,2,99]
        ]
        
        # Setup object positions
        self.object_positions = [
            {"img": self.objects["bed_big"], "x": 1, "y": 1},
            {"img": self.objects["tanaman"], "x": 5, "y": 1},
            {"img": self.objects["tanaman2"], "x": 7, "y": 10},
            {"img": self.objects["sofa"], "x": 13, "y": 1},
            {"img": self.objects["sofa"], "x": 14, "y": 1},
            {"img": self.objects["meja_bundar"], "x": 13, "y": 2},
            {"img": self.objects["meja_kotak"], "x": 6, "y": 5},
            {"img": self.objects["meja_kotak"], "x": 8, "y": 5},
            {"img": self.objects["kursi-atas"], "x": 6, "y": 4.2},
            {"img": self.objects["kursi-atas"], "x": 7, "y": 4.2},
            {"img": self.objects["kursi-atas"], "x": 8, "y": 4.2},
            {"img": self.objects["kursi-atas"], "x": 9, "y": 4.2},
            {"img": self.objects["kursi-kanan"], "x": 10.2, "y": 5.5},
            {"img": self.objects["kursi-kiri"], "x": 5.2, "y": 5.5},
            {"img": self.objects["kursi-atas"], "x": 6, "y": 7},
            {"img": self.objects["kursi-atas"], "x": 7, "y": 7},
            {"img": self.objects["kursi-atas"], "x": 8, "y": 7},
            {"img": self.objects["kursi-atas"], "x": 9, "y": 7}
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
            HidingSpot(pygame.Rect(5 * TILE_SIZE - 10, 1 * TILE_SIZE - 10, TILE_SIZE + 20, TILE_SIZE + 20), "tanaman1"),
            HidingSpot(pygame.Rect(7 * TILE_SIZE - 10, 10 * TILE_SIZE - 10, TILE_SIZE + 20, TILE_SIZE + 20), "tanaman2"),
        ]
        
        # Setup patrol routes
        patrol_routes = [
            [(3, 3), (3, 8), (12, 8), (12, 3)],
            [(16, 2), (16, 8), (16, 8), (16, 2)],
        ]
        
        # Setup guards
        from game.entities.guard import Guard
        
        guard_types = {
            "ranger": {
                "sprite_sheet": pygame.image.load("game/assets/guard_img/rangerr.png").convert_alpha(),
                "speed": GUARD_SPEED,
                "vision_range": 200,
                "color": (255, 0, 0)
            },
            "aristocrate": {
                "sprite_sheet": pygame.image.load("game/assets/guard_img/aristocrate.png").convert_alpha(),
                "speed": GUARD_SPEED * 1.2,
                "vision_range": 180,
                "color": (255, 0, 0)
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
            Guard(3 * TILE_SIZE, 3 * TILE_SIZE, "ranger", patrol_routes[0], guard_frames["ranger"], guard_types["ranger"], self.colliders),
            Guard(16 * TILE_SIZE, 2 * TILE_SIZE, "aristocrate", patrol_routes[1], guard_frames["aristocrate"], guard_types["aristocrate"], self.colliders)
        ]
        
        # Setup collectible items
        self.setup_collectible_items()
    
    def setup_collectible_items(self):
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
        num_items = min(6, len(valid_item_positions))
        
        # List of shapes and colors for items
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
        
        # Create collectible items with different shapes and colors
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
        self.colliders = [c for c in self.colliders if not (c.left == 19 * TILE_SIZE and c.top == 5 * TILE_SIZE)]
    
    def check_room_transition(self):
        # Check if player is at exit door (right side of room) - lebih ketat
        if (self.door_opened and 
            self.player.x > SCREEN_WIDTH - TILE_SIZE // 2 and  # Harus sangat dekat dengan tepi kanan
            self.player.y > 4.5 * TILE_SIZE and self.player.y < 6.5 * TILE_SIZE):  # Area pintu lebih sempit
            # Transition to next room
            self.game_manager.transition_to_room(1)  # Index 1 for second room
