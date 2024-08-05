import pytest
from news.models import News


@pytest.mark.django_db
def test_successful_creation(news):
    news_count = News.objects.count()
    assert news_count == 1
