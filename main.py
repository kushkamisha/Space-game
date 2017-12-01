# # # # # # # # # #
# Astrocrash game #
# # # # # # # # # #

import math
import random
import operator
from livewires import games, color


games.init(screen_width=640, screen_height=480, fps=50)
DELAY = 3

class Wrapper(games.Sprite):
    """ Sprite, which wraps around the screen """

    def update(self):
        """ Wrap sprite around screen """
        if self.top > games.screen.height:
            self.bottom = 0

        if self.bottom < 0:
            self.top = games.screen.height

        if self.left > games.screen.width:
            self.right = 0

        if self.right < 0:
            self.left = games.screen.width

    def die(self):
        """ Destroys object """
        self.destroy()


class Collider(Wrapper):
    """ A wraper that can collide with another object """

    def update(self):
        """ Check for overlapping sprites """
        super(Collider, self).update()
        if self.overlapping_sprites:
            for sprite in self.overlapping_sprites:
                sprite.lifes -= 1
                if sprite.lifes == 0:
                    sprite.die()
            self.die()

    def die(self):
        """ Destroys object with an explosion """
        new_explosion = Explosion(x=self.x, y=self.y)
        games.screen.add(new_explosion)
        self.destroy()


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
            random.random() / size * 2.5 / DELAY,
            dy=random.choice([-1, 1]) * Asteroid.SPEED *
            random.random() / size * 2.5 / DELAY)

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
    ROTATION_STEP = 5 / DELAY
    VELOCITY_STEP = .07 / DELAY
    MISSILE_DELAY = 20 * DELAY
    VELOCITY_MAX = 4 / DELAY

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
    VELOCITY_FACTOR = 12 / DELAY
    LIFETIME = 30 * DELAY

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


class Explosion(games.Animation):
    """ Animationed explosion """
    sound = games.load_sound("sounds/explosion.wav")
    images = ["images/explosion1.bmp",
              "images/explosion2.bmp",
              "images/explosion3.bmp",
              "images/explosion4.bmp",
              "images/explosion5.bmp",
              "images/explosion6.bmp",
              "images/explosion7.bmp",
              "images/explosion8.bmp",
              "images/explosion9.bmp"]

    def __init__(self, x, y):
        super(Explosion, self).__init__(images=Explosion.images,
                                        x=x, y=y,
                                        repeat_interval=2 * DELAY, n_repeats=1,
                                        is_collideable=False)
        Explosion.sound.play()


##
# Top scores after end of the game
##
class Username(games.Text):
    """ A moving ship. """
    def __init__(self, score,
                 filename,
                 value, size=60,
                 color=color.black,
                 x=games.screen.width/2,
                 y=games.screen.height/2,
                 delay=5):

        super(Username, self).__init__(value=value,
                                       size=size,
                                       color=color,
                                       x=x, y=y)

        self.default_length = len(self.value)
        self.filename = filename
        self.score = str(score)
        self.delay = delay * DELAY
        self.time_remain = delay *DELAY

    def update(self):
        """ Move ship based on keys pressed. """
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

    def you_lose(self):
        """ Save score to database and display top scores """
        with open(self.filename, 'a') as f:
            # Save score to the file
            f.write(self.value[17:] + ' ' + self.score + '\n')
        self.destroy()

        top_players = getTop(self.filename)
        scores = Scores(my_score=self.score,
                        top_players=top_players,
                        size=60,
                        color=color.black)
        scores.show_top()


class Scores():
    """ Top player's score """
    def __init__(self, my_score, top_players, size, color):
        """ Init scores filename """
        self.my_score = my_score
        self.top_players = top_players
        self.size = size
        self.color = color

    def show_top(self):
        """ Display top scores """
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
            my_points = games.Text(value=self.my_score,
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


def getTop(filename):
    """ Get top 3 players from file """
    scores_arr = []
    with open(filename) as scores:
        for player in scores:
            player = player[:-1]
            temp = [player.split()[0], int(player.split()[1])]
            scores_arr.append(temp)
    top3players_int = sorted(scores_arr,
                             key=operator.itemgetter(1),
                             reverse=True)[:3]
    top3players = []
    for i in range(len(top3players_int)):
        top3players.append([top3players_int[i][0], str(top3players_int[i][1])])

    return top3players


class Game():
    """ The game """
    def __init__(self):
        """ Initialize game object """
        # set level
        self.level = 0

        # cheate list of asteroids
        self.asteroids = []

        # load sound for level advance
        self.sound = games.load_sound("sounds/level.wav")

        # create score
        self.score = games.Text(value=0,
                                size=30,
                                color=color.white,
                                top=5,
                                right=games.screen.width-19,
                                is_collideable=False)
        games.screen.add(self.score)

        # create player's ship
        self.ship = Ship(game=self,
                         x=games.screen.width/2,
                         y=games.screen.height/2)
        games.screen.add(self.ship)

    def play(self):
        """ Starts game """
        # begin music theme
        games.music.load("sounds/theme.mid")
        games.music.play(-1)

        # load and set background
        nebula_image = games.load_image("images/nebula.png")
        games.screen.background = nebula_image

        # advance to level 1
        self.advance()

        # start game
        games.screen.mainloop()

    def advance(self):
        """ Advance to the next level """
        self.level += 1

        # reserved space around the ship
        BUFFER = 150

        # create new asteroids
        for i in range(self.level):
            # calculate an x and y at least BUFFER distance from the ship

            # choose minimum distance along x-axis and y-axis
            x_min = random.randrange(BUFFER)
            y_min = BUFFER - x_min

            # choose distance along x-axis and y-axis based on minimum distance
            x_distance = random.randrange(x_min, games.screen.width - x_min)
            y_distance = random.randrange(y_min, games.screen.height - y_min)

            # calculate location based on distance
            x = self.ship.x + x_distance
            y = self.ship.y + y_distance

            # wrap around screen, if necessary
            x %= games.screen.width
            y %= games.screen.height

            # create the asteroid
            if i % 2 == 0:
                size = Asteroid.LARGE
                lifes = 1
            else:
                size = Asteroid.POWERFUL
                lifes = 3
            new_asteroid = Asteroid(game=self,
                                    x=x, y=y,
                                    size=size,
                                    lifes=lifes)
            games.screen.add(new_asteroid)
            self.asteroids.append(new_asteroid)

            # display level number
            level_message = games.Message(value="Level "+str(self.level),
                                          size=40,
                                          color=color.yellow,
                                          x=games.screen.width/2,
                                          y=games.screen.height/10,
                                          lifetime=3*games.screen.fps,
                                          is_collideable=False)
            games.screen.add(level_message)

            # play new level sound (except at first level)
            if self.level > 1:
                self.sound.play()

    def end(self):
        """ Ends game """
        # Destroy all asteroids on the screen
        for asteroid in self.asteroids:
            children = asteroid.get_asteroids()
            for child in children:
                child.totally_die()
            asteroid.totally_die()

        # show 'Game over' for 1 second
        end_message = games.Message(value="Game over",
                                    size=90,
                                    color=color.red,
                                    x=games.screen.width/2,
                                    y=games.screen.height/2,
                                    lifetime=1*games.screen.fps * DELAY,
                                    after_death=self.records,
                                    is_collideable=False)
        games.screen.add(end_message)

    def records(self):
        """ Enter player's name and display top 3 players """
        username = Username(score=str(self.score.value),
                            filename="database/scores.txt",
                            value="Enter your name: ")
        games.screen.add(username)


def main():
    astrocrash = Game()
    astrocrash.play()

if __name__ == "__main__":
    main()
