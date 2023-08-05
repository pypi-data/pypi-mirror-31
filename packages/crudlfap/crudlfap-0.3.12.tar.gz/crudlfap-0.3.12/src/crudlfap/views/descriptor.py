class Views(list):
    def __set__(self, value):
        import ipdb; ipdb.set_trace()
        self.views = value

    def __get__(self):
        import ipdb; ipdb.set_trace()
