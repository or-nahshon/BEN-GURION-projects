import numpy as np
import pandas as pd
from scipy.stats import chi2

df = None
counter= 0


class BranchNode(object):  # create an Object- to make one node
    def __init__(self, question, data, terms):

        self.question = question
        self.data= data
        self.terms=terms
        self.subTrees=[]

        global counter
        self.id = counter
        counter+=1

    def __str__(self):
        if isinstance(self.subTrees[0], BranchNode):
            x = "Go To question number %s" %self.subTrees[0].id
        else:
            x = self.subTrees[0]

        if isinstance(self.subTrees[1], BranchNode):
            y = "Go To question number %s" % self.subTrees[1].id
        else:
            y = self.subTrees[1]

        str = "\n question number %s : %s" % (self.id, self.question)
        str1= "\n if [%s]<=%s -->> %s ;" % (self.question,self.terms[0],x)
        str2= "else -->> %s" % (y)

        return str+str1+str2


def read_file(path):
    global df
    df = pd.read_csv(path, skiprows=[0])
    df = df.drop(columns='ID')


def split_data(ratio):
    '''if k=0.6 return random 60% data as dataset, and else as valid'''
    train = df.sample(frac=ratio, random_state=0)  # random state is a seed value
    test = df.drop(train.index)
    return train, test


def tree_error(k: int):
    read_file("DefaultOfCreditCardClients.csv")
    Kfolds = np.array_split(df, k)
    totalError = 0
    for i in range(k):
        trainSet = pd.concat([Kfolds[j] for j in range(k) if j is not i])
        validSet = Kfolds[i]
        attributes = [i for i in trainSet.columns if i != 'default payment next month']
        root = decision_tree_learning(trainSet, attributes)
        pruning(root)
        totalError += calculate_errors(root, validSet)/len(validSet)
    print('\n \n the ERROR is: ', totalError/k)


def build_tree(k: float):
    read_file("DefaultOfCreditCardClients.csv")
    trainSet, validSet = split_data(k)
    attributes = [i for i in trainSet.columns if i != 'default payment next month' ]
    root = decision_tree_learning(trainSet, attributes)
    pruning(root)
    print_tree(root)
    error = calculate_errors(root, validSet)
    try:
        print('\n \n the ERROR is: ', error / len(validSet))
    except: #for case k=1 so there is not valid test
        print('\n \n can not calculate error cuz k=1 and there is no valid test ')

def pruning(node):
    if isinstance(node, str):
        return None, node

    if node == None:  # using Chi square test
        return None, -1

    NodeFalse, ansFalse = pruning(node.subTrees[0])
    if NodeFalse is None:
        node.subTrees[0] = ansFalse

    NodeTrue, ansTrue = pruning(node.subTrees[1])
    if NodeTrue is None:
        node.subTrees[1] = ansTrue

    if NodeTrue is None or NodeFalse is None:
        splitesData = partition(node)
        FalseData = splitesData[0]
        TrueData = splitesData[1]
    else:
        FalseData = NodeFalse.data
        TrueData = NodeTrue.data
    if chi_squre_test(node, FalseData, TrueData):
        yes, no = count_defaulted(node.data)
        ans = 'default' if no < yes else 'not default'
        return None, ans
    else:
        return node, -1



def chi_squre_test(node, FalseData, TrueData):  # Chi square test, calculate the statistical
    pl = 0  # value and using chi library to get the critical value
    pr = 0
    RNeg = 0
    RPos = 0
    LPos = 0
    LNeg = 0
    yes, no = count_defaulted(node.data)
    if node.subTrees[0] is not None:
        LPos, LNeg = count_defaulted(FalseData)
        pl = len(FalseData) / len(node.data)

    if node.subTrees[1] is not  None:
        RPos, RNeg = count_defaulted(TrueData)
        pr = len(TrueData) / len(node.data)
    expectedL = pl * no
    expectedR = pr * yes
    if expectedL == 0:
        k1 = 0
    else:
        k1 = ((((expectedL - LNeg) ** 2) / expectedL) +
              (((expectedL - LPos) ** 2) / expectedL))
    if expectedR == 0:
        k2 = 0
    else:
        k2 = ((((expectedR - RNeg) ** 2) / expectedR) +
              (((expectedR - RPos) ** 2) / expectedR))
    k = k1 + k2
    p = 0.95
    NumOfElements = len(node.data)
    df = NumOfElements - 1  # number of freedom degree
    value = chi2.ppf(p, df)
    Chi_Kriti = value  # the critical value
    Chi_Statisti = k
    return (Chi_Kriti <= Chi_Statisti)



