import random
from livewires import games, color
from interface import Asteroid, Ship, Scores


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
                                    lifetime=1*games.screen.fps,
                                    after_death=self.records,
                                    is_collideable=False)
        games.screen.add(end_message)

    def records(self):
        """ Enter player's name and display top 3 players """
        scores = Scores(score=str(self.score.value),
                        filename="database/scores.txt",
                        value="Enter your name: ")
        games.screen.add(scores)
