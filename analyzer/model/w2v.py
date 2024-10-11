from gensim.models.phrases import Phrases, Phraser
from gensim.models import Word2Vec
import multiprocessing
import pandas as pd
from sklearn.cluster import KMeans
import joblib


def w2v_model(df: pd.DataFrame) -> None:
    """
    Train a word2vec model from a DataFrame of comments.

    The model is saved to a file named './model/w2v_model.pkl'.

    Parameters
    ----------
    df : pd.DataFrame
        A DataFrame with a single column 'comment' containing the text
        comments.
    """
    sent = [row.split() for row in df['comment']]
    cores = multiprocessing.cpu_count() 
    phrases = Phrases(sent, min_count=10, progress_per=10000)
    bigram = Phraser(phrases)
    sentences = bigram[sent]

    w2v_model = Word2Vec(
        min_count=20,
        window=2,
        vector_size=300,
        sample=6e-5,
        alpha=0.03,
        min_alpha=0.0007,
        negative=20,
        workers=cores-1
    )
    w2v_model.build_vocab(sentences, progress_per=10000)
    w2v_model.train(
        sentences,
        total_examples=w2v_model.corpus_count,
        epochs=30,
        report_delay=1
    )
    w2v_model.init_sims(replace=True)
    w2v_model.save("./analyzer/model/w2vmodel.model")


def kmeans_clusters(pd: pd.DataFrame) -> None:
    """
    Use the word2vec model generated by the function w2v_model to cluster the
    words into two clusters using k-means clustering.

    The function prints the 10 words closest to the center of the positive
    cluster.
    """
    word_vectors = Word2Vec.load("./analyzer/model/w2vmodel.model").wv
    kmeans_model = KMeans(
        n_clusters=2, max_iter=1000, random_state=True, n_init=50
    ).fit(X=word_vectors.vectors)
    positive_cluster_center = kmeans_model.cluster_centers_[0]
    negative_cluster_center = kmeans_model.cluster_centers_[1]
    print(
        word_vectors.similar_by_vector(
            kmeans_model.cluster_centers_[0], topn=10, restrict_vocab=None
        )
    )


