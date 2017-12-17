from livewires import games, color
import random
import math
import operator
from screen import Wrapper, Collider


class Asteroid(Wrapper):
    """ Moving asteroid on the screen """
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    POWERFUL = 1.5
    SPAWN = 2
    POINTS = 30
    total = 0
    images = {SMALL: games.load_image("images/asteroid_small.bmp"),
              MEDIUM: games.load_image("images/asteroid_med.bmp"),
              LARGE: games.load_image("images/asteroid_big.bmp"),
              POWERFUL: games.load_image("images/asteroid_powerful.bmp")}
    SPEED = 2

    def __init__(self, game, x, y, size, lifes):
        """ Initialize sprite with asteroid image """
        self.lifes = lifes
        Asteroid.total += 1
        self.asteroids = []

        super(Asteroid, self).__init__(
            image=Asteroid.images[size],
            x=x, y=y,
            dx=random.choice([-1, 1]) * Asteroid.SPEED *
            random.random() / size * 2.5,
            dy=random.choice([-1, 1]) * Asteroid.SPEED *
            random.random() / size * 2.5)

        self.game = game
        self.size = size

    def die(self):
        """ Destroys asteroid """
        Asteroid.total -= 1

        self.game.score.value += int(Asteroid.POINTS / self.size)
        self.game.score.right = games.screen.width - 10

        # if size of asteroid isn't small, replace with two smaller asteroids
        if self.size != Asteroid.SMALL and self.size != Asteroid.POWERFUL:
            for i in range(Asteroid.SPAWN):
                new_asteroid = Asteroid(game=self.game,
                                        x=self.x,
                                        y=self.y,
                                        size=self.size - 1,
                                        lifes=1)
                games.screen.add(new_asteroid)
                self.asteroids.append(new_asteroid)

        # if all asteroids are gone, advance to next level
        if Asteroid.total == 0:
            self.game.advance()

        super(Asteroid, self).die()

    def totally_die(self):
        """
        Destroys asteroid without adding smaller asteroids on the screen
        """
        super(Asteroid, self).die()

    def get_asteroids(self):
        """ Returns list of asteroids on the screen """
        return self.asteroids


class Ship(Collider):
    """ Player's ship """
    image = games.load_image("images/ship.bmp")
    sound = games.load_sound("sounds/thrust.wav")
    ROTATION_STEP = 5
    VELOCITY_STEP = .07
    MISSILE_DELAY = 20
    VELOCITY_MAX = 4

    def __init__(self, game, x, y):
        """ Initialize space ship sprite """
        super(Ship, self).__init__(image=Ship.image, x=x, y=y)
        self.game = game
        self.missile_wait = 0

    def update(self):
        """ Rotate based on key pressed """
        super(Ship, self).update()

        # rotate based on left and right arrow keys
        if games.keyboard.is_pressed(games.K_LEFT):
            self.angle -= Ship.ROTATION_STEP
        if games.keyboard.is_pressed(games.K_RIGHT):
            self.angle += Ship.ROTATION_STEP

        # move ship
        if games.keyboard.is_pressed(games.K_UP):
            Ship. sound.play()

            # change velocity components based on ship's angle
            angle = self.angle * math.pi / 180  # convert to radians
            self.dx += Ship.VELOCITY_STEP * math.sin(angle)
            self.dy += Ship.VELOCITY_STEP * -math.cos(angle)

            # cap velocity in each direction
            self.dx = min(max(self.dx, -Ship.VELOCITY_MAX), Ship.VELOCITY_MAX)
            self.dy = min(max(self.dy, -Ship.VELOCITY_MAX), Ship.VELOCITY_MAX)

        if games.keyboard.is_pressed(games.K_DOWN):
            Ship. sound.play()

            # change velocity components based on ship's angle
            angle = self.angle * math.pi / 180  # convert to radians
            self.dx -= Ship.VELOCITY_STEP * math.sin(angle)
            self.dy -= Ship.VELOCITY_STEP * -math.cos(angle)

            # cap velocity in each direction
            self.dx = min(max(self.dx, -Ship.VELOCITY_MAX), Ship.VELOCITY_MAX)
            self.dy = min(max(self.dy, -Ship.VELOCITY_MAX), Ship.VELOCITY_MAX)

        # if waiting until the ship can fire next, decrease wait
        if self.missile_wait > 0:
            self.missile_wait -= 1

        # if pressed space and missile wait is over, then launch missile
        if games.keyboard.is_pressed(games.K_SPACE) and self.missile_wait == 0:
            new_missile = Missile(self.x, self.y, self.angle)
            games.screen.add(new_missile)
            self.missile_wait = Ship.MISSILE_DELAY

    def die(self):
        """ Destroy ship and end the game """
        self.game.end()
        super(Ship, self).die()


