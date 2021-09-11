import copy
import Mailbox
import Message

class Agent(object):
    def __init__(self, agent_id, variable_value=None, domain=None):
        self.agent_id = agent_id
        self.variable_value = variable_value
        self.domain = domain
        self.constraints = []
        self.agent_view = {} #agent : value
        self.mailbox = Mailbox.Mailbox()

    def initialize(self):
        raise NotImplementedError()

    def compute(self):
        raise NotImplementedError()

    def send_msgs(self):
        raise NotImplementedError()

    def reactToMsg(self, msg):
        raise NotImplementedError()

    def receive_messages(self):
        for msg in self.mailbox.msgs:
            self.reactToMsg(msg)
        self.mailbox.msgs = []


class Agent_MGM2(Agent):
    def __init__(self, agent_id, randnum, p=0.5):
        Agent.__init__(self, agent_id)
        self.rand = randnum
        self.p = p
        self.current_cost = None
        self.outgoingMail = Mailbox.Mailbox()
        self.offered = False
        self.offered_agent_id = None
        self.R = None
        self.bestValueOption = None
        self.swap = False

    def send_msgs(self): #send all messages from outgoing mailbox
        msgs = self.outgoingMail.msgs
        self.outgoingMail.msgs = []
        return msgs

    def initialize(self): #this will be a random decision of a value
        index = self.rand.randint(0, len(self.domain)-1)
        self.variable_value = self.domain[index]
        self.send_value_to_neighbors() #creates messages for outbox of current value

    def acceptFriendship(self, msg): #calculates best R for improvement of a friendship
        maxR = -1
        minMydomval = None
        minOtherDomVal = None
        myView=copy.copy(self.agent_view)
        myNeigView=copy.copy(msg.agentView)
        for domval in self.domain:
            for domvalneighbor in msg.domain:
                myView[self.offered_agent_id]= domvalneighbor
                myNeigView[self.agent_id]= domval
                c1 = calculateCostIfUsingValue(domval, self.constraints, myView)
                c2 = calculateCostIfUsingValue(domvalneighbor, msg.constraints, myNeigView)
                R = (self.current_cost + msg.currentCost) - (c1 + c2)
                if R > maxR:
                    maxR = R
                    minMydomval = domval
                    minOtherDomVal = domvalneighbor

        self.R = maxR
        self.bestValueOption = minMydomval

        return minOtherDomVal

    def checkAlgorithmStateByMessages(self): #checks the state of the algorithm according to the type of messages the agent
        # receives. since the alg is synch', they will all be in the same stage at the same time
        for msg in self.mailbox.msgs:
            if type(msg) == Message.ValueMessage:
                return 1
            elif type(msg) == Message.FriendshipMessage or type(msg) == Message.UnFriendshipMessage:
                return 2
            elif type(msg) == Message.AcceptFriendshipMessage or type(msg) == Message.DeclineFriendshipMessage:
                return 3
            elif type(msg) == Message.RMessage:
                return 4
            elif type(msg) == Message.CanSwapMessage or type(msg) == Message.CannotSwapMessage or type(msg) == Message.SwapPhaseNotPartners:
                return 5

    def compute(self): #here we write the MGM2 algorithm for a single agent
        incoming = len(self.mailbox.msgs)
        algorithmState = self.checkAlgorithmStateByMessages()

        if algorithmState == 1:
            self.receive_value_messages() #get everyones values
            self.randomize_partner() #choose if to get a partner and if so, send random neighbor a friendship message

        elif algorithmState == 2:
            self.finalize_partnerships() #if i asked for friendship, i reject everyone
                                        #if i didnt ask for a friendship, i approve first request and reject the rest

        elif algorithmState == 3:
            self.get_R() #calculate R
            self.send_R_to_neighbors() #send R

        elif algorithmState == 4:
            self.check_if_can_swap() #checks if this agent is best out of neighbors

        elif algorithmState == 5: #if both can swap/not in a couple and still best, swap
            self.find_out_if_can_swap()

            if self.swap is True:
                self.variable_value = self.bestValueOption

            self.send_value_to_neighbors() #send value to neighbor (whether agent swapped or not)

            self.resetAlgorithmParameters() #reset state of friendships, etc.


    def choose_best_domval(self): #single agent improvement
        Rmax = -1
        bestVal = None
        for domval in self.domain:
            cost = calculateCostIfUsingValue(domval, self.constraints, self.agent_view)
            R = self.current_cost - cost
            if R > Rmax:
                Rmax = R
                bestVal = domval
        self.R = Rmax
        self.bestValueOption = bestVal

    def resetAlgorithmParameters(self): #reset state of friendships, etc.
        self.offered = False
        self.offered_agent_id = None
        self.R = None
        self.bestValueOption = None
        self.swap = False

    def receive_value_messages(self): #update agent view and cost
        for msg in self.mailbox.msgs:
            self.agent_view[msg.sender_id] = msg.context
        self.mailbox.msgs = []
        self.current_cost = calculateCostIfUsingValue(self.variable_value, self.constraints, self.agent_view)

    def randomize_partner(self): #choose if to have a friend, and which friend if chosen
        chosenNeighbor = None
        if self.rand.random() < self.p:  # offer friendship
            chosenNeighbor = self.rand.choice(list(self.agent_view.keys()))
            self.offered_agent_id = chosenNeighbor
            self.offered = True
            self.outgoingMail.msgs.append(
                Message.FriendshipMessage(self.agent_id, chosenNeighbor, self.domain, self.variable_value,
                                          self.constraints, self.agent_view, self.current_cost))
        unchosen_neighbors = copy.deepcopy(list(self.agent_view.keys()))
        if chosenNeighbor is not None:
            unchosen_neighbors.remove(chosenNeighbor)
        for neighbor in unchosen_neighbors: #send fake messages to whoever we didnt offer
            self.outgoingMail.msgs.append(Message.UnFriendshipMessage(self.agent_id, neighbor))

    def finalize_partnerships(self): #accept or decline friendship offers
        for msg in self.mailbox.msgs:
            if type(msg) == Message.FriendshipMessage and self.offered is False:
                otherDomAlternative = self.acceptFriendship(msg)
                self.offered = True
                self.offered_agent_id = msg.sender_id
                self.outgoingMail.msgs.append(Message.AcceptFriendshipMessage(self.agent_id, self.offered_agent_id, self.R, self.bestValueOption,
                                                    otherDomAlternative))
            else:  # did offer but not to sender or already accepted a partner
                self.outgoingMail.msgs.append(Message.DeclineFriendshipMessage(self.agent_id, msg.sender_id))
        self.mailbox.msgs = []

    def get_R(self):
        for msg in self.mailbox.msgs:
            if type(msg) == Message.AcceptFriendshipMessage:
                self.R = msg.R
                self.bestValueOption = msg.receiverAlternativeDomVal
                self.offered = True
                self.offered_agent_id = msg.sender_id
                break
        else: #didnt get a friendship
            self.offered = False
            self.offered_agent_id = None
            self.choose_best_domval()  # updates R and bestValueOption

        self.mailbox.msgs = []


    def send_R_to_neighbors(self): #send R messages to all neighbors
        for neighbor in self.agent_view.keys():
            self.outgoingMail.msgs.append(Message.RMessage(self.agent_id, neighbor, self.R))

    def check_if_can_swap(self): #checks if can swap- if i am single and better than everyone, swap, if i am not single and me and my partner are each better than everyone, swap.

        self.swap=True
        for msg in self.mailbox.msgs:
            if msg.R > self.R or (msg.R == self.R and msg.sender_id!=self.offered_agent_id and msg.sender_id < self.agent_id ): #someone else is better than me
                self.swap = False
                break


        self.mailbox.msgs = []

        if self.swap is True and self.R>0:  # self.R is the max - will swap
            if self.offered is True:
                self.outgoingMail.msgs.append(Message.CanSwapMessage(self.agent_id, self.offered_agent_id))
        else:
            self.swap = False
            if self.offered is True:
                self.outgoingMail.msgs.append(Message.CannotSwapMessage(self.agent_id, self.offered_agent_id))

        for neighbor in self.agent_view.keys(): #fake message to all that arent my partner
            if neighbor != self.offered_agent_id:
                self.outgoingMail.msgs.append(Message.SwapPhaseNotPartners(self.agent_id, neighbor))


    def find_out_if_can_swap(self): #partners decide if can swap together
        if self.swap is True:
            for msg in self.mailbox.msgs:
                if type(msg) is Message.CannotSwapMessage:
                    self.swap = False

        self.mailbox.msgs = []

    def send_value_to_neighbors(self):#send a value message to each of my neighbors
        for neighbor in self.agent_view.keys():
            self.outgoingMail.msgs.append(
                Message.ValueMessage(sender_id=self.agent_id, receiver_id=neighbor, context=self.variable_value))


