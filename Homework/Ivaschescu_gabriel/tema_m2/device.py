#base class for diffrent devices to inherit


class Device:
    def __init__(self,name):
        self.name = name

    def __str__(self):
        return f"{self.__class__.__name__} - {self.name}"