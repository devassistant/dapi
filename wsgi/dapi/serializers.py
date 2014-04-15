from django.contrib.auth.models import User
from dapi.models import MetaDap, Dap
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    fedora_username = serializers.Field(source='profile.fedora_username')
    github_username = serializers.Field(source='profile.github_username')
    full_name = serializers.Field(source='get_full_name')
    url = serializers.HyperlinkedIdentityField(
        view_name='user-detail',
        lookup_field='username')
    metadap_set = serializers.HyperlinkedRelatedField(
        view_name='metadap-detail',
        lookup_field='package_name',
        many=True)
    codap_set = serializers.HyperlinkedRelatedField(
        view_name='metadap-detail',
        lookup_field='package_name',
        many=True)

    class Meta:
        model = User
        fields = (
            'url',
            'id',
            'username',
            'full_name',
            'metadap_set',
            'codap_set',
            'fedora_username',
            'github_username',
        )
        


class MetaDapSerializer(serializers.HyperlinkedModelSerializer):
    reports = serializers.Field(source='get_unsolved_reports_count')
    tags = serializers.Field(source='tags.all')
    similar_daps = serializers.Field(source='similar_active_daps')
    url = serializers.HyperlinkedIdentityField(
        view_name='metadap-detail',
        lookup_field='package_name')
    user = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        lookup_field='username')
    comaintainers = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        lookup_field='username',
        many=True)

    class Meta:
        model = MetaDap
        fields = (
            'url',
            'id',
            'package_name',
            'user',
            'active',
            'rank_count',
            'average_rank',
            'latest',
            'latest_stable',
            'reports',
            'dap_set',
            'comaintainers',
            'tags',
            'similar_daps',
        )


class DapSerializer(serializers.HyperlinkedModelSerializer):
    package_name = serializers.Field(source='metadap.package_name')
    authors = serializers.Field(source='get_authors')
    is_pre = serializers.Field(source='is_pre')
    is_latest = serializers.Field(source='is_latest')
    is_latest_stable = serializers.Field(source='is_latest_stable')
    reports = serializers.Field(source='metadap.get_unsolved_reports_count')
    active = serializers.Field(source='metadap.active')
    download = serializers.Field(source='file.url')
    metadap = serializers.HyperlinkedRelatedField(
        view_name='metadap-detail',
        lookup_field='package_name')

    class Meta:
        model = Dap
        fields = (
            'url',
            'id',
            'metadap',
            'package_name',
            'version',
            'license',
            'summary',
            'description',
            'authors',
            'homepage',
            'bugreports',
            'is_pre',
            'is_latest',
            'is_latest_stable',
            'reports',
            'active',
            'download',
        )
