import pygame
import random
import math
import sys
from game.utils.constants import *
from game.utils.asset_loader import load_and_transform
from game.maps.base_room import BaseRoom, HidingSpot, CollectibleItem

class StaticGuard:
    def __init__(self, x, y, image_path, colliders=None, vision_range=250, vision_color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path).convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vision_range = vision_range
        self.vision_color = vision_color
        self.direction = 'down'  # Default direction
        self.rotation_timer = 0
        self.rotation_interval = 3000  # Rotate every 3 seconds
        self.alert_level = 0
        self.state = "patrol"
        self.last_known_player_pos = None
        self.colliders = colliders or []  # Store colliders
        
        # Emote variables
        self.show_emote = False
        self.emote_type = "none"
        self.emote_timer = 0
        self.emote_duration = 2000
        
        # Sound variables
        self.alert_sound_played = False
        self.alert_sound = None
        self.alert_sound_channel = None
        try:
            self.alert_sound = pygame.mixer.Sound("game/assets/sound/alert.wav")
            self.alert_sound.set_volume(0.7)
        except pygame.error as e:
            print(f"Could not load alert sound file: {e}")
    
        # Patrol properties
        self.is_patrolling = True
        self.base_patrol_speed = 3.0  # Base speed
        self.patrol_speed = self.base_patrol_speed
        self.patrol_timer = 0
        self.speed_change_timer = 0
        self.speed_change_interval = random.randint(800, 2000)  # Random interval for speed changes
        self.direction_change_interval = random.randint(500, 1500)  # Random interval for direction changes
        self.move_direction = [random.choice([-1, 1]), random.choice([-1, 1])]  # Random initial direction
        self.movement_pattern = "straight"  # Can be "straight", "zigzag", or "erratic"
        self.pattern_change_timer = 0
        self.pattern_change_interval = random.randint(2000, 4000)  # Change pattern every 2-4 seconds
        self.zigzag_amplitude = random.uniform(0.5, 1.5)  # For zigzag pattern
        self.zigzag_frequency = random.uniform(0.005, 0.015)  # For zigzag pattern
        self.patrol_bounds = {
            'min_x': TILE_SIZE * 1,
            'max_x': SCREEN_WIDTH - TILE_SIZE * 1 - self.width,
            'min_y': TILE_SIZE * 1,
            'max_y': SCREEN_HEIGHT - TILE_SIZE * 1 - self.height
        }
        
        # Add a preference for vertical movement to ensure Trump moves up and down more often
        self.vertical_movement_bias = 0.7  # Higher chance to move vertically
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self, dt, player, guards=None, hiding_spots=None):
        # Update patrol movement
        if self.is_patrolling:
            # Update timers
            self.patrol_timer += dt
            self.speed_change_timer += dt
            self.pattern_change_timer += dt
            
            # Change speed randomly
            if self.speed_change_timer >= self.speed_change_interval:
                self.speed_change_timer = 0
                self.speed_change_interval = random.randint(800, 2000)
                # Randomly choose a new speed between 50% and 200% of base speed
                self.patrol_speed = self.base_patrol_speed * random.uniform(0.5, 2.0)
            
            # Change movement pattern randomly
            if self.pattern_change_timer >= self.pattern_change_interval:
                self.pattern_change_timer = 0
                self.pattern_change_interval = random.randint(2000, 4000)
                self.movement_pattern = random.choice(["straight", "zigzag", "erratic"])
                # Reset zigzag parameters
                self.zigzag_amplitude = random.uniform(0.5, 1.5)
                self.zigzag_frequency = random.uniform(0.005, 0.015)
            
            # Change direction randomly
            if self.patrol_timer >= self.direction_change_interval:
                self.patrol_timer = 0
                self.direction_change_interval = random.randint(300, 1200)
                
                # Different direction change behavior based on pattern
                if self.movement_pattern == "straight":
                    # For straight movement, completely change direction
                    # Add bias toward vertical movement to ensure Trump moves up and down
                    if random.random() < self.vertical_movement_bias:
                        # Prioritize vertical movement
                        self.move_direction[0] = random.choice([-0.3, 0, 0.3])  # Reduced horizontal movement
                        self.move_direction[1] = random.choice([-1, 1])  # Full vertical movement
                    else:
                        self.move_direction[0] = random.choice([-1, 0, 1])
                        self.move_direction[1] = random.choice([-1, 0, 1])
                    
                    # Ensure we're not standing still
                    if self.move_direction[0] == 0 and self.move_direction[1] == 0:
                        self.move_direction[1] = random.choice([-1, 1])  # Default to vertical movement
                
                elif self.movement_pattern == "erratic":
                    # For erratic movement, make more dramatic changes with vertical bias
                    if random.random() < self.vertical_movement_bias:
                        self.move_direction[0] = random.choice([-0.5, 0, 0.5])
                        self.move_direction[1] = random.choice([-1, -0.7, 0.7, 1])
                    else:
                        self.move_direction[0] = random.choice([-1, -0.7, 0, 0.7, 1])
                        self.move_direction[1] = random.choice([-1, -0.7, 0, 0.7, 1])
                    
                    # Ensure we're not standing still
                    if abs(self.move_direction[0]) < 0.1 and abs(self.move_direction[1]) < 0.1:
                        self.move_direction[1] = random.choice([-1, 1])  # Default to vertical movement
            
            # Calculate base movement
            move_x = self.move_direction[0] * self.patrol_speed
            move_y = self.move_direction[1] * self.patrol_speed
            
            # Apply zigzag pattern if active
            if self.movement_pattern == "zigzag":
                # Add sine wave to movement for zigzag effect
                if abs(self.move_direction[0]) > abs(self.move_direction[1]):
                    # Moving more horizontally, zigzag vertically
                    move_y += math.sin(self.patrol_timer * self.zigzag_frequency) * self.zigzag_amplitude * self.patrol_speed
                else:
                    # Moving more vertically, zigzag horizontally
                    move_x += math.sin(self.patrol_timer * self.zigzag_frequency) * self.zigzag_amplitude * self.patrol_speed
            
            # Update position with bounds checking
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            # Bounce off boundaries
            if new_x < self.patrol_bounds['min_x'] or new_x > self.patrol_bounds['max_x']:
                self.move_direction[0] *= -1
                new_x = self.x + (self.move_direction[0] * self.patrol_speed)
            
            if new_y < self.patrol_bounds['min_y'] or new_y > self.patrol_bounds['max_y']:
                self.move_direction[1] *= -1
                new_y = self.y + (self.move_direction[1] * self.patrol_speed)
            
            # Update position
            self.x = new_x
            self.y = new_y
            
            # Update direction based on movement
            if abs(move_x) > abs(move_y):
                self.direction = 'right' if move_x > 0 else 'left'
            else:
                self.direction = 'down' if move_y > 0 else 'up'
        
        # Check if player is visible
        if player:
            player_is_hidden = False
            if hiding_spots:
                for spot in hiding_spots:
                    if spot.contains_player(player):
                        player_is_hidden = True
                        break
            
            if not player_is_hidden:
                if self.can_see_player(player):
                    self.alert_level = 100
                    self.state = "chase"
                    self.last_known_player_pos = (player.x + player.width // 2, player.y + player.height // 2)
                    
                    # If in chase mode, move toward player
                    if self.state == "chase":
                        player_center_x = player.x + player.width // 2
                        player_center_y = player.y + player.height // 2
                        guard_center_x = self.x + self.width // 2
                        guard_center_y = self.y + self.height // 2
                        
                        dx = player_center_x - guard_center_x
                        dy = player_center_y - guard_center_y
                        distance = math.sqrt(dx*dx + dy*dy)
                        
                        if distance > 0:
                            # Move toward player with increased speed
                            chase_speed = self.patrol_speed * 1.2
                            move_x = (dx / distance) * chase_speed
                            move_y = (dy / distance) * chase_speed
                            
                            self.x += move_x
                            self.y += move_y
                            
                            # Update direction based on movement
                            if abs(move_x) > abs(move_y):
                                self.direction = 'right' if move_x > 0 else 'left'
                            else:
                                self.direction = 'down' if move_y > 0 else 'up'
                    
                    # Show alert emote
                    if not self.show_emote:
                        self.show_emote = True
                        self.emote_type = "alert"
                        self.emote_timer = 0
                        
                        # Play alert sound if not already playing
                        if not self.alert_sound_played and self.alert_sound:
                            self.alert_sound_channel = self.alert_sound.play()
                            self.alert_sound_played = True
                else:
                    # Gradually decrease alert level
                    self.alert_level = max(0, self.alert_level - 0.5)
                    
                    if self.alert_level < 30 and self.state == "chase":
                        self.state = "patrol"
                        # Show confused emote
                        self.show_emote = True
                        self.emote_type = "confused"
                        self.emote_timer = 0
                        
                        # Stop alert sound
                        if self.alert_sound_played and self.alert_sound_channel and self.alert_sound_channel.get_busy():
                            self.alert_sound_channel.stop()
                        self.alert_sound_played = False
            elif self.state == "chase":
                # Player is hiding, decrease alert level faster
                self.alert_level = max(0, self.alert_level - 1.5)
                
                if self.alert_level < 30:
                    self.state = "patrol"
                    # Show confused emote
                    self.show_emote = True
                    self.emote_type = "confused"
                    self.emote_timer = 0
                    
                    # Stop alert sound
                    if self.alert_sound_played and self.alert_sound_channel and self.alert_sound_channel.get_busy():
                        self.alert_sound_channel.stop()
                    self.alert_sound_played = False
        
        # Update emote timer
        if self.show_emote:
            self.emote_timer += dt
            if self.emote_timer >= self.emote_duration:
                self.show_emote = False
                self.emote_timer = 0
    
    def can_see_player(self, player):
        # Calculate distance to player
        player_center_x = player.x + player.width // 2
        player_center_y = player.y + player.height // 2
        guard_center_x = self.x + self.width // 2
        guard_center_y = self.y + self.height // 2
        
        dx = player_center_x - guard_center_x
        dy = player_center_y - guard_center_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Adjust vision range based on player's crouching state
        effective_range = self.vision_range
        if player.is_crouching:
            effective_range = max(self.vision_range - player.stealth_bonus, self.vision_range * 0.7)
        
        # If player is beyond vision range, can't see
        if distance > effective_range:
            return False
        
        # Calculate angle to player
        angle_to_player = math.atan2(dy, dx)
        
        # Get guard's facing direction angle
        if self.direction == 'up':
            guard_angle = math.atan2(-1, 0)
        elif self.direction == 'down':
            guard_angle = math.atan2(1, 0)
        elif self.direction == 'left':
            guard_angle = math.atan2(0, -1)
        else:  # right
            guard_angle = math.atan2(0, 1)
        
        # Calculate angle difference
        angle_diff = abs(angle_to_player - guard_angle)
        angle_diff = min(angle_diff, 2 * math.pi - angle_diff)  # Handle wrap-around
        
        # Check if player is within field of view (90 degrees - wider than regular guards)
        fov_rad = math.radians(90) / 2
        
        if angle_diff <= fov_rad:
            # Simple ray casting to check for obstacles
            segments = 10
            for i in range(1, segments + 1):
                segment_x = guard_center_x + (dx * i / segments)
                segment_y = guard_center_y + (dy * i / segments)
                
                segment_rect = pygame.Rect(segment_x - 2, segment_y - 2, 4, 4)
                
                # Check collision with obstacles
                for collider in self.colliders:
                    if segment_rect.colliderect(collider):
                        return False  # Obstacle blocking view
                
            return True  # No obstacles, can see player
            
        return False  # Player outside field of view
    
    def draw(self, surface):
        # Draw vision cone
        self.draw_vision_cone(surface)
        
        # Draw the guard
        surface.blit(self.image, (self.x, self.y))
        
        # Draw emote if needed
        if self.show_emote:
            # Position emote next to guard's head
            emote_x = self.x + self.width + 5
            emote_y = self.y - 10
        
            # Draw emote based on type
            font = pygame.font.SysFont(None, 24)
            if self.emote_type == "alert":
                emote_text = font.render("!!", True, (255, 0, 0))  # Red for alert
            elif self.emote_type == "confused":
                emote_text = font.render("??", True, (255, 255, 0))  # Yellow for confusion
        
            surface.blit(emote_text, (emote_x, emote_y))
    
        # Draw alert level indicator
        if self.alert_level > 0:
            # Draw background bar
            bar_width = 40
            bar_height = 5
            bar_x = self.x + (self.width - bar_width) // 2
            bar_y = self.y - 10
            
            pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            
            # Draw alert level
            alert_width = int(bar_width * (self.alert_level / 100))
            
            # Color changes based on alert level
            if self.alert_level < 30:
                color = (0, 255, 0)  # Green
            elif self.alert_level < 70:
                color = (255, 255, 0)  # Yellow
            else:
                color = (255, 0, 0)  # Red
                
            pygame.draw.rect(surface, color, (bar_x, bar_y, alert_width, bar_height))
    
    def draw_vision_cone(self, surface):
        # Vision cone visualization
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Direction vectors based on guard's facing direction
        if self.direction == 'up':
            dir_x, dir_y = 0, -1
        elif self.direction == 'down':
            dir_x, dir_y = 0, 1
        elif self.direction == 'left':
            dir_x, dir_y = -1, 0
        else:  # right
            dir_x, dir_y = 1, 0
        
        # Draw a semi-transparent vision cone
        vision_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Create a cone with 90-degree field of view (wider than regular guards)
        angle = math.atan2(dir_y, dir_x)
        fov_rad = math.radians(90)  # 90-degree field of view
        
        # Create a polygon for the vision cone
        points = [(center_x, center_y)]
        for i in range(21):  # More points = smoother cone
            a = angle - fov_rad/2 + (fov_rad * i / 20)
            end_x = center_x + math.cos(a) * self.vision_range
            end_y = center_y + math.sin(a) * self.vision_range
            points.append((end_x, end_y))
        
        # Vision cone color based on guard state
        if self.state == "patrol":
            color = self.vision_color + (30,)  # 30% opacity
        else:  # chase
            color = (255, 0, 0, 50)  # Red with 50% opacity
            
        pygame.draw.polygon(vision_surface, color, points)
        surface.blit(vision_surface, (0, 0))

class Room4(BaseRoom):
    def load_assets(self):
        # Load tiles (same as Room2)
        self.tiles = {
            0: load_and_transform("game/assets/ruangan4/walls/floor.png", (TILE_SIZE, TILE_SIZE)),
            1: load_and_transform("game/assets/ruangan4/walls/wall-kiri.png", (TILE_SIZE, TILE_SIZE)),
            1.5: load_and_transform("game/assets/ruangan4/walls/wall-kanan.png", (TILE_SIZE, TILE_SIZE)),
            2: load_and_transform("game/assets/ruangan4/walls/wall-atas.png", (TILE_SIZE, TILE_SIZE)),
            2.5: load_and_transform("game/assets/ruangan4/walls/wall-bawah.png", (TILE_SIZE, TILE_SIZE)),
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
            "dokumen": load_and_transform("game/assets/ruangan4/objects/dokumen.png", (TILE_SIZE, TILE_SIZE)),
         
        }
        
        # Initialize lighting variables
        self.light_radius = 150  # Light radius around player
        self.ambient_light = 100  # Ambient light level (0-255, 0 = completely dark)
        
        # Create surface for lighting effect
        self.light_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Variable for document found
        self.document_found = False
        self.document_timer = 0
        self.document_duration = 5000  # 5 seconds
    
    def setup_room(self):
        # Setup tilemap (same layout as room2)
        self.tilemap = [
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ]
        
        # Setup object positions
        self.object_positions = [

            {"img": self.objects["tanaman"], "x": 15, "y": 1},
            {"img": self.objects["tanaman2"], "x": 13, "y": 10},
   
            # Add the secret document on a desk in the center
            # Remove this line:
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
        
        # Setup the static guard (using the trum.png asset)
        self.guards = [
            StaticGuard(10 * TILE_SIZE, 5 * TILE_SIZE, "game/assets/guard_img/trum.png", 
                colliders=self.colliders, vision_range=250, vision_color=(255, 0, 0))
        ]
        
        # Setup the secret document as a collectible item
        self.setup_secret_document()
        
        # Variables for alarm
        self.alarm_triggered = False
        self.alarm_timer = 0
        self.alarm_duration = 5000  # 5 seconds
        self.alarm_sound_played = False
        self.alarm_sound = None
        self.alarm_sound_channel = None
        try:
            self.alarm_sound = pygame.mixer.Sound("game/assets/sound/alert.wav")
            self.alarm_sound.set_volume(0.7)
        except pygame.error as e:
            print(f"Could not load alarm sound file: {e}")
    
    def setup_secret_document(self):
        # Place the secret document in the center of the room
        document_x = 10 * TILE_SIZE
        document_y = 5 * TILE_SIZE
        
        # Create a custom document item that doesn't use the star shape
        class DocumentItem(CollectibleItem):
            def draw(self, surface):
                if not self.collected:
                    # Draw a treasure chest/document instead of the default shapes
                    chest_img = self.objects["dokumen"] if hasattr(self, "objects") else pygame.Surface((self.width, self.height))
                    surface.blit(chest_img, (self.x, self.y))
        
        # Create the document item
        document_item = DocumentItem(document_x, document_y, "regular", "none", (255, 215, 0), 500)
        document_item.width = 32
        document_item.height = 32
        document_item.objects = self.objects  # Pass objects to the item so it can access the document image
        
        # Set this as the ONLY collectible item
        self.collectible_items = [document_item]
        
        # Important: Don't spawn any other items
        self.key_spawned = True  # Prevent key from spawning
        self.all_items_collected = True  # Mark all items as collected to prevent other logic
    
    def update(self, dt, mouse_held, mouse_pos):
        # Update base room elements
        super().update(dt, mouse_held, mouse_pos)
        
        # Check if document has been collected
        if self.collectible_items and self.collectible_items[0].collected and not self.document_found:
            self.document_found = True
            self.document_timer = 0
            
            # Add notification
            self.add_notification("Dokumen Rahasia Ditemukan!", (255, 215, 0), SCREEN_WIDTH // 2, 100, duration=3000, velocity=0)
            
            # Show document content prolog
            self.show_document_prolog()
        
        # Update document timer
        if self.document_found:
            self.document_timer += dt
            
        # Update alarm
        if self.alarm_triggered:
            # Play alarm sound if not already playing
            if not self.alarm_sound_played and self.alarm_sound:
                pygame.mixer.stop()
                self.alarm_sound_channel = self.alarm_sound.play()
                self.alarm_sound_played = True
        
            self.alarm_timer += dt
            if self.alarm_timer >= self.alarm_duration:
                self.alarm_triggered = False
                # Stop alarm sound
                if self.alarm_sound_played:
                    pygame.mixer.stop()
                    self.alarm_sound_played = False

    def show_document_prolog(self):
        # Pause background music during document reveal
        pygame.mixer.music.pause()
        
        # Setup screen
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Whitehouse Heist - Document Revealed")
        
        # Load font
        font = pygame.font.Font("game/assets/font/Share_Tech_Mono/ShareTechMono-Regular.ttf", 24)
        title_font = pygame.font.Font("game/assets/font/Share_Tech_Mono/ShareTechMono-Regular.ttf", 36)
        
        # Document content
        self.prolog_content = [
            "RESEP RAHASIA RAMBUT ORANYE ",
            "",
            "Bahan-bahan:",
            "- 2 botol cat rambut oranye menyala",
            "- 1 botol pernis kayu",
            "- 3 sendok makan lem kayu",
            "- 1 kaleng hairspray ekstra kuat",
            "- 1 botol jus jeruk (untuk aroma)",
            "",
            "Cara Penggunaan:",
            "1. Campurkan semua bahan dalam mangkuk plastik",
            "2. Aduk hingga konsistensi seperti semen basah",
            "3. Oleskan ke rambut dengan spatula",
            "4. Keringkan dengan kipas angin industri",
            "5. Jangan keramas selama minimal 2 minggu",
            "",
            "PERINGATAN: Hindari hujan, angin kencang, dan pertanyaan jurnalis"
        ]
        
        # Fade effect variables
        fade_alpha = 255
        fade_speed = 3
        fade_in = True
        fade_out = False
        
        # Variables for visual effects
        time_passed = 0
        read_time = 0
        total_read_time = 10000  # 10 seconds to read before guard catches player
        
        # Main loop
        clock = pygame.time.Clock()
        running = True
        
        while running:
            dt = clock.tick(60)
            time_passed += dt
            read_time += dt
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                        fade_out = True
            
            # Handle fade in/out
            if fade_in:
                fade_alpha = max(0, fade_alpha - fade_speed)
                if fade_alpha <= 0:
                    fade_in = False
            
            if fade_out or read_time >= total_read_time:
                fade_alpha = min(255, fade_alpha + fade_speed)
                if fade_alpha >= 255:
                    running = False
            
            # Draw background
            screen.fill((0, 0, 0))
            
            # Create document background
            doc_width, doc_height = 600, 700
            doc_surface = pygame.Surface((doc_width, doc_height), pygame.SRCALPHA)
            doc_surface.fill((255, 250, 240))  # Off-white color for paper
            
            # Add a decorative border
            pygame.draw.rect(doc_surface, (139, 69, 19), (0, 0, doc_width, doc_height), 10)  # Brown border
            
            # Add a title
            title_text = title_font.render(self.prolog_content[0], True, (255, 69, 0))  # Orange color for title
            title_rect = title_text.get_rect(center=(doc_width // 2, 50))
            doc_surface.blit(title_text, title_rect)
            
            # Add document content
            y_offset = 120
            for line in self.prolog_content[1:]:
                if line == "":
                    y_offset += 20  # Add space for empty lines
                    continue
                    
                line_color = (0, 0, 0)  # Default black text
                
                # Highlight important parts
                if "PERINGATAN:" in line:
                    line_color = (255, 0, 0)  # Red for warnings
                elif line.startswith("Bahan-bahan:") or line.startswith("Cara Penggunaan:"):
                    line_color = (0, 0, 128)  # Navy for section headers
                
                text = font.render(line, True, line_color)
                text_rect = text.get_rect(midleft=(40, y_offset))
                doc_surface.blit(text, text_rect)
                y_offset += 30
            
            # Position and draw the document
            doc_rect = doc_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(doc_surface, doc_rect)
            
            # If time is almost up, show the guard catching message
            if read_time >= total_read_time - 3000 and read_time < total_read_time:
                # Create a semi-transparent overlay at the bottom
                warning_surface = pygame.Surface((SCREEN_WIDTH, 100), pygame.SRCALPHA)
                warning_surface.fill((0, 0, 0, 200))
                screen.blit(warning_surface, (0, SCREEN_HEIGHT - 100))
                
                # Show warning message
                warning_text = font.render("*Terdengar langkah kaki mendekat...*", True, (255, 0, 0))
                warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
                screen.blit(warning_text, warning_rect)
            
            # Draw "press space" indicator that blinks
            if (time_passed // 500) % 2 == 0:  # Blink every 500ms
                continue_text = font.render("Tekan SPASI untuk melanjutkan...", True, (255, 255, 255))
                continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
                screen.blit(continue_text, continue_rect)
            
            # Draw fade overlay
            if fade_in or fade_out:
                fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                fade_surface.fill((0, 0, 0, fade_alpha))
                screen.blit(fade_surface, (0, 0))
            
            pygame.display.flip()
        
        # Show caught by guard scene
        self.show_caught_by_guard()
        
        # After document reveal is done, set game as completed
        self.game_manager.game_completed = True
        
        # Resume background music
        pygame.mixer.music.unpause()

    def show_caught_by_guard(self):
        # Setup screen
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Load font
        font = pygame.font.Font("game/assets/font/Share_Tech_Mono/ShareTechMono-Regular.ttf", 36)
        small_font = pygame.font.Font("game/assets/font/Share_Tech_Mono/ShareTechMono-Regular.ttf", 24)
        
        # Fade in
        fade_alpha = 255
        fade_speed = 3
        
        # Main loop for fade in
        clock = pygame.time.Clock()
        running = True
        time_passed = 0
        
        while fade_alpha > 0 and running:
            dt = clock.tick(60)
            time_passed += dt
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                        running = False
            
            # Decrease fade alpha
            fade_alpha = max(0, fade_alpha - fade_speed)
            
            # Draw background
            screen.fill((0, 0, 0))
            
            # Draw guard image (use the same image as in the room)
            try:
                guard_img = pygame.image.load("game/assets/guard_img/trum.png").convert_alpha()
                guard_img = pygame.transform.scale(guard_img, (guard_img.get_width() * 2, guard_img.get_height() * 2))
                guard_rect = guard_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
                screen.blit(guard_img, guard_rect)
            except pygame.error:
                pass  # Skip if image can't be loaded
            
            # Draw caught message
            caught_text = font.render("TERTANGKAP!", True, (255, 0, 0))
            caught_rect = caught_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            screen.blit(caught_text, caught_rect)
            
            # Draw explanation
            explanation_text = small_font.render("Kau mencuri rahasia rambut terpenting di dunia!", True, (255, 255, 255))
            explanation_rect = explanation_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
            screen.blit(explanation_text, explanation_rect)
            
            # Draw fade overlay
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, fade_alpha))
            screen.blit(fade_surface, (0, 0))
            
            pygame.display.flip()
        
        # Hold the scene for a moment
        pygame.time.delay(3000)
        
        # Fade out
        fade_alpha = 0
        while fade_alpha < 255 and running:
            dt = clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                        fade_alpha = 255
            
            # Increase fade alpha
            fade_alpha = min(255, fade_alpha + fade_speed)
            
            # Draw background
            screen.fill((0, 0, 0))
            
            # Draw guard image
            try:
                screen.blit(guard_img, guard_rect)
            except:
                pass
            
            # Draw caught message
            screen.blit(caught_text, caught_rect)
            
            # Draw explanation
            screen.blit(explanation_text, explanation_rect)
            
            # Draw fade overlay
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, fade_alpha))
            screen.blit(fade_surface, (0, 0))
            
            pygame.display.flip()

    def draw_document_found_message(self):
        # Only show a simple notification since we have the full prolog now
        if self.document_timer < 1000:  # Just show for a brief moment
            # Create a semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))  # Black with 100/255 opacity
            
            # Draw message
            font = pygame.font.SysFont(None, 48)
            message = font.render("DOKUMEN RAHASIA DITEMUKAN!", True, (255, 215, 0))
            message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            
            self.screen.blit(overlay, (0, 0))
            self.screen.blit(message, message_rect)
    
    def check_room_transition(self):
        # Check if player is at exit door (left side of room) - lebih ketat
        if (self.player.x < TILE_SIZE // 2 and  # Harus sangat dekat dengan tepi kiri
            self.player.y > 4.5 * TILE_SIZE and self.player.y < 6.5 * TILE_SIZE):  # Area pintu lebih sempit
            # Transition back to room 3
            self.game_manager.transition_to_room(2)
        
            # Position player at bottom exit door of room 3
            self.player.x = 9 * TILE_SIZE
            self.player.y = SCREEN_HEIGHT - TILE_SIZE * 2
    
    def draw(self):
        # Draw background and base objects
        self.draw_tilemap()
        self.draw_objects()
        self.draw_items()
        
        # Draw guards
        for guard in self.guards:
            guard.draw(self.screen)
        
        # Draw player (only if not hiding)
        if not self.player_is_hidden:
            self.player.draw(self.screen)
            self.player.draw_stamina_bar(self.screen)
        
        # Draw collection effects
        self.draw_collection_effects()
        
        # Draw notifications
        self.draw_notifications()
        
        # Draw hiding indicator if player is hiding
        if self.player_is_hidden and self.current_hiding_spot:
            self.draw_hiding_indicator()
        
        # Draw score
        score_text = self.font.render(f"Score: {self.game_manager.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Draw debug info if enabled
        if self.show_debug:
            self.draw_debug_info()
        
        # Apply lighting effect
        self.apply_lighting_effect()
        
        # Draw alarm effect if active
        if self.alarm_triggered:
            self.draw_alarm_effect()
        
        # Draw document found message if document was found
        if self.document_found:
            self.draw_document_found_message()
    
    def apply_lighting_effect(self):
        # Create surface for lighting effect
        self.light_surface.fill((0, 0, 0, 255 - self.ambient_light))
        
        # Create light circle around player if not hiding
        if not self.player_is_hidden:
            player_center_x = int(self.player.x + self.player.width // 2)
            player_center_y = int(self.player.y + self.player.height // 2)
            
            # Create light gradient
            for radius in range(self.light_radius, 0, -1):
                alpha = int(255 * (1 - radius / self.light_radius))
                pygame.draw.circle(self.light_surface, (0, 0, 0, alpha), 
                                  (player_center_x, player_center_y), radius, 1)
        
        # Apply lighting effect to screen
        self.screen.blit(self.light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    
    def draw_alarm_effect(self):
        # Create red flashing effect for alarm
        if (self.alarm_timer // 200) % 2 == 0:  # Flash every 200ms
            alarm_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alarm_surface.fill((255, 0, 0, 30))  # Transparent red
            self.screen.blit(alarm_surface, (0, 0))
            
            # Draw alarm text
            alarm_font = pygame.font.SysFont(None, 48)
            alarm_text = alarm_font.render("! ALARM !", True, (255, 0, 0))
            text_rect = alarm_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
            self.screen.blit(alarm_text, text_rect)

    def cleanup(self):
        """Method to clean up resources when leaving the room"""
        # Stop alarm sound if still playing
        if hasattr(self, 'alarm_sound_played') and self.alarm_sound_played:
            pygame.mixer.stop()
            self.alarm_sound_played = False