class Missile(Collider):
    """ A missile launched by the player's ship """
    image = games.load_image("images/missile.bmp")
    sound = games.load_sound("sounds/missile.wav")
    BUFFER = 40
    VELOCITY_FACTOR = 12
    LIFETIME = 30

    def __init__(self, ship_x, ship_y, ship_angle):
        """ Initialize sprite with missile image """
        Missile.sound.play()

        # convert to radians
        angle = ship_angle * math.pi / 180

        # calculate missile's starting position
        buffer_x = Missile.BUFFER * math.sin(angle)
        buffer_y = Missile.BUFFER * -math.cos(angle)
        x = ship_x + buffer_x
        y = ship_y + buffer_y

        # calculate missile's velocity components
        dx = Missile.VELOCITY_FACTOR * math.sin(angle)
        dy = Missile.VELOCITY_FACTOR * -math.cos(angle)

        # create the missile
        super(Missile, self).__init__(image=Missile.image,
                                      x=x, y=y,
                                      dx=dx, dy=dy)
        self.lifetime = Missile.LIFETIME

    def update(self):
        """ Move the missile """
        super(Missile, self).update()

        # if lifetime is up, destroy the missile
        self.lifetime -= 1
        if self.lifetime == 0:
            self.destroy()


class Scores(games.Text):
    """ Save/display top scores after end of the game. """
    def __init__(self, score,
                 filename,
                 value, size=60,
                 color=color.black,
                 x=games.screen.width/2,
                 y=games.screen.height/2,
                 delay=5):

        super(Scores, self).__init__(value=value,
                                     size=size,
                                     color=color,
                                     x=x, y=y)

        self.default_length = len(self.value)
        self.filename = filename
        self.score = str(score)
        self.delay = delay
        self.time_remain = delay
        self.top_players = []

    def update(self):
        """ Ley user enter his nickname. """
        if (self.time_remain != 0):
            self.time_remain -= 1

        alphabet = [ch_code for ch_code in range(97, 122)]
        numbers = [ch_code for ch_code in range(48, 58)]

        # Enter letters
        for char_code in alphabet:
            if games.keyboard.is_pressed(char_code) and \
               self.time_remain == 0 and len(self.value) < 25:
                self.value += chr(char_code).upper()
                self.time_remain = self.delay
        # Enter digits
        for char_code in numbers:
            if games.keyboard.is_pressed(char_code) and \
               self.time_remain == 0 and len(self.value) < 25:
                self.value += chr(char_code).upper()
                self.time_remain = self.delay
        # Enter backspace
        if games.keyboard.is_pressed(games.K_BACKSPACE) and \
           self.time_remain == 0 and len(self.value) > 17:
            self.value = self.value[:-1]
            self.time_remain = self.delay
        # Enter return
        if games.keyboard.is_pressed(games.K_RETURN):
            # Save score to database and display top scores
            # If username is empty set is to PLAYER
            if (len(self.value) == self.default_length):
                self.value += 'PLAYER'
            self.you_lose()

    def get_top(self):
            """ Get top 3 players from file """
            scores_arr = []
            with open(self.filename) as scores:
                for player in scores:
                    player = player[:-1]
                    temp = [player.split()[0], int(player.split()[1])]
                    scores_arr.append(temp)
            top3players_int = sorted(scores_arr,
                                     key=operator.itemgetter(1),
                                     reverse=True)[:3]
            top3players = []
            for i in range(len(top3players_int)):
                top3players.append([top3players_int[i][0],
                                   str(top3players_int[i][1])])

            return top3players

    def show_top(self):
        """ Display top scores """
        self.top_players = self.get_top()

        for i in range(len(self.top_players)):
            # Add "Top players" phrase on the screen
            phrase = games.Text(value="TOP PLAYERS",
                                size=self.size,
                                color=color.red,
                                x=games.screen.width/2,
                                y=70)
            games.screen.add(phrase)
            # Add player's name on the screen
            player = games.Text(value=self.top_players[i][0],
                                size=self.size,
                                color=self.color,
                                x=250,
                                y=150+50*i)
            games.screen.add(player)
            # Add score on the screen
            score = games.Text(value=self.top_players[i][1],
                               size=self.size,
                               color=self.color,
                               x=450,
                               y=150+50*i)
            games.screen.add(score)
            # Add your name on the screen
            label = games.Text(value="Your score: ",
                               size=self.size,
                               color=self.color,
                               x=250,
                               y=330)
            games.screen.add(label)
            # Add your score on the screen
            my_points = games.Text(value=self.score,
                                   size=self.size,
                                   color=self.color,
                                   x=450,
                                   y=330)
            games.screen.add(my_points)
            # Add <press Esc to exit> label
            label = games.Text(value="<press Esc to exit>",
                               size=40,
                               color=self.color,
                               x=games.screen.width/2,
                               y=410)
            games.screen.add(label)

    def you_lose(self):
        """ Save score to database and display top scores """
        with open(self.filename, 'a') as f:
            # Save score to the file
            f.write(self.value[17:] + ' ' + self.score + '\n')
        self.destroy()
        self.show_top()