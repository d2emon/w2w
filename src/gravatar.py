from hashlib import md5


class Gravatar:
    """
    Class for using Gravatar service

    Property 'default' - default image
    - File not found: '404'
    - Mystery man: 'mm'
    - Identicon: 'identicon'
    - Monsters: 'monsterid'
    - Faces: 'wavatar'
    - Retro games: 'retro'
    - Empty: 'blank'
    - Custom image: 'http://example.com/image.jpeg'

    Property 'rating' - image rating ('g', 'pg','r', 'x')
    """
    default = "wavatar"
    rating = 'g'

    def __init__(self, email=None):
        self.email = email
        # self.email = "d2emonium@gmail.com"

    def hash(self):
        return md5(self.email.encode('utf-8')).hexdigest()

    def url(self, size=128):
        return "http://www.gravatar.com/avatar/{}.jpg?d={}&r={}&s={}".format(
            self.hash(),
            self.default,
            self.rating,
            str(size),
        )

    def profile(self):
        return "https://www.gravatar.com/{}.json".format(
            self.hash(),
        )


def gravatar(email, size=128):
    avatar = Gravatar(email)
    return avatar.url(size=size)
