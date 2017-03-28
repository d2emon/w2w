import unittest
import gravatar


class TestGravatar(unittest.TestCase):
    gravatar_url = "https://www.gravatar.com"
    def setUp(self):
        self.email = 'john@example.com'
        self.gravatar = gravatar.Gravatar(self.email)
        self.code = 'd4c74594d841139328695756648b6bd6'

    def test_avatar(self):
        expected = "{}/avatar/{}".format(self.gravatar_url, self.code)
        url = self.gravatar.url(128)
        self.assertEqual(url[0:len(expected)], expected)

    def test_profile(self):
        expected = "{}/{}".format(self.gravatar_url, self.code)
        url = self.gravatar.profile()
        self.assertEqual(url[0:len(expected)], expected)

    def test_static_avatar(self):
        expected = "{}/avatar/{}".format(self.gravatar_url, self.code)
        url = gravatar.gravatar(self.email, 128)
        self.assertEqual(url[0:len(expected)], expected)



if __name__ == '__main__':  # pragma : no cover
    unittest.main()
