from livewires import games


games.init(screen_width=640, screen_height=480, fps=50)


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
                                        repeat_interval=2, n_repeats=1,
                                        is_collideable=False)
        Explosion.sound.play()
