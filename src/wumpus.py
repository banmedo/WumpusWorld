class Wumpus:
    alive = True
    
    def __init__(self, location):
        self.set_location(location)

    def set_location(self, location):
        self.location = location

    def get_location(self):
        return self.location

    def is_alive(self):
        return self.alive

    def kill(self):
        self.alive = False
