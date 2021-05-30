class Percepts:
    """This contains a set of percepts that the agent can perceive.
    """
    def __init__(
        self,
        stench = False,
        breeze = False,
        glitter = False,
        bump = False,
        screech = False,
        is_terminated = False,
        reward = 0):
        
        self.stench = stench
        self.breeze = breeze
        self.glitter = glitter
        self.bump = bump
        self.screech = screech
        self.is_terminated = is_terminated
        self.reward = reward

    def __str__(self):
        return "stench: {0}, breeze: {1}, glitter: {2}, bump: {3}, screech: {4}, is_terminated: {5}, reward: {6}"\
            .format(
                self.stench,
                self.breeze,
                self.glitter,
                self.bump,
                self.screech,
                self.is_terminated,
                self.reward
            )
