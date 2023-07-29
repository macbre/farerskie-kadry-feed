from utils import get_first_hashtag


def test_get_first_hashtag():
    assert get_first_hashtag(
        'Jadąc drogą nr 65 w kierunku osady #Selatrað, mija się dwa przyklejone do wąskiego paska asfaltu farerskie '
        'przysiółki') == 'Selatrað'

    assert get_first_hashtag(
        'Za nie lada wyczyn uchodzi na Wyspach Owczych zgubienie się w leśnej gęstwinie ;)') is None


if __name__ == "__main__":
    test_get_first_hashtag()
