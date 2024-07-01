# -*- coding: utf-8 -*-

import jieba
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import KMeans
import json

class K_meansClustering():
    def __init__(self, maxCorpusSize, stopwords_path=None):
        # self.stopwords = self.load_stopwords(stopwords_path)
        self.vectorizer = CountVectorizer()
        self.transformer = TfidfTransformer()
        self.maxCorpusSize = maxCorpusSize
        self.corpus = []
        self.raw_items_json = []

    # def load_stopwords(self, stopwords=None):
    #     """
    #     加载停用词
    #     :param stopwords:
    #     :return:
    #     """
    #     if stopwords:
    #         with open(stopwords, 'r', encoding='utf-8') as f:
    #             return [line.strip() for line in f]
    #     else:
    #         return []

    def preprocess_data(self, corpus_path):
        """
        文本预处理，每行一个文本
        :param corpus_path:
        :return:
        """
        self.corpus = []
        with open(corpus_path, 'r',encoding='utf-8') as f:
            self.raw_items_json = json.load(f)
            self.json_uid_list = self.raw_items_json[0]
        num = 0
        for item_uid in self.json_uid_list:
            item = self.raw_items_json[1][item_uid]
            if num >= self.maxCorpusSize:
                break
            num += 1
            tmp = ' '.join([word for word in jieba.lcut(item['title'].strip()) if word.isalnum()])
            tmp = tmp + ' ' + ' '.join([word for word in jieba.lcut(item['abstract'].strip()) if word.isalnum()])
            tmp = tmp + ' '
            for keyword in item['keywords']:
                tmp += keyword
            self.corpus.append(tmp)
        # self.raw_items_json = None
        # self.json_uid_list = None

    def get_text_tfidf_matrix(self):
        """
        获取tfidf矩阵
        :param corpus:
        :return:
        """
        tfidf = self.transformer.fit_transform(self.vectorizer.fit_transform(self.corpus))

        # 获取词袋中所有词语
        # words = self.vectorizer.get_feature_names()

        # 获取tfidf矩阵中权重
        weights = tfidf.toarray()
        return weights

    def k_means(self, corpus_path, n_clusters=2):
        """
        KMeans文本聚类
        :param corpus_path: 语料路径（每行一篇）,文章id从0开始
        :param n_clusters: ：聚类类别数目
        :return: {cluster_id1:[text_id1, text_id2]}
        """
        self.preprocess_data(corpus_path)
        weights = self.get_text_tfidf_matrix()

        clf = KMeans(n_clusters=n_clusters, max_iter=1000, algorithm='elkan')

        clf.fit(weights)

        y = clf.fit_predict(weights)

        # 中心点
        centers = clf.cluster_centers_

        # 用来评估簇的个数是否合适,距离约小说明簇分得越好,选取临界点的簇的个数
        score = clf.inertia_

        # 每个样本所属的簇
        result = {}
        for text_idx, label_idx in enumerate(y):
            if label_idx not in result:
                result[label_idx] = [text_idx]
            else:
                result[label_idx].append(text_idx)
        return result


if __name__ == '__main__':
    # K_means = K_meansClustering(1000, stopwords_path='../data/stop_words.txt')
    K_means = K_meansClustering(10000)
    result = K_means.k_means(r"D:\vscode_workspace\ZhongYiPapers\database\MetaData.json", n_clusters=2)
    display_num = 50
    for i in range(display_num):
        print(K_means.raw_items_json[1][K_means.raw_items_json[0][result[1][i]]]['title'])
    print("")
    print("")
    print("")
    for i in range(display_num):
        print(K_means.raw_items_json[1][K_means.raw_items_json[0][result[1][i]]]['title'])
