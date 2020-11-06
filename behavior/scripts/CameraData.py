class BoundingBox:

    pos_x = 0
    pos_y = 0
    size_x = 0
    size_y = 0

    def __init__(self, pos_x, pos_y, size_x, size_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.size_x = size_x
        self.size_y = size_y

    def area(self):
        return self.size_x * self.size_y

    def median_point(self):
        return [self.pos_x + (self.size_x / 2), self.pos_y + (self.size_y / 2)]


class CameraData:

    SIZE_X = 1920
    SIZE_Y = 1080
    target_bounding_box = None

    def __init__(self):
        self.target_bounding_box = BoundingBox(0, 0, 0, 0)
