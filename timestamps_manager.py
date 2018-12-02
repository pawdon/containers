from sortedcontainers import SortedList


class TimestampsManager:
    def __init__(self):
        self.min = -1
        self.max = -1
        self.timestamps = SortedList()

    def __str__(self):
        return "\n\t".join([f"Timestamps ({len(self.timestamps)}); current state = ({self.min}, {self.max}):"]
                           + [str(x) for x in self.timestamps])

    def reset(self):
        self.__init__()

    def get_min(self):
        return self.min

    def get_max(self):
        return self.max

    def _set_min_directly(self, x):
        if x <= self.max:
            self.min = x

    def _set_max_directly(self, x):
        if x >= self.min:
            self.max = x

    def set_min(self, x):
        if x in self.timestamps:
            self._set_min_directly(x)

    def set_max(self, x):
        if x in self.timestamps:
            self._set_max_directly(x)

    def increase_min(self):
        if self.min < self.timestamps[-1]:
            ind = self.timestamps.index(self.min)
            self._set_min_directly(self.timestamps[ind + 1])
            return self.get_min()
        else:
            return -1

    def increase_max(self):
        if self.max < self.timestamps[-1]:
            ind = self.timestamps.index(self.max)
            self._set_max_directly(self.timestamps[ind + 1])
            return self.get_max()
        else:
            return -1

    def add(self, x):
        if type(x) is int and x >= 0:
            if len(self.timestamps) == 0:
                self.timestamps.add(x)
                self.min = x
                self.max = x
            elif x not in self.timestamps:
                self.timestamps.add(x)
                self.min = min(self.min, x)
                self.max = max(self.max, x)


def test():
    tm = TimestampsManager()
    tm.add(5)
    tm.add(3)
    tm.add(5)
    tm.add(1)
    tm.add(10)
    print(tm)
    tm.set_max(tm.get_min())
    print(tm)
    tm.increase_max()
    tm.increase_max()
    tm.set_min(3)
    print(tm)
    tm.increase_min()
    tm.increase_min()
    tm.increase_min()
    tm.increase_min()
    tm.increase_min()
    tm.increase_min()
    print(tm)


if __name__ == "__main__":
    test()
