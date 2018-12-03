from sortedcontainers import SortedList


class TimestampsManager:
    """
    Class used for storing a list of timestamps
    and managing information about timestamps range of interest.
    """
    def __init__(self):
        """
        Constructor.
        """
        self.min = -1                   # lower limit of timestamps range of interest
        self.max = -1                   # upper limit of timestamps range of interest
        self.timestamps = SortedList()  # list of timestamps (unsigned ints)

    def __str__(self):
        """
        Create a string from the timestamps manager. Used when call print(timestamps manager).
        :return: A string describing the timestamps manager.
        """
        return "\n\t".join([f"Timestamps ({len(self.timestamps)}); current state = ({self.min}, {self.max}):"]
                           + [str(x) for x in self.timestamps])

    def reset(self):
        """
        Reset the timestamp manager.
        :return:
        """
        self.__init__()

    def get_min(self):
        """
        Return lower limit of timestamps range of interest.
        :return: lower limit of timestamps range of interest
        """
        return self.min

    def get_max(self):
        """
        Return upper limit of timestamps range of interest.
        :return: upper limit of timestamps range of interest
        """
        return self.max

    def _set_min_directly(self, x):
        """
        Private method.
        Check if a given value is less than or equal to the upper limit of timestamps range of interest
        and set the lower limit of timestamps range of interest.
        :param x: timestamp
        :return:
        """
        if x <= self.max:
            self.min = x

    def _set_max_directly(self, x):
        """
        Private method.
        Check if a given value is greater than or equal to the lower limit of timestamps range of interest
        and set the upper limit of timestamps range of interest.
        :param x: timestamp
        :return:
        """
        if x >= self.min:
            self.max = x

    def set_min(self, x):
        """
        Check if a given value is inside the timestamps list
        and if so, set it as the lower limit of timestamps range of interest.
        :param x: timestamp
        :return:
        """
        if x in self.timestamps:
            self._set_min_directly(x)

    def set_max(self, x):
        """
        Check if a given value is inside the timestamps list
        and if so, set it as the upper limit of timestamps range of interest.
        :param x: timestamp
        :return:
        """
        if x in self.timestamps:
            self._set_max_directly(x)

    def increase_min(self):
        """
        Try to change the lower limit of timestamps range of interest to the next value of timestamp.
        :return: new lower limit of timestamps range of interest (if successfully changed) or -1
        """
        if self.min < self.timestamps[-1]:
            ind = self.timestamps.index(self.min)
            self._set_min_directly(self.timestamps[ind + 1])
            return self.get_min()
        else:
            return -1

    def increase_max(self):
        """
        Try to change the upper limit of timestamps range of interest to the next value of timestamp.
        :return: new upper limit of timestamps range of interest (if successfully changed) or -1
        """
        if self.max < self.timestamps[-1]:
            ind = self.timestamps.index(self.max)
            self._set_max_directly(self.timestamps[ind + 1])
            return self.get_max()
        else:
            return -1

    def add(self, x):
        """
        Check if a given value is a correct timestamp
        and if so, add it to the list.
        :param x: timestamp
        :return:
        """
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
