class Cursor:
    def __init__(self, data):
        self.data = data
        self.pos = -1

    def is_eof(self):
        if self.pos + 1 == len(self.data):
            return True
        return False

    def peek(self):
        if self.is_eof():
            return None
        return self.data[self.pos + 1]

    def advance(self):
        if self.is_eof():
            return None
        self.pos += 1
        return self.data[self.pos]
