import Mailbox
import Agent
import pandas

class Mailer(object):
    def __init__(self, problem, termination, save=False):
        self.agents = problem.agents
        self.msg_box = Mailbox.Mailbox()
        self.termination = termination
        self.save = save
        if save: #should we save data for second graphs
            self.data = pandas.DataFrame(columns={'iteration', 'cost'})

    def agents_react_to_msgs(self, iteration): #plays out a single iteration - agents receive messages, react, and the mailer takes the outgoing messages
        for agent in self.agents:
            if iteration == 0:
                agent.initialize() #first iteration (randomize)
            else:
                agent.compute() #receive msgs and react

            self.msg_box.msgs.extend(agent.send_msgs())

    def execute(self): #run iterations
        for iteration in range(0, self.termination + 1):
            self.agents_react_to_msgs(iteration) #agents receive messages, react and create messages for next iteration
            self.mailer_disperse_msgs_to_each_mailbox() #mailer puts all next iteration messages in the mailboxes of the agents (to react in next iter)
            if iteration % 10 == 0: #calculate cost and save data
                cost = self.calculateCurrentPrice()
                print(iteration, ",", cost)
                if self.save:
                    self.data = self.data.append({'iteration': float(iteration), 'cost': cost}, ignore_index=True)

    def mailer_disperse_msgs_to_each_mailbox(self):#disperses the messages in the agents mailboxes
        message_map = self.create_message_map(self.msg_box.msgs)
        for agent_id, msgs in message_map.items():
            receiver = self.getAgentByID(agent_id)
            receiver.mailbox.msgs.extend(msgs)
            self.removeSentMsgs(msgs)

    def removeSentMsgs(self, msgs): #empty mailbox once messages are sent
        for m in msgs:
            self.msg_box.msgs.remove(m)

    def calculateCurrentPrice(self): #calculates current cost of broken constraints
        totalCost = 0
        totalAgentView={}
        for a in self.agents:
            totalAgentView[a.agent_id]=a.variable_value
        for a in self.agents:
            totalCost += Agent.calculateCostIfUsingValue(a.variable_value, a.constraints, totalAgentView)

        return totalCost

    def getAgentByID(self, agent_id): #finds agent by id
        for a in self.agents:
            if a.agent_id == agent_id:
                return a

    def create_message_map(self, msgs_to_send): #creates a dictionary of agent id: [messages to receive]
        message_map = {}
        for msg in msgs_to_send:
            if msg.receiver_id not in message_map.keys():
                message_map[msg.receiver_id] =[msg]
            else: message_map[msg.receiver_id].append(msg)
        return message_map
