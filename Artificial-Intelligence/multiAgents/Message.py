

class Message(object): #standard message
    def __init__(self, sender_id, receiver_id):
        self.sender_id = sender_id
        self.receiver_id = receiver_id


class FriendshipMessage(Message): #offer friendship- share all info
    def __init__(self, sender_id, receiver_id, domain, value, constraints, agentView, currentCost):
        Message.__init__(self, sender_id, receiver_id)
        self.domain = domain
        self.value = value
        self.constraints = constraints
        self.agentView = agentView
        self.currentCost = currentCost


class UnFriendshipMessage(Message): #fake message - dont offer friendship
    def __init__(self, sender_id, receiver_id):
        Message.__init__(self, sender_id, receiver_id)


class AcceptFriendshipMessage(Message):#accepting a friendship message - calculates R and values for best swap
    def __init__(self, sender_id, receiver_id, R, senderAlternativeDomVal, receiverAlternativeDomVal):
        Message.__init__(self, sender_id, receiver_id)
        self.R = R
        self.senderAlternativeDomVal = senderAlternativeDomVal
        self.receiverAlternativeDomVal = receiverAlternativeDomVal


class DeclineFriendshipMessage(Message): #declining a friendship message
    def __init__(self, sender_id, receiver_id):
        Message.__init__(self, sender_id, receiver_id)


class ValueMessage(Message): #value message
    def __init__(self, sender_id, receiver_id, context):
        Message.__init__(self, sender_id, receiver_id)
        self.context = context


class RMessage(Message): #r message
    def __init__(self, sender_id, receiver_id, R):
        Message.__init__(self, sender_id, receiver_id)
        self.R = R


class CanSwapMessage(Message): #send to neighbor if can swap locally in next iter
    def __init__(self, sender_id, receiver_id):
        Message.__init__(self, sender_id, receiver_id)


class CannotSwapMessage(Message):#send to neighbor if cannot swap locally in next iter
    def __init__(self, sender_id, receiver_id):
        Message.__init__(self, sender_id, receiver_id)


class SwapPhaseNotPartners(Message):#fake message - send to all neighbors that arent my partner
    def __init__(self, sender_id, receiver_id):
        Message.__init__(self, sender_id, receiver_id)
