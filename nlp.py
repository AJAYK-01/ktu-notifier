import nltk
nltk.download('stopwords')
nltk.download('wordnet')
import numpy as np
import tensorflow.python.keras
from tensorflow.python.keras.preprocessing.text import Tokenizer
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.layers import Conv1D
from tensorflow.python.keras.layers import Flatten
from tensorflow.python.keras.layers import MaxPooling1D
from tensorflow.python.keras.layers.embeddings import Embedding
from tensorflow.python.keras.preprocessing.sequence import pad_sequences
from string import punctuation
from os import listdir
from collections import Counter
from nltk.corpus import stopwords
from numpy import loadtxt
from tensorflow.python.keras.models import load_model
import pickle5 as pickle
from nltk.stem import WordNetLemmatizer 
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics
from sklearn.model_selection import train_test_split
  
lemmatizer = WordNetLemmatizer()

# load doc into memory
def load_doc(filename):
    # open the file as read only
    file = open(filename, 'r')
    # read all text
    text = file.read()
    # close the file
    file.close()
    return text

# turn a doc into clean tokens
def clean_doc(doc):
    # split into tokens by white space
    tokens = doc.split()
    # remove punctuation from each token
    tokens = [lemmatizer.lemmatize(w) for w in tokens]
    # remove remaining tokens that are not alphabetic
    tokens = [word for word in tokens if word.isalpha()]
    # filter out stop words
    stop_words = set(stopwords.words('english'))
    tokens = [w for w in tokens if not w in stop_words]
    # filter out short tokens
    tokens = [word for word in tokens if len(word) > 1]
    return tokens

# load doc and add to vocab
def add_doc_to_vocab(filename, vocab):
    # load doc
    doc = load_doc(filename)
    # clean doc
    tokens = clean_doc(doc)
    # update counts
    vocab.update(tokens)

# load all docs in a directory
def process_docs(directory, vocab, is_trian):
    # walk through all files in the folder
    for filename in listdir(directory):
        # create the full path of the file to open
        path = directory + '/' + filename
        # add doc to vocab
        add_doc_to_vocab(path, vocab)

# define vocab
vocab = Counter()
# add all docs to vocab
process_docs('data/neg_train', vocab, True)
process_docs('data/pos_train', vocab, True)
# print the size of the vocab
print(len(vocab))
# print the top words in the vocab
print(vocab.most_common(50))

min_occurane = 3
tokens = [k for k,c in vocab.items() if c >= min_occurane]
print(len(tokens))

# save list to file
def save_list(lines, filename):
    # convert lines to a single blob of text
    data = '\n'.join(lines)
    # open file
    file = open(filename, 'w')
    # write text
    file.write(data)
    # close file
    file.close()

# save tokens to a vocabulary file
save_list(tokens, 'vocab.txt')

# load doc into memory
def load_doc(filename):
    # open the file as read only
    file = open(filename, 'r')
    # read all text
    text = file.read()
    # close the file
    file.close()
    return text

# load the vocabulary
vocab_filename = 'vocab.txt'
vocab = load_doc(vocab_filename)
vocab = vocab.split()
vocab = set(vocab)

# turn a doc into clean tokens
def clean_doc(doc, vocab):
    # split into tokens by white space
    tokens = doc.split()
    # remove punctuation from each token
    tokens = [lemmatizer.lemmatize(w) for w in tokens]
    # filter out tokens not in vocab
    tokens = [w for w in tokens if w in vocab]
    tokens = ' '.join(tokens)
    return tokens


    # load all docs in a directory


def process_docs(directory, vocab, is_trian):
    documents = list()
    print(directory+" : ",len(listdir(directory)))
    # walk through all files in the folder
    for filename in listdir(directory):
        # skip any reviews in the test set
        # create the full path of the file to open
        path = directory + '/' + filename
           # load the doc
        doc = load_doc(path)
        # clean doc
        tokens = clean_doc(doc, vocab)
        # add to list
        documents.append(tokens)
    return documents


