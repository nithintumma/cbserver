from sklearn.naive_bayes import MultinomialNB
from scipy import sparse
import numpy as np


#TODO: recluster user vector, find top model for them 
#TODO: reclassify recommendations

X = np.array([[0, 0, 0, 4, 2, 0, 0, 0, 0, 0],
[0, 0, 3, 0, 5, 0, 0, 0, 0, 0],
[5, 5, 0, 0, 0, 0, 0, 0, 0, 0],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 4],
[0, 5, 0, 4, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 1, 2, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 4, 5]
])

A = np.array([[3, 0, 0, 4, 0, 0, 0, 0, 0, 0],
[0, 0, 3, 0, 0, 0, 0, 0, 0, 2],
[0, 5, 0, 0, 0, 3, 0, 0, 0, 0],
[0, 0, 1, 0, 3, 0, 0, 0, 0, 4],
[0, 5, 0, 0, 4, 0, 0, 0, 0, 0],
[0, 0, 0, 1, 0, 0, 5, 0, 0, 0],
[0, 0, 0, 0, 3, 0, 5, 0, 0, 0]
])


y= np.array([1, 1, 2, 2, 3, 3, 3])
mnb = MultinomialNB()
mnb.fit(sparse.csr_matrix(X), y)
#print X.shape
#print mnb.feature_log_prob_[0]
#print mnb.coef_.shape

print mnb.predict(X).shape

anb = MultinomialNB()
anb.fit(sparse.csr_matrix(A), y)
#print anb.feature_log_prob_[0]
#print np.exp(mnb.feature_log_prob_)[0]
#print np.exp(anb.feature_log_prob_)[0]
