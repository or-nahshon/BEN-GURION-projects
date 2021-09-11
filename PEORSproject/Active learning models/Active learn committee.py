
import numpy as np
RANDOM_STATE_SEED = 10
np.random.seed(RANDOM_STATE_SEED)

from sklearn.datasets import load_iris
iris = load_iris()
X_raw = iris['data']
y_raw = iris['target']

from sklearn.decomposition import PCA

# Define our PCA transformer and fit it onto our raw dataset.
pca = PCA(n_components=2).fit_transform(X=X_raw)

import matplotlib as mpl
import matplotlib.pyplot as plt

# Plot our dimensionality-reduced (via PCA) dataset.
plt.figure(figsize=(8.5, 6), dpi=130)
plt.scatter(x=pca[:, 0], y=pca[:, 1], c=iris['target'], cmap='viridis', s=50, alpha=8/10)
plt.title('Iris classes after PCA transformation')
plt.show()

# Isolate our examples for our labeled dataset.
n_labeled_examples = X_raw.shape[0]
training_indices = np.random.randint(low=0, high=n_labeled_examples + 1, size=3)

X_train = X_raw[training_indices]
y_train = y_raw[training_indices]

# initialize the learner
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier

from modAL.models import ActiveLearner
from modAL.uncertainty import classifier_uncertainty, uncertainty_sampling

# Specify our core estimator along with it's active learning model.
# initializing Committee members
knn = KNeighborsClassifier(n_neighbors=3)
forest = RandomForestClassifier()
ann = MLPClassifier(max_iter=1000)
models = (knn, forest, ann)
numbOfModels = len(models)
learner_list = list()

for model in models:
    # initial training data
    X_pool = np.delete(X_raw, training_indices, axis=0)
    y_pool = np.delete(y_raw, training_indices, axis=0)

    # initializing learner
    learner = ActiveLearner(estimator=model, X_training=X_train, y_training=y_train)
    learner_list.append(learner)

# assembling the committee
from modAL import Committee
committee = Committee(learner_list=learner_list)


with plt.style.context('seaborn-white'):
    plt.figure(figsize=(numbOfModels*7, 7))
    for learner_idx, learner in enumerate(committee):

        predictions = learner.predict(X_raw)
        is_correct = (predictions == y_raw)
        unqueried_score = learner.score(X_raw, y_raw)
        print('Initial prediction for model no. %s accuracy: %f' % (learner_idx, unqueried_score))
        # Plot our classification results.
        ax = plt.subplot(1, numbOfModels, learner_idx + 1)
        #plt.subplot(1, numbOfModels, learner_idx + 1)
        ax.scatter(x=pca[:, 0][is_correct], y=pca[:, 1][is_correct], c='g', marker='+', label='Correct',
                  alpha=8 / 10)
        ax.scatter(x=pca[:, 0][~is_correct], y=pca[:, 1][~is_correct], c='r', marker='x', label='Incorrect',
                   alpha=8 / 10)
        ax.set_title('model no. {n} initial predictions  (Accuracy: {score:.3f})'.format(n=learner_idx+1, score=unqueried_score))
        plt.title('model no. %d initial predictions' % (learner_idx))
    plt.show()



performance_history = [unqueried_score]

# learning until the accuracy reaches a given threshold
N_QUERIES =0
while committee.score(X_raw, y_raw) < 0.9 or len(X_pool)>0:
    try:
        query_idx, query_inst = committee.query( X_pool=X_pool)
    except:
        print('X_pool is empty')
        break
    uncertainty = classifier_uncertainty(committee, query_inst.reshape(1, -1))
    if uncertainty >= 0.3:
        N_QUERIES +=1
        X, y = X_pool[query_idx].reshape(1, -1), y_pool[query_idx].reshape(1, )
        committee.teach(X=X, y=y)
        new_score = committee.score(X_raw, y_raw)
        performance_history.append(new_score)
        print('sample no. %d queried, new accuracy: %f,uncertainty %f' % (query_idx, new_score, uncertainty))
    else:
        # predict
        y_predict=committee.predict(query_inst.reshape(1, -1))
        print('sample no. %d predict %f,uncertainty %f' % (query_idx, y_predict, uncertainty))

    X_pool, y_pool = np.delete(X_pool, query_idx, axis=0), np.delete(y_pool, query_idx)



# visualizing the final predictions per learner
with plt.style.context('seaborn-white'):
    plt.figure(figsize=(numbOfModels*7, 7))
    for learner_idx, learner in enumerate(committee):
        predictions = learner.predict(X_raw)
        is_correct = (predictions == y_raw)
        learner_score = learner.score(X_raw, y_raw)
        ax = plt.subplot(1, numbOfModels, learner_idx + 1)
        ax.scatter(x=pca[:, 0][is_correct], y=pca[:, 1][is_correct], c='g', marker='+', label='Correct',
                   alpha=8 / 10)
        ax.scatter(x=pca[:, 0][~is_correct], y=pca[:, 1][~is_correct], c='r', marker='x', label='Incorrect',
                   alpha=8 / 10)
        plt.title('model no. {n} final predictions after {d} queries (Accuracy: {score:.3f})'.format(n=learner_idx,d= N_QUERIES, score=learner_score))
    plt.show()

# visualizing the Committee's predictions
with plt.style.context('seaborn-white'):
    plt.figure(figsize=(8.5, 6), dpi=130)
    prediction = committee.predict(X_raw)
    plt.scatter(x=pca[:, 0], y=pca[:, 1], c=prediction, cmap='viridis', s=50,  alpha=8 / 10)
    plt.title('Committee predictions after %d queries, accuracy = %1.3f'
              % (N_QUERIES, committee.score(X_raw, y_raw)))
    plt.show()


## visualizing the Committee's predictions - correct or not
# Isolate the data we'll need for plotting.
predictions = model.predict(X_raw)
is_correct = (predictions == y_raw)

# Plot our updated classification results once we've trained our learner.
fig, ax = plt.subplots(figsize=(8.5, 6), dpi=130)

ax.scatter(x=pca[:, 0][is_correct],  y=pca[:, 1][is_correct],  c='g', marker='+', label='Correct',   alpha=8/10)
ax.scatter(x=pca[:, 0][~is_correct], y=pca[:, 1][~is_correct], c='r', marker='x', label='Incorrect', alpha=8/10)
plt.title('Committee predictions after %d queries, accuracy = %1.3f'
          % (N_QUERIES, committee.score(X_raw, y_raw)))
ax.legend(loc='lower right')
plt.show()


# Plot our performance over time.
fig, ax = plt.subplots(figsize=(8.5, 6), dpi=130)

ax.plot(performance_history)
ax.scatter(range(len(performance_history)), performance_history, s=13)

ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=5, integer=True))
ax.yaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=10))
ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(xmax=1))

ax.set_ylim(bottom=0, top=1)
ax.grid(True)

ax.set_title('Incremental classification accuracy')
ax.set_xlabel('Query iteration')
ax.set_ylabel('Classification Accuracy')

plt.show()
