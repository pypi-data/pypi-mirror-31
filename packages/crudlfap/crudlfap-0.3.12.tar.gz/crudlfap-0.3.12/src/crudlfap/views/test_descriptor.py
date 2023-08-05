import pytest

from crudlfap import crudlfap


class Example(object):
    def __init__(self):
        self.views = crudlfap.Views()
example = pytest.fixture(lambda: Example())


def test___set__(example):
    import ipdb; ipdb.set_trace()
    example.views = [crudlfap.TemplateView]