def make_model():
    # load all training reviews
    positive_docs = process_docs('data/pos_train', vocab, True)
    negative_docs = process_docs('data/neg_train', vocab, True)
    train_docs = negative_docs + positive_docs
    # create the tokenizer
    tokenizer = Tokenizer()
    # fit the tokenizer on the documents
    tokenizer.fit_on_texts(train_docs)
    with open('tokenizer.pickle', 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # sequence encode
    encoded_docs = tokenizer.texts_to_sequences(train_docs)

    # pad sequences
    max_length = max([len(s.split()) for s in train_docs])
    print("\n\n maxlenght="+str(max_length))

    from tensorflow.python.keras.preprocessing.sequence import pad_sequences
    X = pad_sequences(encoded_docs, maxlen=max_length, padding='post')

    # define training labels
    y = np.array([0 for _ in range(270)] + [1 for _ in range(270)])

    Xtrain, Xtest, ytrain, ytest = train_test_split(X, y, test_size=0.30, random_state=42)
    '''
    # load all test reviews
    positive_docs = process_docs('data/pos_test', vocab, False)
    negative_docs = process_docs('data/neg_test', vocab, False)
    test_docs = negative_docs + positive_docs
    # sequence encode
    encoded_docs = tokenizer.texts_to_sequences(test_docs)
    # pad sequences
    Xtest = pad_sequences(encoded_docs, maxlen=max_length, padding='post')
    # define test labels
    ytest = np.array([0 for _ in range(len(listdir("data/neg_test")))] + [1 for _ in range(len(listdir("data/pos_test")))])
    '''
    print("\n pad_sequences : ",Xtest)
    print("\n ytest : ",ytest)

    # define vocabulary size (largest integer value)
    vocab_size = len(tokenizer.word_index) + 1

    # define model
    model = Sequential()
    model.add(Embedding(vocab_size, 100, input_length=max_length))
    model.add(Conv1D(filters=64, kernel_size=8, activation='relu'))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Conv1D(filters=32, kernel_size=8, activation='relu'))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Flatten())
    model.add(Dense(10, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    print(model.summary())
    # compile network
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    # fit network
    model.fit(Xtrain, ytrain, epochs=20, verbose=1)
    # evaluate
    loss, acc = model.evaluate(Xtest, ytest, verbose=0)
    print('Test Accuracy: %f' % (acc*100))

    model.save("relevancy_model_v2.0.1.h5")
    print("Done!")

def make_model_NB():
    # load all training reviews
    positive_docs = process_docs('data/pos_train', vocab, True)
    negative_docs = process_docs('data/neg_train', vocab, True)
    train_docs = negative_docs + positive_docs
    # create the tokenizer
    tokenizer = Tokenizer()
    # fit the tokenizer on the documents
    tokenizer.fit_on_texts(train_docs)
    with open('tokenizer.pickle', 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # sequence encode
    encoded_docs = tokenizer.texts_to_sequences(train_docs)

    # pad sequences
    max_length = max([len(s.split()) for s in train_docs])
    print("\n\n maxlenght="+str(max_length))

    from tensorflow.python.keras.preprocessing.sequence import pad_sequences
    Xtrain = pad_sequences(encoded_docs, maxlen=max_length, padding='post')

    # define training labels
    ytrain = np.array([0 for _ in range(250)] + [1 for _ in range(250)])

    # load all test reviews
    positive_docs = process_docs('data/pos_test', vocab, False)
    negative_docs = process_docs('data/neg_test', vocab, False)
    test_docs = negative_docs + positive_docs
    # sequence encode
    encoded_docs = tokenizer.texts_to_sequences(test_docs)
    # pad sequences
    Xtest = pad_sequences(encoded_docs, maxlen=max_length, padding='post')
    # define test labels
    ytest = np.array([0 for _ in range(len(listdir("data/neg_test")))] + [1 for _ in range(len(listdir("data/pos_test")))])

    print("\n pad_sequences : ",Xtest)
    print("\n ytest : ",ytest)
    gnb = GaussianNB()
    gnb.fit(Xtrain, ytrain)
    
    # making predictions on the testing set
    y_pred = gnb.predict(Xtest)

    print("Gaussian Naive Bayes model accuracy(in %):", metrics.accuracy_score(ytest, y_pred)*100)


def predict_process_docs(doc,vocab):
    documents = list()
    # clean doc
    tokens = clean_doc(doc, vocab)
    # add to list
    documents.append(tokens)
    return documents

def predict(doc):
    predict_docs = predict_process_docs(doc,vocab)

    with open('tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    encoded_docs = tokenizer.texts_to_sequences(predict_docs)

    X = pad_sequences(encoded_docs, maxlen=94, padding='post')
    # load model
    model = load_model('relevancy_model.h5')
    y=model.predict_classes(np.array(X))
    if (y == [[1]]) :
        #print("\nRelevant \n")
        return(1)
    else :
        #print("\nIrrelevant \n")   
        return(0)




def relevant(notif):
    """ Checks for relevance of the notification content """ 
    result=predict(notif)
    print(result)
    if (result == 1) :
        return 1
    else :
        return 0 


if __name__ == "__main__":
    result=predict(" It is here by notified that the result of B.Tech S5 (S) Exam July 2019 is published. The detailed results are available in the KTU website: www.ktu.edu.in. Students can apply for answer script copy and revaluation by registering in the KTU web portal from 28.10.2019 Monday to 01.11.2019 Friday. The Fee for answer script copy is Rs.500/- per answer script and for revaluation Rs. 600/- per answer script. Students should submit their requests through student login and pay the fee at College office on or before 01.11.2019 Friday. Requests for late registration for revaluation and answer book copy will not be entertained. However in case of technical issues the request will be considered only if the matter is reported to University before the last date with proof.Result Notification - S5 (S)")
    print(result)
    if (result == 1) :
        print("relevant")
    else :
        print("Irrelevant") 
