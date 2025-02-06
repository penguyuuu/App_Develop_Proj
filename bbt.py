class BubbleTea:
    def __init__(self, size, sweetness, temperature, remarks, submit):
        self.__size = size
        self.__sweetness = sweetness
        self.__temperature = temperature
        self.__remarks = remarks
        self.__submit = submit


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

