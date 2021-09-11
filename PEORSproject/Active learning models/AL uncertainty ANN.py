
import matplotlib
import numpy as np

RANDOM_STATE_SEED = 1
np.random.seed(RANDOM_STATE_SEED)

from sklearn.datasets import load_iris
iris = load_iris()
X_raw = iris['data']
y_raw = iris['target']

from sklearn.decomposition import PCA

# Define our PCA transformer and fit it onto our raw dataset.
pca = PCA(n_components=2, random_state=RANDOM_STATE_SEED)
transformed_iris = pca.fit_transform(X=X_raw)

import matplotlib as mpl
import matplotlib.pyplot as plt

# Isolate the data we'll need for plotting.
x_component, y_component = transformed_iris[:, 0], transformed_iris[:, 1]
# Plot our dimensionality-reduced (via PCA) dataset.
plt.figure(figsize=(8.5, 6), dpi=130)
plt.scatter(x=x_component, y=y_component, c=y_raw, cmap='viridis', s=50, alpha=8/10)
plt.title('Iris classes after PCA transformation')
plt.show()


# Isolate our examples for our labeled dataset.
n_labeled_examples = X_raw.shape[0]
training_indices = np.random.randint(low=0, high=n_labeled_examples + 1, size=3)

X_train = X_raw[training_indices]
y_train = y_raw[training_indices]

X_pool = np.delete(X_raw, training_indices, axis=0)
y_pool = np.delete(y_raw, training_indices, axis=0)

# initialize the learner

from sklearn.ensemble import RandomForestClassifier
from modAL.models import ActiveLearner
from modAL.uncertainty import classifier_uncertainty, uncertainty_sampling
from sklearn.neural_network import MLPClassifier

# Specify our core estimator along with it's active learning model.
learner = ActiveLearner(estimator=MLPClassifier(max_iter=2000), X_training=X_train, query_strategy=uncertainty_sampling, y_training=y_train)

# Isolate the data we'll need for plotting.
predictions = learner.predict(X_raw)
is_correct = (predictions == y_raw)

unqueried_score = learner.score(X_raw, y_raw)
print('Initial prediction accuracy: %f' % unqueried_score)

# Plot our classification results.
fig, ax = plt.subplots(figsize=(8.5, 6), dpi=130)
ax.scatter(x=x_component[is_correct],  y=y_component[is_correct],  c='g', marker='+', label='Correct',   alpha=8/10)
ax.scatter(x=x_component[~is_correct], y=y_component[~is_correct], c='r', marker='x', label='Incorrect', alpha=8/10)
ax.legend(loc='lower right')
ax.set_title("ActiveLearner class predictions (Accuracy: {score:.3f})".format(score=unqueried_score))
plt.show()



performance_history = [unqueried_score]

# learning until the accuracy reaches a given threshold
N_QUERIES =0
while learner.score(X_raw, y_raw) < 0.9 or len(X_pool)>0:
    try:
        query_idx, query_inst = learner.query(X_pool=X_pool)
    except:
        print('X_pool is empty')
        break
    uncertainty = classifier_uncertainty(learner, query_inst.reshape(1, -1))
    if uncertainty >= 0.3:
        N_QUERIES +=1
        X, y = X_pool[query_idx].reshape(1, -1), y_pool[query_idx].reshape(1, )
        learner.teach(X=X, y=y)
        new_score = learner.score(X_raw, y_raw)
        performance_history.append(new_score)
        print('sample no. %d queried, new accuracy: %f,uncertainty %f' % (query_idx, new_score, uncertainty))
    else:
        # predict
        y_predict=learner.predict(query_inst.reshape(1, -1))
        print('sample no. %d predict %f,uncertainty %f' % (query_idx, y_predict, uncertainty))
    X_pool, y_pool = np.delete(X_pool, query_idx, axis=0), np.delete(y_pool, query_idx)

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

# Isolate the data we'll need for plotting.
predictions = learner.predict(X_raw)
is_correct = (predictions == y_raw)

# Plot our updated classification results once we've trained our learner.
fig, ax = plt.subplots(figsize=(8.5, 6), dpi=130)

ax.scatter(x=x_component[is_correct],  y=y_component[is_correct],  c='g', marker='+', label='Correct',   alpha=8/10)
ax.scatter(x=x_component[~is_correct], y=y_component[~is_correct], c='r', marker='x', label='Incorrect', alpha=8/10)

ax.set_title('Classification accuracy after {n} queries: {final_acc:.3f}'.format(n=N_QUERIES, final_acc=performance_history[-1]))
ax.legend(loc='lower right')

plt.show()