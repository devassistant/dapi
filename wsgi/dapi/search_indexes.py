import datetime
from haystack import indexes
from dapi import models


class MetaDapIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return models.MetaDap

    def index_queryset(self, using=None):
        '''Used when the entire index for model is updated.'''
        return self.get_model().objects.filter(active=True)
