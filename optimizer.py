class IOptimizer:
    def __init__(self):
        pass

    @staticmethod
    def info():
        return "Abstract optimizer interface"

    def optimize(self, **args):
        return {}


class OptimizerSelector:
    @staticmethod
    def select(nr=1):
        if nr == 1:
            return Optimizer1()
        else:
            return IOptimizer()

    @staticmethod
    def correct_algorithms_ids():
        return [1]


class Optimizer1(IOptimizer):
    def __init__(self):
        super().__init__()

    @staticmethod
    def info():
        return "Optimizer version 1"

    def optimize(self, **args):
        return {}

