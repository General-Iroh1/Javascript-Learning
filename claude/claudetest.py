import tkinter as tk
import time
import random
import math

class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("WASD Movement Game")

        # Make fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", lambda _: self.root.attributes('-fullscreen', False))

        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Create canvas
        self.canvas = tk.Canvas(root, width=self.screen_width, height=self.screen_height, bg="lightblue")
        self.canvas.pack()

        # Player position (center of screen)
        self.player_x = self.screen_width // 2
        self.player_y = self.screen_height // 2
        self.player_speed = 5

        # Create simple colored rectangles as placeholders for images
        # Main player (larger rectangle)
        self.player = self.canvas.create_rectangle(
            self.player_x - 25, self.player_y - 25,
            self.player_x + 25, self.player_y + 25,
            fill="blue", outline="darkblue", width=2
        )

        # Create kill counter text
        self.kill_counter_text = self.canvas.create_text(
            100, 30,
            text="Kills: 0",
            font=("Arial", 28, "bold"),
            fill="white",
            anchor="w"
        )

        # Create wave counter text
        self.wave_counter_text = self.canvas.create_text(
            100, 65,
            text="Wave: 1",
            font=("Arial", 28, "bold"),
            fill="white",
            anchor="w"
        )

        # List to store projectiles
        self.projectiles = []

        # List to store enemies
        self.enemies = []

        # Enemy spawn settings
        self.enemy_spawn_cooldown = 2000  # 2 seconds
        self.last_enemy_spawn = 0
        self.enemy_speed = self.player_speed / 2

        # Track which keys are currently pressed
        self.keys_pressed = set()

        # Shooting cooldown (in milliseconds)
        self.shoot_cooldown = 200  # 0.2 seconds
        self.last_shoot_time = 0

        # Game state
        self.game_over = False
        self.shop_open = False

        # Score tracking
        self.enemies_killed = 0
        self.wave_number = 1
        self.enemies_killed_this_wave = 0

        # Upgrades
        self.bullet_speed_multiplier = 1.0
        self.bazooka_level = 0  # 0 = no bazooka, 1 = opposite direction, 2 = random direction
        self.player_speed_multiplier = 1.0
        self.bullet_damage = 1.0
        self.bullet_color_level = 0  # 0=yellow, 1=dark blue, 2=purple, 3=turquoise, 4=black

        # Player health
        self.player_max_hp = 1
        self.player_current_hp = 1

        # Create HP counter text (after HP variables are initialized)
        self.hp_counter_text = self.canvas.create_text(
            100, 100,
            text=f"HP: {self.player_current_hp}/{self.player_max_hp}",
            font=("Arial", 28, "bold"),
            fill="green",
            anchor="w"
        )

        # Create testing button (adds 20 kills)
        test_button_x = self.screen_width - 150
        test_button_y = 50
        self.test_button = self.canvas.create_rectangle(
            test_button_x - 80, test_button_y - 25,
            test_button_x + 80, test_button_y + 25,
            fill="purple", outline="white", width=2
        )
        self.test_button_text = self.canvas.create_text(
            test_button_x, test_button_y,
            text="+20 Kills",
            font=("Arial", 18, "bold"),
            fill="white"
        )

        # Bind click event for test button
        self.canvas.tag_bind(self.test_button, "<Button-1>", self.add_test_kills)
        self.canvas.tag_bind(self.test_button_text, "<Button-1>", self.add_test_kills)

        # Enemy stats
        self.enemy_max_health = 1
        self.enemy_speed_multiplier = 1.0
        self.shop_count = 0
        self.last_shop_kills = 0  # Track when last shop was opened
        self.last_boss_spawn_kills = 0  # Track when last boss was spawned

        # Boss tracking
        self.boss_number = 0
        self.current_boss = None
        self.current_boss_index = -1
        self.boss_last_shoot = 0
        self.boss_shoot_cooldown = 2000  # 2 seconds
        self.boss_spawn_time = 0
        self.boss_last_special = 0
        self.boss_special_cooldown = 10000  # 10 seconds

        # Bind keys for press and release
        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)

        # Start game loop
        self.update_game()

    def key_press(self, event):
        key = event.keysym.lower()

        # Add key to pressed set for continuous movement
        if key in ['w', 'a', 's', 'd']:
            self.keys_pressed.add(key)

        # For arrow keys, remove opposite directions to allow direction changes
        if key == 'up':
            self.keys_pressed.discard('down')
            self.keys_pressed.add('up')
        elif key == 'down':
            self.keys_pressed.discard('up')
            self.keys_pressed.add('down')
        elif key == 'left':
            self.keys_pressed.discard('right')
            self.keys_pressed.add('left')
        elif key == 'right':
            self.keys_pressed.discard('left')
            self.keys_pressed.add('right')

    def key_release(self, event):
        key = event.keysym.lower()
        # Remove key from pressed set
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def add_test_kills(self, event=None):
        # Add 20 kills for testing
        self.enemies_killed += 20
        self.enemies_killed_this_wave += 20

    def shoot_projectile(self, dx, dy):
        # Get bullet color based on upgrade level
        bullet_colors = [
            ("yellow", "orange"),
            ("darkblue", "blue"),
            ("purple", "darkviolet"),
            ("turquoise", "cyan"),
            ("black", "gray")
        ]
        fill_color, outline_color = bullet_colors[min(self.bullet_color_level, 4)]

        # Create colored oval (rounded) as projectile
        projectile = self.canvas.create_oval(
            self.player_x - 8, self.player_y - 8,
            self.player_x + 8, self.player_y + 8,
            fill=fill_color, outline=outline_color, width=2
        )

        # Store projectile info: [canvas_id, x, y, dx, dy]
        base_speed = 8 * self.bullet_speed_multiplier
        self.projectiles.append([projectile, self.player_x, self.player_y, dx * base_speed, dy * base_speed])

        # If bazooka upgrade level 1, shoot extra bullet in opposite direction
        if self.bazooka_level == 1:
            projectile_back = self.canvas.create_oval(
                self.player_x - 8, self.player_y - 8,
                self.player_x + 8, self.player_y + 8,
                fill=fill_color, outline=outline_color, width=2
            )
            self.projectiles.append([projectile_back, self.player_x, self.player_y, -dx * base_speed, -dy * base_speed])

        # If bazooka upgrade level 2, shoot extra bullet in random direction
        elif self.bazooka_level >= 2:
            # Shoot opposite direction bullet
            projectile_back = self.canvas.create_oval(
                self.player_x - 8, self.player_y - 8,
                self.player_x + 8, self.player_y + 8,
                fill=fill_color, outline=outline_color, width=2
            )
            self.projectiles.append([projectile_back, self.player_x, self.player_y, -dx * base_speed, -dy * base_speed])

            # Shoot random direction bullet
            random_angle = random.uniform(0, 2 * math.pi)
            random_dx = math.cos(random_angle)
            random_dy = math.sin(random_angle)

            projectile_random = self.canvas.create_oval(
                self.player_x - 8, self.player_y - 8,
                self.player_x + 8, self.player_y + 8,
                fill=fill_color, outline=outline_color, width=2
            )
            self.projectiles.append([projectile_random, self.player_x, self.player_y, random_dx * base_speed, random_dy * base_speed])

    def boss_rush_attack(self, boss_idx, start_x=None, start_y=None):
        # Check if boss still exists
        if boss_idx >= len(self.enemies) or not self.enemies[boss_idx][4]:
            return

        # Remove telegraph icon
        if self.enemies[boss_idx][6] is not None:
            self.canvas.delete(self.enemies[boss_idx][6])
            self.enemies[boss_idx][6] = None

        # Move boss to center
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        self.enemies[boss_idx][1] = center_x
        self.enemies[boss_idx][2] = center_y

        # Update canvas position
        self.canvas.coords(
            self.enemies[boss_idx][0],
            center_x - 40, center_y - 40,
            center_x + 40, center_y + 40
        )

        # Shoot projectiles in 8 directions
        directions = [
            (0, -1),   # Up
            (1, -1),   # Up-right
            (1, 0),    # Right
            (1, 1),    # Down-right
            (0, 1),    # Down
            (-1, 1),   # Down-left
            (-1, 0),   # Left
            (-1, -1)   # Up-left
        ]

        for dx, dy in directions:
            boss_projectile = self.canvas.create_oval(
                center_x - 6, center_y - 6,
                center_x + 6, center_y + 6,
                fill="orange", outline="red", width=2
            )
            self.projectiles.append([boss_projectile, center_x, center_y, dx * 10, dy * 10, True])

    def boss_summon_attack(self, boss_idx):
        # Check if boss still exists
        if boss_idx >= len(self.enemies) or not self.enemies[boss_idx][4]:
            return

        # Remove telegraph icon
        if self.enemies[boss_idx][6] is not None:
            self.canvas.delete(self.enemies[boss_idx][6])
            self.enemies[boss_idx][6] = None

        # Get boss position
        boss_x = self.enemies[boss_idx][1]
        boss_y = self.enemies[boss_idx][2]

        # Spawn enemy near boss
        spawn_offset = 100
        x = boss_x + random.choice([-spawn_offset, spawn_offset])
        y = boss_y + random.choice([-spawn_offset, spawn_offset])

        # Keep within screen bounds
        x = max(50, min(x, self.screen_width - 50))
        y = max(50, min(y, self.screen_height - 50))

        # Create red square enemy
        enemy = self.canvas.create_rectangle(
            x - 20, y - 20,
            x + 20, y + 20,
            fill="red", outline="darkred", width=2
        )

        # Store enemy info with 3 HP: [canvas_id, x, y, health, is_boss, boss_level, telegraph_icon]
        self.enemies.append([enemy, x, y, 3, False, 0, None])

    def spawn_boss(self):
        # Spawn boss at random edge of screen
        edge = random.choice(['top', 'bottom', 'left', 'right'])

        if edge == 'top':
            x = random.randint(100, self.screen_width - 100)
            y = 100
        elif edge == 'bottom':
            x = random.randint(100, self.screen_width - 100)
            y = self.screen_height - 100
        elif edge == 'left':
            x = 100
            y = random.randint(100, self.screen_height - 100)
        else:  # right
            x = self.screen_width - 100
            y = random.randint(100, self.screen_height - 100)

        # Calculate boss health (50, 100, 200, 400, ...)
        boss_health = 50 * (2 ** self.boss_number)

        # Create large red boss square
        boss = self.canvas.create_rectangle(
            x - 40, y - 40,
            x + 40, y + 40,
            fill="darkred", outline="red", width=4
        )

        # Store boss info: [canvas_id, x, y, health, is_boss, boss_level, telegraph_icon]
        # boss_level: 0=first boss (projectiles only), 1=second boss (adds rush attack), 2+=third boss (adds summon)
        self.current_boss = [boss, x, y, boss_health, True, self.boss_number, None]
        self.enemies.append(self.current_boss)
        self.current_boss_index = len(self.enemies) - 1
        self.boss_spawn_time = time.time() * 1000
        self.boss_last_special = self.boss_spawn_time

    def spawn_enemy(self):
        # Spawn enemy at random edge of screen
        edge = random.choice(['top', 'bottom', 'left', 'right'])

        if edge == 'top':
            x = random.randint(50, self.screen_width - 50)
            y = 50
        elif edge == 'bottom':
            x = random.randint(50, self.screen_width - 50)
            y = self.screen_height - 50
        elif edge == 'left':
            x = 50
            y = random.randint(50, self.screen_height - 50)
        else:  # right
            x = self.screen_width - 50
            y = random.randint(50, self.screen_height - 50)

        # Create red square enemy
        enemy = self.canvas.create_rectangle(
            x - 20, y - 20,
            x + 20, y + 20,
            fill="red", outline="darkred", width=2
        )

        # Store enemy info: [canvas_id, x, y, health, is_boss, boss_level, telegraph_icon]
        self.enemies.append([enemy, x, y, self.enemy_max_health, False, 0, None])

    def show_game_over(self):
        # Display game over screen
        self.game_over = True

        # Create semi-transparent overlay
        overlay = self.canvas.create_rectangle(
            0, 0, self.screen_width, self.screen_height,
            fill="black", stipple="gray50"
        )

        # Game Over text
        game_over_text = self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 2 - 150,
            text="GAME OVER",
            font=("Arial", 72, "bold"),
            fill="red"
        )

        # Kill count text
        kill_text = self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 2 - 50,
            text=f"You died! You had {self.enemies_killed} kills!",
            font=("Arial", 36, "bold"),
            fill="white"
        )

        # Create retry button
        button_width = 200
        button_height = 60
        button_x = self.screen_width // 2
        button_y = self.screen_height // 2 + 50

        retry_button = self.canvas.create_rectangle(
            button_x - button_width // 2, button_y - button_height // 2,
            button_x + button_width // 2, button_y + button_height // 2,
            fill="green", outline="darkgreen", width=3
        )

        retry_text = self.canvas.create_text(
            button_x, button_y,
            text="RETRY",
            font=("Arial", 24, "bold"),
            fill="white"
        )

        # Bind click event to retry button
        def on_click(event):
            click_x, click_y = event.x, event.y
            if (button_x - button_width // 2 <= click_x <= button_x + button_width // 2 and
                button_y - button_height // 2 <= click_y <= button_y + button_height // 2):
                self.restart_game()

        self.canvas.bind("<Button-1>", on_click)

    def restart_game(self):
        # Clear canvas
        self.canvas.delete("all")

        # Reset player position
        self.player_x = self.screen_width // 2
        self.player_y = self.screen_height // 2

        # Recreate kill counter
        self.kill_counter_text = self.canvas.create_text(
            100, 30,
            text="Kills: 0",
            font=("Arial", 28, "bold"),
            fill="white",
            anchor="w"
        )

        # Recreate wave counter
        self.wave_counter_text = self.canvas.create_text(
            100, 65,
            text="Wave: 1",
            font=("Arial", 28, "bold"),
            fill="white",
            anchor="w"
        )

        # Recreate HP counter
        self.hp_counter_text = self.canvas.create_text(
            100, 100,
            text=f"HP: {self.player_current_hp}/{self.player_max_hp}",
            font=("Arial", 28, "bold"),
            fill="green",
            anchor="w"
        )

        # Recreate testing button
        test_button_x = self.screen_width - 150
        test_button_y = 50
        self.test_button = self.canvas.create_rectangle(
            test_button_x - 80, test_button_y - 25,
            test_button_x + 80, test_button_y + 25,
            fill="purple", outline="white", width=2
        )
        self.test_button_text = self.canvas.create_text(
            test_button_x, test_button_y,
            text="+20 Kills",
            font=("Arial", 18, "bold"),
            fill="white"
        )
        self.canvas.tag_bind(self.test_button, "<Button-1>", self.add_test_kills)
        self.canvas.tag_bind(self.test_button_text, "<Button-1>", self.add_test_kills)

        # Recreate player
        self.player = self.canvas.create_rectangle(
            self.player_x - 25, self.player_y - 25,
            self.player_x + 25, self.player_y + 25,
            fill="blue", outline="darkblue", width=2
        )

        # Clear all game objects
        self.projectiles = []
        self.enemies = []

        # Reset timers to current time to prevent immediate spawns/shots
        current_time = time.time() * 1000
        self.last_shoot_time = current_time
        self.last_enemy_spawn = current_time

        # Reset game state
        self.game_over = False
        self.keys_pressed = set()

        # Reset score and upgrades
        self.enemies_killed = 0
        self.wave_number = 1
        self.enemies_killed_this_wave = 0
        self.bullet_speed_multiplier = 1.0
        self.bazooka_level = 0
        self.player_speed_multiplier = 1.0
        self.bullet_damage = 1.0
        self.bullet_color_level = 0
        self.shop_open = False
        self.enemy_max_health = 1
        self.enemy_speed_multiplier = 1.0
        self.shop_count = 0
        self.boss_number = 0
        self.current_boss = None
        self.boss_last_shoot = 0
        self.player_max_hp = 1
        self.player_current_hp = 1
        self.last_shop_kills = 0
        self.last_boss_spawn_kills = 0

        # Unbind click event
        self.canvas.unbind("<Button-1>")

        # Restart the game loop
        self.update_game()

    def show_shop(self):
        # Pause game
        self.shop_open = True

        # Create semi-transparent overlay
        self.canvas.create_rectangle(
            0, 0, self.screen_width, self.screen_height,
            fill="black", stipple="gray50"
        )

        # Shop title
        self.canvas.create_text(
            self.screen_width // 2, 100,
            text="SHOP - Choose an Upgrade",
            font=("Arial", 48, "bold"),
            fill="gold"
        )

        # Shop items
        button_width = 280
        button_height = 140
        spacing = 310
        start_x = (self.screen_width - (spacing * 4)) // 2

        # Faster Gun Button
        gun_x = start_x
        gun_y = self.screen_height // 2

        gun_button = self.canvas.create_rectangle(
            gun_x, gun_y - button_height // 2,
            gun_x + button_width, gun_y + button_height // 2,
            fill="cyan", outline="blue", width=3
        )

        self.canvas.create_text(
            gun_x + button_width // 2, gun_y - 30,
            text="Faster Gun",
            font=("Arial", 24, "bold"),
            fill="black"
        )

        self.canvas.create_text(
            gun_x + button_width // 2, gun_y + 20,
            text="Increases\nbullet speed\nby 50%",
            font=("Arial", 16),
            fill="black"
        )

        # Bazooka Button
        bazooka_x = start_x + spacing
        bazooka_y = self.screen_height // 2

        bazooka_button = self.canvas.create_rectangle(
            bazooka_x, bazooka_y - button_height // 2,
            bazooka_x + button_width, bazooka_y + button_height // 2,
            fill="orange", outline="red", width=3
        )

        bazooka_title = "Bazooka" if self.bazooka_level == 0 else f"Bazooka (Lvl {self.bazooka_level})"
        self.canvas.create_text(
            bazooka_x + button_width // 2, bazooka_y - 30,
            text=bazooka_title,
            font=("Arial", 24, "bold"),
            fill="black"
        )

        if self.bazooka_level == 0:
            bazooka_desc = "Shoot extra\nbullet in\nopposite direction"
        else:
            bazooka_desc = "Add bullet in\nrandom direction"

        self.canvas.create_text(
            bazooka_x + button_width // 2, bazooka_y + 20,
            text=bazooka_desc,
            font=("Arial", 16),
            fill="black"
        )

        # Shoes Button
        shoes_x = start_x + spacing * 2
        shoes_y = self.screen_height // 2

        shoes_button = self.canvas.create_rectangle(
            shoes_x, shoes_y - button_height // 2,
            shoes_x + button_width, shoes_y + button_height // 2,
            fill="lime", outline="green", width=3
        )

        self.canvas.create_text(
            shoes_x + button_width // 2, shoes_y - 30,
            text="Shoes",
            font=("Arial", 24, "bold"),
            fill="black"
        )

        self.canvas.create_text(
            shoes_x + button_width // 2, shoes_y + 20,
            text="Increases\nmovement speed\nby 50%",
            font=("Arial", 16),
            fill="black"
        )

        # Bullet Color Button
        color_x = start_x + spacing * 3
        color_y = self.screen_height // 2

        # Determine color button appearance based on level
        color_levels = ["yellow", "darkblue", "purple", "turquoise", "black"]
        current_color = color_levels[min(self.bullet_color_level, 4)]

        color_button = self.canvas.create_rectangle(
            color_x, color_y - button_height // 2,
            color_x + button_width, color_y + button_height // 2,
            fill=current_color if current_color != "black" else "gray",
            outline="gold", width=3
        )

        color_title = "Bullet Power" if self.bullet_color_level == 0 else f"Bullet Power (Lvl {self.bullet_color_level})"
        text_color = "white" if current_color in ["darkblue", "purple", "black"] else "black"

        self.canvas.create_text(
            color_x + button_width // 2, color_y - 30,
            text=color_title,
            font=("Arial", 22, "bold"),
            fill=text_color
        )

        self.canvas.create_text(
            color_x + button_width // 2, color_y + 20,
            text="Increases damage\nby 0.5 and changes\nbullet color",
            font=("Arial", 14),
            fill=text_color
        )

        # HP Upgrade Button
        hp_x = start_x + spacing * 4
        hp_y = self.screen_height // 2

        hp_button = self.canvas.create_rectangle(
            hp_x, hp_y - button_height // 2,
            hp_x + button_width, hp_y + button_height // 2,
            fill="pink", outline="red", width=3
        )

        self.canvas.create_text(
            hp_x + button_width // 2, hp_y - 30,
            text="Heart",
            font=("Arial", 24, "bold"),
            fill="black"
        )

        self.canvas.create_text(
            hp_x + button_width // 2, hp_y + 20,
            text="Adds 1 HP\nTank a hit from\nenemy or projectile",
            font=("Arial", 16),
            fill="black"
        )

        # Bind click event to shop buttons
        def on_shop_click(event):
            click_x, click_y = event.x, event.y

            # Check gun button
            if (gun_x <= click_x <= gun_x + button_width and
                gun_y - button_height // 2 <= click_y <= gun_y + button_height // 2):
                self.bullet_speed_multiplier += 0.5
                self.close_shop()

            # Check bazooka button
            elif (bazooka_x <= click_x <= bazooka_x + button_width and
                  bazooka_y - button_height // 2 <= click_y <= bazooka_y + button_height // 2):
                self.bazooka_level += 1
                self.close_shop()

            # Check shoes button
            elif (shoes_x <= click_x <= shoes_x + button_width and
                  shoes_y - button_height // 2 <= click_y <= shoes_y + button_height // 2):
                self.player_speed_multiplier += 0.5
                self.close_shop()

            # Check bullet color button
            elif (color_x <= click_x <= color_x + button_width and
                  color_y - button_height // 2 <= click_y <= color_y + button_height // 2):
                if self.bullet_color_level < 4:  # Max level is 4
                    self.bullet_color_level += 1
                    self.bullet_damage += 0.5
                self.close_shop()

            # Check HP button
            elif (hp_x <= click_x <= hp_x + button_width and
                  hp_y - button_height // 2 <= click_y <= hp_y + button_height // 2):
                self.player_max_hp += 1
                self.player_current_hp += 1
                self.close_shop()

        self.canvas.bind("<Button-1>", on_shop_click)

    def close_shop(self):
        # Buff enemies after each shop visit
        self.shop_count += 1
        self.enemy_max_health += 1

        # Update health of existing enemies
        for enemy in self.enemies:
            enemy[3] += 1  # Add 1 to current health

        # Clear canvas
        self.canvas.delete("all")

        # Recreate kill counter
        self.kill_counter_text = self.canvas.create_text(
            100, 30,
            text=f"Kills: {self.enemies_killed}",
            font=("Arial", 28, "bold"),
            fill="white",
            anchor="w"
        )

        # Recreate wave counter
        self.wave_counter_text = self.canvas.create_text(
            100, 65,
            text=f"Wave: {self.wave_number}",
            font=("Arial", 28, "bold"),
            fill="white",
            anchor="w"
        )

        # Recreate HP counter
        hp_color = "green" if self.player_current_hp == self.player_max_hp else "yellow" if self.player_current_hp > 1 else "red"
        self.hp_counter_text = self.canvas.create_text(
            100, 100,
            text=f"HP: {self.player_current_hp}/{self.player_max_hp}",
            font=("Arial", 28, "bold"),
            fill=hp_color,
            anchor="w"
        )

        # Recreate testing button
        test_button_x = self.screen_width - 150
        test_button_y = 50
        self.test_button = self.canvas.create_rectangle(
            test_button_x - 80, test_button_y - 25,
            test_button_x + 80, test_button_y + 25,
            fill="purple", outline="white", width=2
        )
        self.test_button_text = self.canvas.create_text(
            test_button_x, test_button_y,
            text="+20 Kills",
            font=("Arial", 18, "bold"),
            fill="white"
        )
        self.canvas.tag_bind(self.test_button, "<Button-1>", self.add_test_kills)
        self.canvas.tag_bind(self.test_button_text, "<Button-1>", self.add_test_kills)

        # Recreate player
        self.player = self.canvas.create_rectangle(
            self.player_x - 25, self.player_y - 25,
            self.player_x + 25, self.player_y + 25,
            fill="blue", outline="darkblue", width=2
        )

        # Recreate all projectiles
        for proj in self.projectiles:
            # Handle both player projectiles (5 elements) and enemy projectiles (6 elements)
            is_enemy_proj = len(proj) > 5 and proj[5]
            x, y, dx, dy = proj[1], proj[2], proj[3], proj[4]

            # Choose color based on whether it's enemy projectile
            if is_enemy_proj:
                fill_color, outline_color = "orange", "red"
            else:
                # Get player bullet color based on upgrade level
                bullet_colors = [
                    ("yellow", "orange"),
                    ("darkblue", "blue"),
                    ("purple", "darkviolet"),
                    ("turquoise", "cyan"),
                    ("black", "gray")
                ]
                fill_color, outline_color = bullet_colors[min(self.bullet_color_level, 4)]

            new_proj_id = self.canvas.create_oval(
                x - 8, y - 8,
                x + 8, y + 8,
                fill=fill_color, outline=outline_color, width=2
            )
            proj[0] = new_proj_id

        # Recreate all enemies
        for enemy in self.enemies:
            enemy_id = enemy[0]
            ex = enemy[1]
            ey = enemy[2]
            is_boss = enemy[4]
            if is_boss:
                new_enemy_id = self.canvas.create_rectangle(
                    ex - 40, ey - 40,
                    ex + 40, ey + 40,
                    fill="darkred", outline="red", width=4
                )
            else:
                new_enemy_id = self.canvas.create_rectangle(
                    ex - 20, ey - 20,
                    ex + 20, ey + 20,
                    fill="red", outline="darkred", width=2
                )
            enemy[0] = new_enemy_id

        # Unbind shop click
        self.canvas.unbind("<Button-1>")

        # Resume game
        self.shop_open = False

        # Restart the game loop
        self.update_game()

    def update_game(self):
        # Don't update if game is over or shop is open
        if self.game_over or self.shop_open:
            return

        # Handle continuous movement based on pressed keys
        current_speed = self.player_speed * self.player_speed_multiplier
        if 'w' in self.keys_pressed:
            self.player_y -= current_speed
        if 's' in self.keys_pressed:
            self.player_y += current_speed
        if 'a' in self.keys_pressed:
            self.player_x -= current_speed
        if 'd' in self.keys_pressed:
            self.player_x += current_speed

        # Update player position on canvas
        self.canvas.coords(
            self.player,
            self.player_x - 25, self.player_y - 25,
            self.player_x + 25, self.player_y + 25
        )

        # Update kill counter, wave counter, and HP display
        self.canvas.itemconfig(self.kill_counter_text, text=f"Kills: {self.enemies_killed}")
        self.canvas.itemconfig(self.wave_counter_text, text=f"Wave: {self.wave_number}")

        # Update HP text color based on health
        hp_color = "green" if self.player_current_hp == self.player_max_hp else "yellow" if self.player_current_hp > 1 else "red"
        self.canvas.itemconfig(self.hp_counter_text, text=f"HP: {self.player_current_hp}/{self.player_max_hp}", fill=hp_color)

        # Get current time for cooldowns
        current_time = time.time() * 1000  # Convert to milliseconds

        # Check if new wave should start (every 10 kills)
        if self.enemies_killed_this_wave >= 10:
            self.wave_number += 1
            self.enemies_killed_this_wave = 0
            # Increase enemy speed each wave, but cap it at 80% of player speed
            max_enemy_speed = (self.player_speed * self.player_speed_multiplier) * 0.8
            current_base_enemy_speed = self.enemy_speed * self.enemy_speed_multiplier
            if current_base_enemy_speed < max_enemy_speed:
                self.enemy_speed_multiplier += 0.1

        # Spawn boss every 30 kills (at 30, 60, 90, etc.)
        if self.enemies_killed > 0 and self.enemies_killed % 30 == 0 and self.current_boss is None and self.enemies_killed != self.last_boss_spawn_kills:
            self.last_boss_spawn_kills = self.enemies_killed
            self.spawn_boss()

        # Spawn enemies periodically (not if boss is alive)
        if self.current_boss is None and current_time - self.last_enemy_spawn >= self.enemy_spawn_cooldown:
            self.spawn_enemy()
            self.last_enemy_spawn = current_time

        # Handle automatic shooting with cooldown
        if current_time - self.last_shoot_time >= self.shoot_cooldown:
            # Determine shooting direction based on arrow keys pressed
            dx, dy = 0, 0

            if 'up' in self.keys_pressed:
                dy = -1
            if 'down' in self.keys_pressed:
                dy = 1
            if 'left' in self.keys_pressed:
                dx = -1
            if 'right' in self.keys_pressed:
                dx = 1

            # Shoot if any arrow key is pressed
            if dx != 0 or dy != 0:
                self.shoot_projectile(dx, dy)
                self.last_shoot_time = current_time

        # Update enemies (move towards player)
        enemies_to_remove = []

        for i, enemy in enumerate(self.enemies):
            enemy_id = enemy[0]
            ex = enemy[1]
            ey = enemy[2]
            is_boss = enemy[4]

            # Calculate direction to player
            dx = self.player_x - ex
            dy = self.player_y - ey
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 0:
                # Normalize and apply enemy speed (with wave multiplier)
                speed = self.enemy_speed * self.enemy_speed_multiplier
                dx = (dx / distance) * speed
                dy = (dy / distance) * speed

                # Update enemy position
                ex += dx
                ey += dy

                # Update canvas position (different size for boss)
                if is_boss:
                    self.canvas.coords(
                        enemy_id,
                        ex - 40, ey - 40,
                        ex + 40, ey + 40
                    )
                else:
                    self.canvas.coords(
                        enemy_id,
                        ex - 20, ey - 20,
                        ex + 20, ey + 20
                    )

                # Update stored position
                self.enemies[i][1] = ex
                self.enemies[i][2] = ey

            # Boss attacks
            if is_boss:
                boss_level = enemy[5]
                telegraph_icon = enemy[6]

                # Regular projectile shooting
                if current_time - self.boss_last_shoot >= self.boss_shoot_cooldown:
                    # Boss shoots at player
                    if distance > 0:
                        shoot_dx = (self.player_x - ex) / distance
                        shoot_dy = (self.player_y - ey) / distance

                        boss_projectile = self.canvas.create_oval(
                            ex - 6, ey - 6,
                            ex + 6, ey + 6,
                            fill="orange", outline="red", width=2
                        )
                        self.projectiles.append([boss_projectile, ex, ey, shoot_dx * 6, shoot_dy * 6, True])  # Added is_enemy flag
                        self.boss_last_shoot = current_time

                # Boss special attacks - check if it's time for a special attack
                if current_time - self.boss_last_special >= self.boss_special_cooldown:
                    # Trigger special attack
                    if telegraph_icon is None:
                        # Boss 2+ (level 1+): Rush to center and shoot 8 directions
                        if boss_level >= 1:
                            # Show telegraph for rush attack
                            telegraph_icon = self.canvas.create_text(
                                ex, ey - 60,
                                text="!",
                                font=("Arial", 48, "bold"),
                                fill="yellow"
                            )
                            self.enemies[i][6] = telegraph_icon
                            # Schedule the rush attack after 1 second
                            self.root.after(1000, lambda idx=i, curr_x=ex, curr_y=ey: self.boss_rush_attack(idx, curr_x, curr_y))
                            # Reset timer for next special attack
                            self.boss_last_special = current_time
                        # Boss 3+ (level 2+): Also do summon attack
                        if boss_level >= 2:
                            # Schedule summon attack 2 seconds after rush (or immediately if no rush)
                            delay = 2000 if boss_level >= 1 else 0
                            self.root.after(delay, lambda idx=i: self.boss_summon_attack(idx))

            # Check collision with player
            collision_radius = 65 if is_boss else 45
            player_distance = math.sqrt((self.player_x - ex)**2 + (self.player_y - ey)**2)
            if player_distance < collision_radius:
                if is_boss:
                    # Boss always instakills
                    self.show_game_over()
                    return
                else:
                    # Regular enemy - reduce HP
                    self.player_current_hp -= 1
                    if self.player_current_hp <= 0:
                        self.show_game_over()
                        return
                    # Destroy the enemy that hit the player
                    if i not in enemies_to_remove:
                        enemies_to_remove.append(i)

        # Update all projectiles and check collisions
        projectiles_to_remove = []

        for i, proj in enumerate(self.projectiles):
            # Check if this is an enemy projectile
            is_enemy_proj = len(proj) > 5 and proj[5]
            proj_id, x, y, dx, dy = proj[0], proj[1], proj[2], proj[3], proj[4]

            # Update position
            x += dx
            y += dy

            # Update canvas position
            self.canvas.coords(
                proj_id,
                x - 8, y - 8,
                x + 8, y + 8
            )

            # Update stored position
            self.projectiles[i][1] = x
            self.projectiles[i][2] = y

            # Check for enemy projectile hitting player
            if is_enemy_proj:
                player_dist = math.sqrt((x - self.player_x)**2 + (y - self.player_y)**2)
                if player_dist < 33:  # Bullet radius (8) + player radius (25)
                    # Reduce player HP
                    self.player_current_hp -= 1
                    if self.player_current_hp <= 0:
                        self.show_game_over()
                        return
                    # Destroy the projectile
                    projectiles_to_remove.append(i)

            # Check collision with enemies (player projectiles only)
            if not is_enemy_proj:
                hit_enemy = False
                for j, enemy in enumerate(self.enemies):
                    enemy_id = enemy[0]
                    ex = enemy[1]
                    ey = enemy[2]
                    is_boss = enemy[4]

                    # Simple collision detection (distance-based)
                    distance = math.sqrt((x - ex)**2 + (y - ey)**2)
                    hit_radius = 48 if is_boss else 28

                    if distance < hit_radius:
                        hit_enemy = True
                        # Reduce enemy health by bullet damage
                        self.enemies[j][3] -= self.bullet_damage

                        # Mark enemy for removal if health reaches 0
                        if self.enemies[j][3] <= 0:
                            if j not in enemies_to_remove:
                                enemies_to_remove.append(j)
                        break

                # Remove if hit enemy or off screen
                if hit_enemy or x < 0 or x > self.screen_width or y < 0 or y > self.screen_height:
                    projectiles_to_remove.append(i)
            else:
                # Remove enemy projectiles if off screen
                if x < 0 or x > self.screen_width or y < 0 or y > self.screen_height:
                    projectiles_to_remove.append(i)

        # Remove destroyed projectiles
        for i in reversed(projectiles_to_remove):
            self.canvas.delete(self.projectiles[i][0])
            del self.projectiles[i]

        # Remove destroyed enemies and update kill count
        boss_defeated = False
        for i in reversed(enemies_to_remove):
            enemy = self.enemies[i]
            is_boss = enemy[4] if len(enemy) > 4 else False

            self.canvas.delete(self.enemies[i][0])
            del self.enemies[i]
            self.enemies_killed += 1
            self.enemies_killed_this_wave += 1

            # Check if boss was defeated
            if is_boss:
                boss_defeated = True
                self.current_boss = None
                self.boss_number += 1  # Increment boss number for next boss

        # Check if shop should open (after boss defeat)
        if boss_defeated:
            self.last_shop_kills = self.enemies_killed
            self.show_shop()
            return

        # Continue game loop
        self.root.after(16, self.update_game)  # ~60 FPS

if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
