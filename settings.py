class Settings:

    def __init__(self):

        # Screen Settings
        self.screen_width = 2560
        self.screen_height = 1080
        self.bg_color = (230, 230, 230)

        # Ship settings
        self.ship_limit = 3

        # Bullet settings
        self.bullet_width = 10
        self.bullet_height = 15
        self.bullet_color = (190, 22, 0)
        self.bullets_allowed = 3

        # Alien settings
        self.fleet_drop_speed = 10
        # fleet_direction of 1 represents right; -1 represents left.

        # How quickly the game speeds up
        self.speedup_scale = 1.2

        # How quickly the alien point values increase
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Initialzie speed settings and alien point values."""
        self.ship_speed = 5.0
        self.bullet_speed = 10
        self.alien_speed = 5

        # Fleet_direction of 1 represents right; -1 left.
        self.fleet_direction = 1

        # Scoring
        self.alien_points = 50

    def increase_speed(self):
        """Increase the speed"""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)

