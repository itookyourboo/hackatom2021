class Word:
    def __init__(self):
        self.start = None
        self.end = None
        self.value = None
        self.conf = None

    def __str__(self):
        return f'{self.value}[{self.start}; {self.end}] - {self.conf}'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end
