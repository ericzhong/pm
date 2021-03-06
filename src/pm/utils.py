# coding:utf-8


class Helper:

    def __init__(self):
        pass

    @classmethod
    def add_prefix(cls, text, prefix=""):
        str = ""
        for s in text.splitlines():
            str += "%s%s\n" % (prefix, s)
        return str

    @classmethod
    def quote(cls, text):
        return cls.add_prefix(text, "> ")

    @classmethod
    def limit_length(cls, string, length):
        suffix = '...'
        suffix_size = len(suffix)
        if len(string) > length - suffix_size:
            return string[:length - suffix_size] + suffix
        else:
            return string

    @classmethod
    def get_offset(cls, offset_str=None):
        try:
            offset = int(offset_str) if offset_str else 0
        except ValueError:
            offset = 0
        return offset

    @classmethod
    def get_orderby_options(cls, orders):
        assert(isinstance(orders, list))
        reverse = ["-" + str(x) for x in orders]
        return orders + reverse


if __name__ == '__main__':
    # Test
    text = "1\n2\n3\n4\n5\n"
    print Helper.quote(text)
