from django.contrib.auth.models import User, Group
from .models import Subject
from rest_framework import serializers


class SubjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Subject
        fields = ['url', 's_name']
