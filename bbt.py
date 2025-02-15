class BubbleTea:
    def __init__(self, type, size, sweetness, temperature, remarks, submit):
        self.__type = type
        self.__size = size
        self.__sweetness = sweetness
        self.__temperature = temperature
        self.__remarks = remarks
        self.__submit = submit

    def get_type(self):
        return self.__type

    def get_size(self):
        return self.__size

    def get_sweetness(self):
        return self.__sweetness

    def get_temperature(self):
        return self.__temperature

    def get_remarks(self):
        return self.__remarks

    def get_submit(self):
        return self.__submit

    def set_type(self, type):
        self.__type = type

    def set_size(self, size):
        self.__size = size

    def set_sweetness(self, sweetness):
        self.__sweetness = sweetness

    def set_temperature(self, temperature):
        self.__temperature = temperature

    def set_remarks(self, remarks):
        self.__remarks = remarks

    def set_submit(self, submit):
        self.__submit = submit

