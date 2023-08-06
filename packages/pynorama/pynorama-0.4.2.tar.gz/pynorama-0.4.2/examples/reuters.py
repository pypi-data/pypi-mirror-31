import pandas as pd
from nltk.corpus import reuters
from nltk import sent_tokenize, word_tokenize

from pynorama import View, make_config
from pynorama.table import PandasTable
from pynorama.logging import logger
from pynorama.exceptions import RecordNotFound


class ReutersView(View):
    def __init__(self):
        super(ReutersView, self).__init__(
            name='reuters', description='nltk\'s reuters corpus')

    def load(self):
        self.df = pd.DataFrame([{
            'doc_id': doc_id,
            'abspath': str(reuters.abspath(doc_id)),
            'categories': ', '.join(reuters.categories(doc_id)),
            'headline': reuters.raw(doc_id).split('\n', 1)[0],
            'length': len(reuters.raw(doc_id))
        } for doc_id in reuters.fileids()])

        nb = pd.read_csv('/Users/slavi/prj/pynorama/examples/nb_svm.csv')
        self.df = pd.merge(self.df, nb, how='outer')

        logger.info('Finishing processing reuters dataset.')

    def get_table(self):
        return PandasTable(self.df)

    def get_pipeline(self):
        return {
            'raw': {'viewer': 'raw'},
            'doctree': {'parents': ['raw'],
                        'viewer': 'doctree'}
        }

    def get_record(self, key, stage):
        rawdoc = reuters.raw(key)
        if stage == 'raw':
            return rawdoc
        if stage == 'doctree':
            return [word_tokenize(sent) for sent in sent_tokenize(rawdoc)]

        raise RecordNotFound(key, stage)

    def get_config(self):
        return make_config('doc_id',
                           available_transforms=['nans', 'search', 'quantile_range'],
                           initial_visible_columns=['doc_id', 'headline', 'categories', 'length'])
