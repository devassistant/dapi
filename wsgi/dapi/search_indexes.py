from haystack import indexes
from dapi import models
from dapi.logic import PLATFORMS


class MetaDapIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    package_name = indexes.CharField(model_attr='package_name')
    active = indexes.BooleanField(model_attr='active')
    has_assistants = indexes.BooleanField()
    has_stable = indexes.BooleanField()
    supported_platforms = indexes.MultiValueField()
    average_rank = indexes.FloatField(model_attr='average_rank', default=0.0)
    rank_count = indexes.IntegerField(model_attr='rank_count', default=0)
    # When adding new fields, do not forget to rebuild index by ./manage.py rebuild_index

    def get_model(self):
        return models.MetaDap

    def index_queryset(self, using=None):
        '''Used when the entire index for model is updated.'''
        return self.get_model().objects.all()

    def prepare(self, object):
        self.prepared_data = super(MetaDapIndex, self).prepare(object)

        if object.latest:
            self.prepared_data['has_assistants'] = object.latest.has_assistants

            self.prepared_data['supported_platforms'] = object.latest.get_supported_platforms()
            if not self.prepared_data['supported_platforms']:
                self.prepared_data['supported_platforms'] = PLATFORMS
        else:
            self.prepared_data['has_assistants'] = False
            self.prepared_data['supported_platforms'] = []

        self.prepared_data['has_stable'] = bool(object.latest_stable)

        return self.prepared_data
