import pygame
import math
import random
from game.utils.constants import *
from game.utils.asset_loader import load_and_transform, get_frames

class HidingSpot:
    def __init__(self, rect, name=""):
        self.rect = rect
        self.name = name
        self.occupied = False
    
    def contains_player(self, player):
        player_rect = player.get_rect()
        return self.rect.colliderect(player_rect) and player.is_crouching

class CollectibleItem:
    def __init__(self, x, y, item_type, shape="circle", color=(255, 255, 0), value=10):
        self.x = x
        self.y = y
        self.item_type = item_type  # "regular" or "key"
        self.shape = shape  # "circle", "square", "diamond", "triangle", "star"
        self.width = 16
        self.height = 16
        self.color = color
        self.value = value  # Value of the item (for score)
        self.collected = False
        self.pulse_timer = 0
        self.pulse_direction = 1
        self.pulse_size = 0
        self.pulse_speed = 0.05
        
        # Variables for magnetic effect
        self.original_x = x
        self.original_y = y
        self.magnetic_radius = 40
        self.is_attracted = False
        self.attraction_speed = 0.15
        self.attraction_progress = 0
        
        # Variables for floating effect
        self.float_offset = random.uniform(0, math.pi * 2)
        self.float_amplitude = 3
        self.float_speed = 0.003
        
        # Variables for rotation effect
        self.rotation_angle = random.uniform(0, 360)
        self.rotation_speed = random.uniform(0.05, 0.2)
        
        # Variables for sparkle effect
        self.sparkle_timer = 0
        self.sparkle_interval = random.uniform(1000, 3000)
        self.sparkle_duration = 300
        self.is_sparkling = False
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def update(self, dt, player=None):
        # Pulsing animation
        self.pulse_timer += dt * self.pulse_speed
        self.pulse_size = math.sin(self.pulse_timer) * 4
        
        # Floating animation
        float_y_offset = math.sin(self.float_offset + dt * self.float_speed) * self.float_amplitude
        
        # Update rotation
        self.rotation_angle = (self.rotation_angle + self.rotation_speed * dt) % 360
        
        # Update sparkle effect
        self.sparkle_timer += dt
        if not self.is_sparkling and self.sparkle_timer >= self.sparkle_interval:
            self.is_sparkling = True
            self.sparkle_timer = 0
        elif self.is_sparkling and self.sparkle_timer >= self.sparkle_duration:
            self.is_sparkling = False
            self.sparkle_timer = 0
            self.sparkle_interval = random.uniform(1000, 3000)
        
        # Magnetic effect when player gets close
        if player and not self.collected and not self.is_attracted:
            player_center_x = player.x + player.width // 2
            player_center_y = player.y + player.height // 2
            item_center_x = self.x + self.width // 2
            item_center_y = self.y + self.height // 2
            
            dx = player_center_x - item_center_x
            dy = player_center_y - item_center_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < self.magnetic_radius:
                self.is_attracted = True
                self.attraction_progress = 0
        
        # If item is being attracted to player
        if self.is_attracted and player and not self.collected:
            self.attraction_progress = min(1.0, self.attraction_progress + self.attraction_speed * (dt / 16.67))
            
            player_center_x = player.x + player.width // 2
            player_center_y = player.y + player.height // 2
            
            eased_progress = self.ease_in_out_cubic(self.attraction_progress)
            
            self.x = self.original_x + (player_center_x - self.width // 2 - self.original_x) * eased_progress
            self.y = self.original_y + (player_center_y - self.height // 2 - self.original_y) * eased_progress
            
            if self.attraction_progress >= 0.95:
                self.collected = True
                return True
        
        # Apply floating offset if not being attracted
        if not self.is_attracted:
            self.y = self.original_y + float_y_offset
            
        return False
    
    def ease_in_out_cubic(self, x):
        if x < 0.5:
            return 4 * x * x * x
        else:
            return 1 - pow(-2 * x + 2, 3) / 2
        
    def draw(self, surface):
        if not self.collected:
            # Center position of the item
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            
            # Base size with pulse effect
            size_mod = int(self.pulse_size)
            base_size = self.width // 2 + size_mod
            
            # Base color and sparkle color
            base_color = self.color
            sparkle_color = (255, 255, 255)
            
            # If sparkling, blend colors
            if self.is_sparkling:
                sparkle_intensity = min(1.0, self.sparkle_timer / (self.sparkle_duration * 0.5))
                if self.sparkle_timer > self.sparkle_duration * 0.5:
                    sparkle_intensity = 1.0 - ((self.sparkle_timer - self.sparkle_duration * 0.5) / (self.sparkle_duration * 0.5))
                
                r = min(255, int(base_color[0] + (sparkle_color[0] - base_color[0]) * sparkle_intensity))
                g = min(255, int(base_color[1] + (sparkle_color[1] - base_color[1]) * sparkle_intensity))
                b = min(255, int(base_color[2] + (sparkle_color[2] - base_color[2]) * sparkle_intensity))
                
                current_color = (r, g, b)
            else:
                current_color = base_color
            
            # Draw shape based on type
            if self.item_type == "key":
                # Draw key (simple shape)
                key_surface = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
                pygame.draw.rect(key_surface, current_color, (5, 10, 15, 5))
                pygame.draw.circle(key_surface, current_color, (15, 7), 7)
                pygame.draw.circle(key_surface, (0, 0, 0), (15, 7), 3)
                rotated_key = pygame.transform.rotate(key_surface, self.rotation_angle)
                key_rect = rotated_key.get_rect(center=(center_x, center_y))
                surface.blit(rotated_key, key_rect.topleft)
            elif self.shape == "circle":
                pygame.draw.circle(surface, current_color, (center_x, center_y), base_size)
                pygame.draw.circle(surface, (255, 255, 255), 
                                  (center_x - base_size//3, center_y - base_size//3), 
                                  base_size//4)
            elif self.shape == "square":
                pygame.draw.rect(surface, current_color, 
                               (center_x - base_size, center_y - base_size, 
                                base_size*2, base_size*2))
                pygame.draw.circle(surface, (255, 255, 255), 
                                  (center_x - base_size//2, center_y - base_size//2), 
                                  base_size//4)
            elif self.shape == "diamond":
                points = [
                    (center_x, center_y - base_size),
                    (center_x + base_size, center_y),
                    (center_x, center_y + base_size),
                    (center_x - base_size, center_y)
                ]
                pygame.draw.polygon(surface, current_color, points)
                pygame.draw.circle(surface, (255, 255, 255), 
                                  (center_x - base_size//3, center_y - base_size//3), 
                                  base_size//4)
            elif self.shape == "triangle":
                points = [
                    (center_x, center_y - base_size),
                    (center_x + base_size, center_y + base_size),
                    (center_x - base_size, center_y + base_size)
                ]
                pygame.draw.polygon(surface, current_color, points)
                pygame.draw.circle(surface, (255, 255, 255), 
                                  (center_x - base_size//3, center_y - base_size//3), 
                                  base_size//4)
            elif self.shape == "star":
                # Draw a simple star
                points = []
                for i in range(10):
                    angle = math.pi/2 + (2*math.pi * i / 10)
                    radius = base_size if i % 2 == 0 else base_size/2
                    x = center_x + radius * math.cos(angle)
                    y = center_y + radius * math.sin(angle)
                    points.append((x, y))
                pygame.draw.polygon(surface, current_color, points)
                pygame.draw.circle(surface, (255, 255, 255), 
                                  (center_x - base_size//3, center_y - base_size//3), 
                                  base_size//4)

class BaseRoom:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.screen = game_manager.screen
        self.player = game_manager.player
        self.clock = game_manager.clock
        
        # Initialize base variables
        self.tiles = {}
        self.objects = {}
        self.object_positions = []
        self.colliders = []
        self.hiding_spots = []
        self.guards = []
        self.collectible_items = []
        self.collection_effects = []
        self.notifications = []
        self.last_positions_before_hiding = {}
        
        # Player hiding state
        self.player_is_hidden = False
        self.current_hiding_spot = None
        
        # Room status
        self.all_items_collected = False
        self.key_spawned = False
        self.key_collected = False
        self.door_opened = False
        
        # Variables for sound effects
        self.footstep_timer = 0
        self.footstep_interval = 300
        self.player_noise_level = 0
        
        # Variables for debug
        self.show_debug = False
        
        # Font for UI
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 72)
        
        # Initialize room
        self.load_assets()
        self.setup_room()
    
    def load_assets(self):
        """
        Load all assets needed for this room.
        Implementation in derived class.
        """
        pass
    
    def setup_room(self):
        """
        Setup room with tilemap, objects, colliders, etc.
        Implementation in derived class.
        """
        pass
    
    def update(self, dt, mouse_held, mouse_pos):
        """
        Update all elements in the room
        """
        # Update player
        old_x, old_y = self.player.x, self.player.y
        self.player.update(dt, mouse_held, mouse_pos, self.colliders)
        
        # Calculate player noise level
        self.update_player_noise(dt, old_x, old_y)
        
        # Check if player is hiding
        self.check_player_hiding()
        
        # Update items
        self.update_items(dt)
        
        # Update collection effects
        self.update_collection_effects(dt)
        
        # Update notifications
        self.update_notifications(dt)
        
        # Update guards
        self.update_guards(dt)
        
        # Check room transition
        self.check_room_transition()
    
    def update_player_noise(self, dt, old_x, old_y):
        if self.player.x != old_x or self.player.y != old_y:
            # Noise level based on speed
            if self.player.speed >= RUN_SPEED:
                self.player_noise_level = 100  # Running is very noisy
            elif self.player.is_crouching:
                self.player_noise_level = 20   # Crouching is very quiet
            else:
                self.player_noise_level = 50   # Normal walking
                
            # Play footstep sound if it's time
            self.footstep_timer += dt
            if self.footstep_timer >= self.footstep_interval:
                # Here you could add code to play footstep sound
                # pygame.mixer.Sound("game/assets/sound/footstep.wav").play()
                self.footstep_timer = 0
        else:
            # If player is not moving, no noise
            self.player_noise_level = 0
    
    def check_player_hiding(self):
        self.player_is_hidden = False
        self.current_hiding_spot = None
        
        for spot in self.hiding_spots:
            if spot.contains_player(self.player):
                # If player just started hiding in this spot, save position
                if not self.player_is_hidden and spot.name not in self.last_positions_before_hiding:
                    self.last_positions_before_hiding[spot.name] = (self.player.x, self.player.y)
                
                self.player_is_hidden = True
                self.current_hiding_spot = spot
                break
    
    def update_items(self, dt):
        for item in self.collectible_items:
            if item.update(dt, self.player):
                # Item has been collected via magnetic effect
                # Add score
                self.game_manager.score += item.value
                
                # Add notification
                self.add_notification(f"+{item.value}", item.color, item.x, item.y - 20)
                
                # Add collection effect
                self.add_collection_effect(item.x + item.width//2, item.y + item.height//2, item.color)
                
                # Check if all regular items have been collected
                regular_items = [i for i in self.collectible_items if i.item_type == "regular"]
                if len(regular_items) > 0 and all(i.collected for i in regular_items) and not self.key_spawned:
                    self.spawn_key()
                    self.key_spawned = True
                    self.add_notification("Key has appeared!", (255, 215, 0), SCREEN_WIDTH // 2, 100, velocity=0)
                
                # Check if key has been collected
                key_items = [i for i in self.collectible_items if i.item_type == "key"]
                if key_items and key_items[0].collected and not self.door_opened:
                    self.open_door()
                    self.door_opened = True
                    self.add_notification("Door has opened!", (0, 255, 0), SCREEN_WIDTH // 2, 100, velocity=0)
    
    def update_collection_effects(self, dt):
        for effect in self.collection_effects[:]:
            effect["timer"] += dt
            
            for particle in effect["particles"]:
                particle["dx"] *= 0.95
                particle["dy"] *= 0.95
                particle["alpha"] = max(0, particle["alpha"] - 5)
                
            if effect["timer"] >= effect["duration"]:
                self.collection_effects.remove(effect)
    
    def update_notifications(self, dt):
        for notification in self.notifications[:]:
            notification["timer"] += dt
            notification["y"] += notification["velocity"] * dt / 16.67
            
            if notification["timer"] >= notification["duration"]:
                self.notifications.remove(notification)
    
    def update_guards(self, dt):
        for guard in self.guards:
            guard.update(dt, self.player, self.guards, self.hiding_spots)
            
            # Check if guard catches player
            if guard.state == "chase" and not self.player_is_hidden:
                # Calculate distance to player
                player_center_x = self.player.x + self.player.width // 2
                player_center_y = self.player.y + self.player.height // 2
                guard_center_x = guard.x + guard.width // 2
                guard_center_y = guard.y + guard.height // 2
                
                dx = player_center_x - guard_center_x
                dy = player_center_y - guard_center_y
                distance = (dx**2 + dy**2)**0.5
                
                # If guard is close enough to player, game over
                if distance < 30:
                    # Gunakan metode set_game_over yang baru
                    self.game_manager.set_game_over()
    
    def check_room_transition(self):
        """
        Check if player is in position to transition to another room.
        Implementation in derived class.
        """
        pass
    
    def spawn_key(self):
        """
        Spawn key in the room.
        Implementation in derived class.
        """
        pass
    
    def open_door(self):
        """
        Open door in the room.
        Implementation in derived class.
        """
        pass
    
    def add_notification(self, text, color, x, y, duration=1000, velocity=-0.5):
        self.notifications.append({
            "text": text,
            "color": color,
            "x": x,
            "y": y,
            "timer": 0,
            "duration": duration,
            "velocity": velocity
        })
    
    def add_collection_effect(self, x, y, color):
        self.collection_effects.append({
            "x": x,
            "y": y,
            "color": color,
            "particles": [],
            "timer": 0,
            "duration": 500
        })
        
        # Create particles
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2.0)
            size = random.randint(2, 5)
            self.collection_effects[-1]["particles"].append({
                "dx": math.cos(angle) * speed,
                "dy": math.sin(angle) * speed,
                "size": size,
                "alpha": 255
            })
    
    def draw(self):
        """
        Draw all elements in the room
        """
        # Draw tilemap and objects
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
        
        #Draw score
        score_text = self.font.render(f"Score: {self.game_manager.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Draw debug info if enabled
        if self.show_debug:
            self.draw_debug_info()
    
    def draw_tilemap(self):
        for y, row in enumerate(self.tilemap):
            for x, tile_id in enumerate(row):
                self.screen.blit(self.tiles[tile_id], (x * TILE_SIZE, y * TILE_SIZE))
    
    def draw_objects(self):
        for obj in self.object_positions:
            self.screen.blit(obj["img"], (obj["x"] * TILE_SIZE, obj["y"] * TILE_SIZE))
    
    def draw_items(self):
        for item in self.collectible_items:
            item.draw(self.screen)
    
    def draw_collection_effects(self):
        for effect in self.collection_effects:
            for particle in effect["particles"]:
                if particle["alpha"] > 0:
                    color = effect["color"] + (particle["alpha"],)
                    px = effect["x"] + particle["dx"] * effect["timer"] / 16.67
                    py = effect["y"] + particle["dy"] * effect["timer"] / 16.67
                    pygame.draw.circle(self.screen, color, (int(px), int(py)), particle["size"])
    
    def draw_notifications(self):
        for notification in self.notifications:
            alpha = 255
            if notification["timer"] < 300:
                alpha = int(255 * notification["timer"] / 300)
            elif notification["timer"] > notification["duration"] - 300:
                alpha = int(255 * (notification["duration"] - notification["timer"]) / 300)
            
            color = notification["color"] + (alpha,)
            notification_font = pygame.font.SysFont(None, 24)
            text_surface = notification_font.render(notification["text"], True, color)
            text_rect = text_surface.get_rect(center=(notification["x"], notification["y"]))
            
            alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
            alpha_surface.fill((255, 255, 255, alpha))
            
            text_surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(text_surface, text_rect)
    
    def draw_hiding_indicator(self):
        font = pygame.font.SysFont(None, 24)
        text = font.render("HIDDEN", True, (0, 255, 0))
        text_rect = text.get_rect(center=(self.current_hiding_spot.rect.centerx, self.current_hiding_spot.rect.top - 20))
        self.screen.blit(text, text_rect)
    
    def draw_debug_info(self):
        y_offset = 40
        # Display guard info
        for i, guard in enumerate(self.guards):
            text = f"Guard {i+1}: {guard.guard_type} - {guard.state}"
            text_surf = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surf, (10, y_offset))
            y_offset += 25
        
        # Display player state
        state_text = f"Player State: {'Crouching' if self.player.is_crouching else 'Standing'}"
        speed_text = f"Speed: {self.player.speed:.1f}"
        stealth_text = f"Stealth Bonus: {self.player.stealth_bonus}"
        noise_text = f"Noise Level: {self.player_noise_level}"
        hidden_text = f"Hidden: {self.player_is_hidden}"
        stamina_text = f"Stamina: {self.player.stamina:.1f}/{self.player.max_stamina}"
        exhausted_text = f"Exhausted: {self.player.is_exhausted}"
        
        state_surf = self.font.render(state_text, True, (255, 255, 255))
        speed_surf = self.font.render(speed_text, True, (255, 255, 255))
        stealth_surf = self.font.render(stealth_text, True, (255, 255, 255))
        noise_surf = self.font.render(noise_text, True, (255, 255, 255))
        hidden_surf = self.font.render(hidden_text, True, (255, 255, 255))
        stamina_surf = self.font.render(stamina_text, True, (255, 255, 255))
        exhausted_surf = self.font.render(exhausted_text, True, (255, 255, 255))
        
        self.screen.blit(state_surf, (10, y_offset))
        self.screen.blit(speed_surf, (10, y_offset + 25))
        self.screen.blit(stealth_surf, (10, y_offset + 50))
        self.screen.blit(noise_surf, (10, y_offset + 75))
        self.screen.blit(hidden_surf, (10, y_offset + 100))
        self.screen.blit(stamina_surf, (10, y_offset + 125))
        self.screen.blit(exhausted_surf, (10, y_offset + 150))
        
        # Draw hiding spot rectangles for debugging
        for spot in self.hiding_spots:
            pygame.draw.rect(surface=self.screen, color=(0, 255, 0, 128), 
                            rect=spot.rect, width=2)
            
        # Draw item collection status
        items_text = f"Items: {sum(1 for item in self.collectible_items if item.collected)}/{len(self.collectible_items)}"
        key_text = f"Key Spawned: {self.key_spawned}, Key Collected: {self.key_collected}"
        door_text = f"Door Opened: {self.door_opened}"
        
        items_surf = self.font.render(items_text, True, (255, 255, 255))
        key_surf = self.font.render(key_text, True, (255, 255, 255))
        door_surf = self.font.render(door_text, True, (255, 255, 255))
        
        self.screen.blit(items_surf, (10, y_offset + 175))
        self.screen.blit(key_surf, (10, y_offset + 200))
        self.screen.blit(door_surf, (10, y_offset + 225))
        
        # Draw magnetic radius for debugging
        for item in self.collectible_items:
            if not item.collected:
                pygame.draw.circle(surface=self.screen, color=(255, 255, 255, 30), 
                                  center=(item.x + item.width//2, item.y + item.height//2), 
                                  radius=item.magnetic_radius, width=1)