class Agent_DSA(Agent):
    def __init__(self, agent_id, randnum, p=0.7):
        Agent.__init__(self, agent_id)
        self.p = p
        self.rand = randnum
        self.current_cost = None

    def initialize(self): #this will be a random decision of a value
        index = self.rand.randint(0, len(self.domain)-1)
        self.variable_value = self.domain[index]

    def send_msgs(self): #sends messages to all neighbors with current value
        msgs = []
        for neighbor in self.agent_view.keys():
            msgs.append(Message.ValueMessage(sender_id=self.agent_id, receiver_id=neighbor, context=self.variable_value))

        return msgs

    def reactToMsg(self, msg): #update agent view
        self.agent_view[msg.sender_id] = msg.context

    def compute(self): #here we write the DSA algorithm for a single agent
        self.receive_messages()
        self.current_cost = calculateCostIfUsingValue(self.variable_value, self.constraints, self.agent_view)

        minCost = None
        bestVal = None
        for domval in self.domain:
            if domval != self.variable_value: #only alternative values
                cost = calculateCostIfUsingValue(domval, self.constraints, self.agent_view)
                if minCost is None:
                    minCost = cost
                    bestVal = domval
                elif cost < minCost:
                    minCost = cost
                    bestVal = domval
        if minCost <= self.current_cost and self.rand.random() < self.p:
            self.variable_value = bestVal


def calculateCostIfUsingValue(domval, constraints, agent_view): #if this agent will choose to use domval, the cost will be domvalcost
    domvalcost = 0
    for constraint in constraints:
        if (domval == constraint.myValue) and (constraint.otherAgentValue == agent_view[constraint.otherAgent_id]):
            domvalcost += constraint.cost
    return domvalcost