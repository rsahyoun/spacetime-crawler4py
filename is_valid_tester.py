#manually test file
import unittest



from scraper import is_valid


class IsValidTest(unittest.TestCase):
    def test_good_domains(self):
        self.assertTrue(is_valid("https://ics.uci.edu/follow-us/"))
        self.assertTrue(is_valid("https://cs.ics.uci.edu/faculty/"))
    def test_bad_domains(self):
        self.assertFalse(is_valid("https://nonameics.uci.edu"))
        self.assertFalse(is_valid("https://ics.uci.edu.fake.org"))


if __name__ == "__main__":
    unittest.main()
