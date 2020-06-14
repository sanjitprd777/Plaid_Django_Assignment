from plaid_link.tasks import add


def test_celery():
    result = add.delay(4, 4)
    assert(result.get() == 8)
