# -*- coding: utf-8 -*-

from hashlib import md5
import colletions
import jieba
from jieba import analyse


def _default_hashfunc(content):
    """
    Default hash function which by MD5 algorithms then return a decimal number
    :param data: data that needs to hash
    :return: return a decimal number that after MD5 algorithms encode
    """
    return int(md5(content).hexdigest(), 16)


def _default_tokenizer_func(content, keyword_weight_pair):
    """
    Default tokenizer function that uses jieba tokenizer.
    :param feature_weight_pair: maximum pair of the keyword-weight list
    :return: return keyword-weight list. Example: [('Example',0.4511233019962264),('Hello',0.25548051420382073),...]
    """
    seg_list = jieba.lcut_for_search(content)
    # Extract keyword-weight list by TF-IDF algorithms and by sorted maximum weight
    jieba.analyse.set_stop_words("stop_words.txt")
    return jieba.analyse.extract_tags("".join(seg_list), topK=keyword_weight_pair, withWeight=True)


class Simhash(object):
    """
        Class Simhash implements simhash algorithms of the Google for filter duplicate content.
        Simhash algorithms idea is will reduce the dimension of content and compares the
        difference of the "Hamming Distance" implements filter duplicate content.
        About simhash algorithms the more introduction: https://en.wikipedia.org/wiki/SimHash
        Simhash default tokenizer is jieba (https://github.com/fxsjy/jieba).
    """

    def __init__(self, content, keyword_weight_pair=20, hash_bit_number=64, hashfunc=None, tokenizer_func=None):
        if hashfunc is None:
            self.hashfunc = _default_hashfunc
        else:
            self.hashfunc = hashfunc

        if tokenizer_func is None:
            self.tokenizer_func = _default_tokenizer_func
        else:
            self.tokenizer_func = tokenizer_func
        self.hash_bit_number = hash_bit_number
        self.simhash = self._simhash(content, keyword_weight_pair)
        if isinstance(data, Simhash):
            self.content = data.content
        else:
            self._simhash(data)

    def __str__(self):
        return str(self.simhash)

    def _simhash(self, content, keyword_weight_pair):
        if content is None or content == "":
            self.content = None
            return
        
        if isinstance(content, collections.Iterable):
            self.content = self.build_by_features(content)
        elif isinstance(content, str):
            features = self.tokenizer_func(content, self.keyword_weight_pari)
            self.content = self.build_by_features(features)
        elif isinstance(content, int):
            self.content = content
        else:
            raise Exception("Unsupported parameter type %s" % type(content))

    def build_by_features(self, features):
        """
        :param features: a list of (token,weight) tuples or a token -> weight dict,
                        if is a string so it need compute weight (a weight of 1 will be assumed).

        :return:
        """
        v = [0] * self.hash_bit_number
        masks = [1 << i for i in range(self.hash_bit_number)]
        if isinstance(features, dict):
            features = features.items()

        # Starting longitudinal accumulation of bits, current bit add current weight
        # when the position that & result of the hashcode and mask are 1
        # else current bit minus the current weight.
        for f in features:
            if isinstance(f, str):
                h = self.hashfunc(f.encode("utf-8"))
                w = 1
            else:
                assert isinstance(f, collections.Iterable)
                h = self.hashfunc(f[0].encode("utf-8"))
                w = f[1]
            for i in range(self.hash_bit_number):
                v[i] += w if h & masks[i] else -w

        result = 0
        for i in range(self.hash_bit_number):
            if v[i] > 0:
                result |= masks[i]
