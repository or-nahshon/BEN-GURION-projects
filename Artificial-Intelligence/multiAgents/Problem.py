import Agent
import random
import Mailer
import matplotlib.pyplot as plt
import pandas
global dataDSA, dataMGM2
dataDSA = pandas.DataFrame(columns={'iteration', 'cost'})
dataMGM2 = pandas.DataFrame(columns={'iteration', 'cost'})

class Constraint(object): #constraint indicating a one sided constraint
    def __init__(self, myValue, otherAgent_id, otherAgentValue, cost):
        self.myValue = myValue
        self.otherAgent_id = otherAgent_id
        self.otherAgentValue = otherAgentValue
        self.cost = cost


class DCOP(object): #a DCOP problem instance
    def __init__(self, prob_id, randnum, p1, p2, algorithm, agents_num=30, domain_size=10):
        self.prob_id = prob_id
        self.rand = randnum
        self.algorithm = algorithm
        self.p1 = p1
        self.p2 = p2
        self.agents = self.create_problem_agents(agents_num, algorithm) #creates agents according to algorithm type
        self.create_problem_domains(domain_size)
        self.create_problem_constraints()


    def createConstraints(self, agent_one, agent_two):
        if agent_one not in agent_two.agent_view.keys(): #if theyre not neighbors yet, make them neighbors
            agent_one.agent_view[agent_two.agent_id] = None
            agent_two.agent_view[agent_one.agent_id] = None

        for i in range(len(agent_one.domain)):#creates the constraints according to p2
            for j in range(len(agent_two.domain)):
                checkp2 = self.rand.random()  # 0-1
                if checkp2 < self.p2:  # the variables are constrained
                    cost = self.rand.randint(1, 10)
                    constraint = Constraint(i, agent_two.agent_id, j, cost)
                    other_constraint = Constraint(j, agent_one.agent_id, i, cost)
                    agent_one.constraints.append(constraint)
                    agent_two.constraints.append(other_constraint)


    def create_problem_domains(self, domain_size): #creates the domains of the variables
        for a in self.agents:
            dom_var = []
            for dom in range(0, domain_size):
                dom_var.append(dom)
            a.domain = dom_var


    def create_problem_agents(self, agents_num, algorithm): #0==DSA, 1==MGM-2
        agents = []
        for i in range(agents_num):
            if algorithm == 0:
                agents.append(Agent.Agent_DSA(agent_id=i, randnum=self.rand))
            elif algorithm == 1:
                agents.append(Agent.Agent_MGM2(agent_id=i, randnum=self.rand))
        return agents

    def create_problem_constraints(self): #decides who will be neighbors and if they are then we call create constraints to find constrained values
        for i in range(len(self.agents)-1):
            for j in range(i+1, len(self.agents)):
                checkp1 = self.rand.random() #0-1
                if checkp1 < self.p1: #the variables are constrained
                    self.createConstraints(self.agents[i], self.agents[j])

class Solver(object): #creates DCOP and mailer to start the run
    def __init__(self, prob_id, randnum, algorithm, p1, p2, save=False):
        self.problem = DCOP(prob_id=prob_id, randnum=randnum, algorithm=algorithm, agents_num=30, p1=p1, p2=p2)
        self.mailer = Mailer.Mailer(self.problem, termination=1000, save=save)
        self.mailer.execute()

def printAnalysisGraph(p1,p2):

    global dataDSA, dataMGM2
    dataDSA = dataDSA[['cost', 'iteration']].groupby(['iteration'], as_index=False).mean()
    dataMGM2 = dataMGM2[['cost', 'iteration']].groupby(['iteration'], as_index=False).mean()

    print(dataDSA)
    print(dataMGM2)

    plt.plot(dataDSA['iteration'], dataDSA['cost'], label='DSA')
    plt.plot(dataMGM2['iteration'], dataMGM2['cost'], label='MGM2')
    plt.title('p1=%s, p2=%s' %(p1, p2))
    plt.xlabel('iteration')
    plt.ylabel('sum of costs')
    plt.legend()
    plt.show()


if __name__ == "__main__":

##### print for p1=0.5, p2=0.2, 0<iter<1000
    p1=0.5
    p2=0.2
    range_ = [0]  # For more accurate analysis >> add more numbers to the list (more numbers = more problems)

    for id in range_:
        s_DSA = Solver(id, random.Random(id), algorithm=0, p1=p1, p2=p2, save=True)
        s_MGM2 = Solver(id, random.Random(id), algorithm=1, p1=p1, p2=p2, save=True)

        dataDSA = dataDSA.append(s_DSA.mailer.data, ignore_index=True)
        dataMGM2 = dataMGM2.append(s_MGM2.mailer.data, ignore_index=True)

    printAnalysisGraph(p1,p2)


