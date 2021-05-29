class Percepts:
    """This contains a set of percepts that the agent can perceive.
    """
    stench = False
    breeze = False
    glitter = False
    bump = False
    screech = False

    def give_stench(self):
        self.stench = True

    def give_breeze(self):
        self.breeze = True

    def give_glitter(self):
        self.glitter = True

    def give_bump(self):
        self.bump = True

    def give_screech(self):
        self.screech = True

    def get_percepts(self):
        return [
            self.stench,
            self.breeze,
            self.glitter,
            self.bump,
            self.screech,
        ]
