class Cookie(dict):
    def as_string(self):
        return "; ".join(
            "{}={}".format(key, value) for key, value in self.items()
        )

    def __repr__(self):
        return self.as_string()

    @classmethod
    def parse_set_cookie(cls, set_cookie):
        key, value = set_cookie[:set_cookie.find(';')].split('=')
        key = key.strip()
        value = value.strip()
        return key, value
