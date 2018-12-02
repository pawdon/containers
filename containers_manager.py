class Container:
    def __init__(self, cid, length, width, height, timestamp):
        self.cid = cid
        self.length = length
        self.width = width
        self.height = height
        self.timestamp = timestamp

    def __str__(self):
        return f"c{self.cid},{self.width},{self.height},{self.length},{self.timestamp}"

    def __repr__(self):
        return f"Container({self.__str__()})"

    def to_string(self, order=None):
        if order is None:
            order = ["length", "width", "height"]
        d = {"length": self.length,
             "width": self.width,
             "height": self.height}
        return f"c{self.cid}," \
               f"{order[0]}={d[order[0]]},{order[1]}={d[order[1]]},{order[2]}={d[order[2]]}," \
               f"timestamp={self.timestamp}"

    @staticmethod
    def from_string(text):
        if text[0] != "c":
            return None
        if text[-1] == "\n":
            text = text[0:-1]
        try:
            cid, width, height, length, timestamp = [int(x) for x in text[1:].split(",")]
        except ValueError:
            return None
        return Container(cid=cid, width=width, height=height, length=length, timestamp=timestamp)


class ContainersManager:
    def __init__(self, **args):
        self.waiting_containers = []
        self.sent_containers = []

        self.const_h = None
        self.min_length = args.get("min_length", 1)
        self.max_length = args.get("max_length", 40)
        self.min_width = args.get("min_width", 1)
        self.max_width = args.get("max_width", 40)
        self.min_height = args.get("min_height", 1)
        self.max_height = args.get("max_height", 40)

    def __str__(self):
        return "\n\t".join([f"Waiting containers ({len(self.waiting_containers)})"]
                           + [str(x) for x in self.waiting_containers]) + "\n" + \
               "\n\t".join([f"Sent containers ({len(self.sent_containers)})"]
                           + [str(x) for x in self.sent_containers])

    def add(self, x, min_timestamp):
        if type(min_timestamp) is not int:
            return None
        container = Container.from_string(x)
        if container is not None:
            check_ok = container.timestamp >= min_timestamp and \
                       self.min_length <= container.length <= self.max_length and \
                       self.min_width <= container.width <= self.max_width and \
                       self.min_height <= container.height <= self.max_height and \
                       container.cid not in [x.cid for x in self.waiting_containers + self.sent_containers]
            if check_ok:
                if self.const_h is None:
                    self.const_h = container.height
                    self.waiting_containers.append(container)
                elif container.height == self.const_h:
                    self.waiting_containers.append(container)
                else:
                    container = None
            else:
                container = None
        return container

    def send(self, containers):
        for container in containers:
            if container in self.waiting_containers:
                self.waiting_containers.remove(container)
                self.sent_containers.append(container)

    def get_containers(self, max_timestamp):
        containers_list = []
        for container in self.waiting_containers:
            if container.timestamp <= max_timestamp:
                containers_list.append(container)
            else:
                break
        return containers_list


def test():
    c1 = Container(cid=2, length=4, width=5, height=7, timestamp=39)
    text = c1.to_string()
    print(text)
    c2 = Container.from_string(text)
    print(c2)
    print(Container.from_string("c10,1,2,2,2"))
    print(Container.from_string("c10,f,2,2,2"))
    print(Container.from_string("c10,1,2,2"))
    print(Container.from_string("c10,1,2,2,2,3"))


def test2():
    cm = ContainersManager()
    cm.add("c10,1,2,2,2", min_timestamp=0)
    cm.add("c11,1,2,2,2", min_timestamp=2)
    cm.add("c12,1,2,2,3", min_timestamp=2)
    cm.add("c13,1,2,2,3", min_timestamp=3)
    cm.add("c14,1,2,2,4", min_timestamp=3)
    cm.add("c15,1,2,2,3", min_timestamp=4)
    cm.add("c16,41,2,2,4", min_timestamp=4)
    cm.add("c14,2,2,2,4", min_timestamp=4)
    print(cm)
    containers = cm.get_containers(max_timestamp=3)
    print(containers)
    cm.send([containers[1], containers[2]])
    print(cm)


if __name__ == "__main__":
    test2()
