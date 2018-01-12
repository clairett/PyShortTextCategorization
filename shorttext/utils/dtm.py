
import numpy as np
from gensim.corpora import Dictionary
from gensim.models import TfidfModel
from scipy.sparse import dok_matrix
import pandas as pd


class DocumentTermMatrix:
    """ Document-term matrix for corpus.

    This is a class that handles the document-term matrix (DTM). With a given corpus, users can
    retrieve term frequency, document frequency, and total term frequency. Weighing using tf-idf
    can be applied.
    """
    def __init__(self, corpus, docids=None, tfidf=False):
        """ Initialize the document-term matrix (DTM) class with a given corpus.

        If document IDs (docids) are given, it will be stored and output as approrpriate.
        If not, the documents are indexed by numbers.

        Users can choose to weigh by tf-idf. The default is not to weigh.

        The corpus has to be a list of lists, with each of the inside list contains all the tokens
        in each document.

        :param corpus: corpus.
        :param docids: list of designated document IDs. (Default: None)
        :param tfidf: whether to weigh using tf-idf. (Default: False)
        :type corpus: list
        :type docids: list
        :type tfidf: bool
        """
        if docids == None:
            self.docid_dict = {i: i for i in range(len(corpus))}
            self.docids = range(len(corpus))
        else:
            if len(docids) == len(corpus):
                self.docid_dict = {docid: i for i, docid in enumerate(docids)}
                self.docids = docids
            elif len(docids) > len(corpus):
                self.docid_dict = {docid: i for i, docid in zip(range(len(corpus)), docids[:len(corpus)])}
                self.docids = docids[:len(corpus)]
            else:
                self.docid_dict = {docid: i for i, docid in enumerate(docids)}
                self.docid_dict = {i: i for i in range(len(docids), range(corpus))}
                self.docids = docids + range(len(docids), range(corpus))
        # generate DTM
        self.generate_dtm(corpus, tfidf=tfidf)

    def generate_dtm(self, corpus, tfidf=False):
        """ Generate the inside document-term matrix and other peripherical information
        objects. This is run when the class is instantiated.

        :param corpus: corpus.
        :param tfidf: whether to weigh using tf-idf. (Default: False)
        :return: None
        :type corpus: list
        :type tfidf: bool
        """
        self.dictionary = Dictionary(corpus)
        self.dtm = dok_matrix((len(corpus), len(self.dictionary)), dtype=np.float)
        bow_corpus = [self.dictionary.doc2bow(doctokens) for doctokens in corpus]
        if tfidf:
            weighted_model = TfidfModel(bow_corpus)
            bow_corpus = weighted_model[bow_corpus]
        for docid in self.docids:
            for tokenid, count in bow_corpus[self.docid_dict[docid]]:
                self.dtm[self.docid_dict[docid], tokenid] = count

    def get_termfreq(self, docid, token):
        """ Retrieve the term frequency of a given token in a particular document.

        Given a token and a particular document ID, compute the term frequency for this
        token. If `tfidf` is set to `True` while instantiating the class, it returns the weighted
        term frequency.

        :param docid: document ID
        :param token: term or token
        :return: term frequency or weighted term frequency of the given token in this document (designated by docid)
        :type docid: any
        :type token: str
        :rtype: numpy.float
        """
        return self.dtm[self.docid_dict[docid], self.dictionary.token2id[token]]

    def get_total_termfreq(self, token):
        """ Retrieve the total occurrences of the given token.

        Compute the total occurrences of the term in all documents. If `tfidf` is set to `True`
        while instantiating the class, it returns the sum of weighted term frequency.

        :param token: term or token
        :return: total occurrences of the given token
        :type token: str
        :rtype: numpy.float
        """
        return sum(self.dtm[:, self.dictionary.token2id[token]].values())

    def get_doc_frequency(self, token):
        """ Retrieve the document frequency of the given token.

        Compute the document frequency of the given token, i.e., the number of documents
        that this token can be found.

        :param token: term or token
        :return: document frequency of the given token
        :type token: str
        :rtype: int
        """
        return len(self.dtm[:, self.dictionary.token2id[token]].values())

    def get_token_occurences(self, token):
        """ Retrieve the term frequencies of a given token in all documents.

        Compute the term frequencies of the given token for all the documents. If `tfidf` is
        set to be `True` while instantiating the class, it returns the weighted term frequencies.

        This method returns a dictionary of term frequencies with the corresponding document IDs
        as the keys.

        :param token: term or token
        :return: a dictionary of term frequencies with the corresponding document IDs as the keys
        :type token: str
        :rtype: dict
        """
        return {self.docid_dict[docidx]: count for (docidx, _), count in self.dtm[:, token].items()}

    def get_doc_tokens(self, docid):
        """ Retrieve the term frequencies of all tokens in the given document.

        Compute the term frequencies of all tokens for the given document. If `tfidf` is
        set to be `True` while instantiating the class, it returns the weighted term frequencies.

        This method returns a dictionary of term frequencies with the tokens as the keys.

        :param docid: document ID
        :return: a dictionary of term frequencies with the tokens as the keys
        :type docid: any
        :rtype: dict
        """
        return {self.dictionary.token2id[tokenid]: count for (_, tokenid), count in self.dtm[self.docid_dict[docid], :].items()}

    def generate_dtm_dataframe(self):
        """ Generate the data frame of the document-term matrix.

        :return: data frame of the document-term matrix
        :rtype: pandas.DataFrame
        """
        tbl = pd.DataFrame(self.dtm.toarray())
        tbl.index = self.docids
        tbl.columns = map(lambda i: self.dictionary[i], range(len(self.dictionary)))
        return tbl