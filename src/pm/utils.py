

class Helper():

    @classmethod
    def add_prefix(self, text, prefix=""):
        str = ""
        for s in text.splitlines():
            str += "%s%s\n" % (prefix, s) 
        return str


    @classmethod
    def quote(self, text):
        return self.add_prefix(text, "> ")


if __name__ == '__main__':
    # Test
    text = "1\n2\n3\n4\n5\n"
    print Helper.quote(text)
