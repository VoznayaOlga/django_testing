from news.models import News


def test_successful_creation(news):
    assert News.objects.count() == 1
