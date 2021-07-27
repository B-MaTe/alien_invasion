import sys
from game_stats import GameStats
from time import sleep
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from button import *
from scoreboard import Scoreboard
import pygame


class AlienInvasion:

    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        # Create an instance to store game statistics.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()
        pygame.display.set_caption("Alien Invasion")
        # Make the "Play" button.
        self.play_button = Button(self, "Play")
        self.text = Text(self, "Press 'p' or click the 'Play' button to start playing")
        self.easy = Easy(self, "Easy")
        self.medium = Medium(self, "Medium")
        self.hard = Hard(self, "Hard")

    def _update_screen(self):
        # Update images on the screen, and flip to the new screen.
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        self.sb.show_score()
        # Draw the button on the screen.
        if not self.stats.game_active:
            self.play_button.draw_button()
            self.text.draw_button()
            self.hard.draw_button()
            self.medium.draw_button()
            self.easy.draw_button()

        pygame.display.flip()

    def run_game(self):
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_keydown_events(self, event):
        # Respond to key presses.
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_q:
            sys.exit()
        # Just in case we have to delete 'q' or that doesnt work
        elif event.key == pygame.K_LALT and pygame.K_F4:
            sys.exit()
        elif event.key == pygame.K_p and not self.stats.game_active:
            self._start_game()
            self.settings.initialize_dynamic_settings()

    def _check_keyup_events(self, event):
        # Respond to releases.
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        easy = self.easy.rect.collidepoint(mouse_pos)
        medium = self.medium.rect.collidepoint(mouse_pos)
        hard = self.hard.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self._start_game()
            self.sb.prep_ships()
        elif easy and not self.stats.game_active:
            self.stats.e = True
            self.sb.prep_ships()
            self._start_game()
        elif medium and not self.stats.game_active:
            self.stats.m = True
            self._start_game()
            self.sb.prep_ships()
        elif hard and not self.stats.game_active:
            self.stats.h  = True
            self._start_game()
            self.sb.prep_ships()

    def _start_game(self):
        # Hide the mouse cursor.
        pygame.mouse.set_visible(False)
        # Reset the game statistics.
        self.stats.reset_stats()
        self.stats.game_active = True
        self.sb.prep_score()
        self.sb.prep_level()

        # Get rid of any remaining aliens and bullets.
        self.aliens.empty()
        self.bullets.empty()

        # Create a new fleet, and center the ship.
        self._create_fleet()
        self.ship.center_ship()
        self.settings.initialize_dynamic_settings()

    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien_width = alien.rect.width
        alien.x = alien_width + 3 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _create_fleet(self):
        """Create the fleet of aliens"""
        # Make and alien and find the number of aliens in a row.
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien_width = alien.rect.width
        available_space_x = self.settings.screen_width - (10 * alien_width)
        number_aliens_x = available_space_x // (3 * alien_width)

        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                            (2 * alien_height) - ship_height)
        number_rows = available_space_y // (3 * alien_height)

        # Create the full fleet of aliens.
        for row_number in range(number_rows):
            # Create the first row of aliens.
            for alien_number in range(number_aliens_x):
                # Create an alien and place it in the row.
                self._create_alien(alien_number, row_number)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_aliens(self):
        """
        Check if the fleet is at an edge,
        then update the positions of all aliens in the fleet.
        """
        self._check_fleet_edges()
        self.aliens.update()

        # Look for ship-alien collision
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """check if any aliens hit the bottom of the screen"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

    def _fire_bullet(self):
        """Create a new bullet and add it ot the bullets group"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update the position of bullets and get rid of old bullets"""
        # Update bullet positions.
        self.bullets.update()
        # Get rid of the bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        # print(len(self.bullets)) To see if the bullets are removed

        self._check_bullet_alien_collision()

    def _check_bullet_alien_collision(self):
        # Check for any bullets that have hit aliens.
        # If so, get rid of the bullet and alien.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
        if not self.aliens:
            # Destroy all existing bullets and recall aliens.
            self.bullets.empty()
            self._create_fleet()
            self._levels()
            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def _levels(self):
        if self.stats.e:
            self.settings.speedup_scale = 1.1
            self.settings.increase_speed()
        elif self.stats.m:
            self.settings.speedup_scale = 1.2
            self.settings.increase_speed()
        elif self.stats.h:
            self.settings.speedup_scale = 1.3
            self.settings.increase_speed()

    def _ship_hit(self):
        """Respond to the ship being hit by an alien"""
        if self.stats.ships_left > 1:
            # Decrement ships_left, update scoreboard.
            self.stats.ships_left -=1
            self.sb.prep_ships()

            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Pause.
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()