def print_tree(node):  # printing the tree recursively
    if isinstance(node, BranchNode):
        print(node)
        for subTree in node.subTrees:
            print_tree(subTree)


def decision_tree_learning(data,attributes, parent=None):

    if len(data) == 0:
        yes, no = count_defaulted(parent.data)
        return 'default' if no<yes else 'not default'

    checkClass = find_classification(data)
    if checkClass is not None: #same classifiction
        return checkClass

    if len(attributes) == 0:
        yes, no = count_defaulted(data)
        return 'default' if no < yes else 'not default'

    branch = get_best_branch(data, attributes)

    splitedData = partition(branch)
    arr = attributes.copy()
    arr.remove(branch.question)
    for i in splitedData.keys():
        subTree = decision_tree_learning(splitedData[i], arr, branch)
        branch.subTrees.append(subTree)

    return branch


def find_classification(data):
    yes, no = count_defaulted(data)
    if yes == len(data):
        return 'default'
    if no == len(data):
        return 'not default'
    return None


def partition(branch):  # sorting the data into two groups by the threshold
    data = branch.data
    col = branch.question
    terms = branch.terms

    ans = {}
    value = terms[0]
    ans[0] = data.loc[data[col] <= value]
    ans[1] = data.loc[data[col] > value]

    return ans


def get_best_branch(data, attributes):

    tot_entropy = calculate_entropy(data)

    bestGain=-1
    bestQ = None
    bestTerms = None

    for key in attributes:
        remainderEntropy, terms = remainder_entropy(data, key)
        gain = tot_entropy - remainderEntropy

        if gain > bestGain:
            bestGain = gain
            bestQ = key
            bestTerms = terms

    branch = BranchNode(bestQ, data, bestTerms)
    return branch


def remainder_entropy(data, col):

    term = [find_thresholds(data, col)]
    data_for_value1 = data.loc[data[col] <= term[0]]
    data_for_value2 = data.loc[data[col] > term[0]]
    attribute_entropy1 = calculate_entropy(data_for_value1)
    attribute_entropy2 = calculate_entropy(data_for_value2)
    entropy = len(data_for_value1) / len(data) * attribute_entropy1 + len(data_for_value2) / len(data) * attribute_entropy2
    return entropy, term


def find_thresholds(data, col):  # decide for each column how will be the threshold
    yes, no = count_defaulted(data)
    values = list(data[col].values)
    values.sort()
    thresholds = (values[no])  # to decide which value will split this column
    return thresholds


def calculate_entropy(data):
    if len(data) == 0:
        return 0
    yes, no = count_defaulted(data)
    pr_yes = yes / (yes + no)
    pr_no = no / (yes + no)
    if pr_no == 0 or pr_yes == 0:
        return 0
    return - (pr_yes * np.math.log2(pr_yes) + pr_no * np.math.log2(pr_no))


def count_defaulted(data):  # counting the number of default we got
    if len(data)==0:
        return 0,0
    yes = data.sum()['default payment next month']
    no = len(data) - yes
    return yes, no


def defaulted_check(row, root):  # returns the decision of the tree
    answer = None
    while answer is None:
        if row[root.question] <= root.terms[0]:
            nextStep = root.subTrees[0]
        else:
            nextStep = root.subTrees[1]

        if isinstance(nextStep, str):
            answer = nextStep
        else:
            root = nextStep

    return answer


def will_default(array: list):
    array_changed = [int(i) for i in array]
    read_file("DefaultOfCreditCardClients.csv")
    attributes = [i for i in df.columns if i != 'default payment next month' and i!='ID']
    row = dict(zip(attributes, array_changed))

    root = decision_tree_learning(df, attributes)
    pruning(root)

    print(defaulted_check(row, root))


def calculate_errors(root, data):
    error = 0
    for i in range(len(data)):
        row = data.iloc[i, :]
        ans = row['default payment next month']
        if ans == 1:
            ans = 'default'
        else:
            ans = 'not default'
        predict = defaulted_check(row, root)
        if ans != predict:
            error = error + 1
    return error


if __name__ == "__main__":
    build_tree(0.8)
    #tree_error(3)
    #will_default( [30000,1,2,2,30,1,2,2,0,0,2,65802,67369,65701,66782,36137,36894,3200,0,3000,3000,1500,0])