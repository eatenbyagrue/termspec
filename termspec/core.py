# -*- coding: utf-8 -*-

from helpers import helpers as util
import numpy as np
import json #just for printing!
from nltk.tokenize import sent_tokenize, word_tokenize
from scipy.spatial.distance import pdist, squareform
from sklearn.feature_extraction.text import CountVectorizer



def retrieve_data_and_tokenize():
	"""Retrieves the data from the source and makes a neat array of words, sentences and documents out of it.
	[ #docs
		[ #document1
			['word1','word2','word3'], #sentence1
			['word1','word2','word3'], #sentence2
		],
		[ #document2
			['word1','word2','word3'], #sentence1
			['word1','word2','word3'], #sentence2
		]
	]

	"""

	docs = ['foo bar bar. boom bam bum. foo', 'foo baz bar', 'foo foo baz baz', 'foo', 'bar derp']

	# docs = (
	# 	"There is no single concept of cool. One of the essential characteristics of cool is its mutability — what is considered cool changes over time and varies among cultures and generations.",
	# 	"One consistent aspect however, is that  is wildly seen as positive and desirable.",
	# 	"The sum and substance of cool is a self-conscious aplomb in overall behavior, which entails a set of specific behavioral characteristics that is firmly anchored in symbology, a set of discernible bodily movements, postures, facial expressions and voice modulations that are acquired and take on strategic social value within the peer context.",
	# 	"Cool was once an attitude fostered by rebels and underdogs, such as slaves, prisoners, bikers and political dissidents, etc., for whom open rebellion invited punishment, so it hid defiance behind a wall of ironic detachment, distancing itself from the source of authority rather than directly confronting it."
	# 	)


	return_docs = []
	for doc in docs:
		sents = sent_tokenize(doc)
		sents = [word_tokenize(sent) for sent in sents]
		sents = [util.normalize(sent) for sent in sents]
		return_docs.append(sents)

	return return_docs

def compute_cooccurrence_matrix(docs):

	# Sentences have to be rejoined. The CountVectorizer only likes strings as document inputs.
	# Then calculates token count per document (in our case each sentence = one document).
	sents = []
	for doc in docs:
		sents.extend([' '.join(sent) for sent in doc])

	count_model = CountVectorizer(ngram_range=(1,1))

	# Counts each cooccurrence and returns a document-word matrix.
	X = count_model.fit_transform(sents)

	# X is now a document-word matrix, but we want a word-word-matrix.
	# The value i,j of the matrix is the count of the word j in document (i.e. sentence) i.
	# Xc ist the word-word-matrix computed from Xc by multiplying with a transponent (?)
	Xc = (X.T * X)

	# Main diagonal to 0, useless anyway.
	Xc.setdiag(0)

	# The Matrix is filled with zero and transformed to the numpy array format.
	M = np.asarray(Xc.todense())

	# These are just all the terms for later reference. important!
	# The c indicates that this data structures should be constant: it depends on its ordering, others might use the exact ordering to map term names and values.
	# Python probably has a better data structure for this (tuples)
	c_fns = count_model.get_feature_names()

	#TODO: Throw out all-zero vectors!

	# How great is just returning two values? Seriously? python ftw
	return M, c_fns

def compute_cosine_similarity_matrix(M):
	"""Calculate the cosine distance for each row in the context matrix with each other.
	I.e. calculate all cosine distances between each cooccurrence vector.

	Takes a 2 dimensional ndarray
	Returns a 2 dimensional ndarray
	"""

	Y = pdist(M,metric='cosine')
	# make the cosine distance matrix readable
	Y = squareform(Y)
	# #take not the cosine distance, but similarity (applied per cell)
	Y = 1 - Y
	return Y

def get_idf_for_word():
	return 0

# All the computed values that can be evaluated later on
results = {}

docs = retrieve_data_and_tokenize()

X, c_fns = compute_cooccurrence_matrix(docs)
util.printprettymatrix(X, c_fns)

Y= compute_cosine_similarity_matrix(X)

# find the context for the specificity term with cooccurrence not 0
sterm = 'foo'
# this is sterm's row of the cooccurence matrix i.e. sterm's context vector
c_context_vector = X[c_fns.index(sterm)]

#remove all zero elements
nonzero_indices = np.flatnonzero(c_context_vector)

#retrieve all context terms that stand in actual cooccurrence with sterm
context_terms = [c_fns[i] for i in nonzero_indices]

util.printprettymatrix(Y, c_fns)


