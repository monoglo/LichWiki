from .models import Article, ArticleHistory
from rest_framework import serializers


class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    subject_id = serializers.IntegerField(source='a_subject.s_id')
    author_id = serializers.IntegerField(source='a_author.u_id')

    class Meta:
        model = Article
        fields = ['a_id', 'subject_id', 'author_id', 'a_title', 'a_text', 'a_create_time']

    def create(self, validated_data):
        return Article.objects.create(
            a_subject_id=validated_data.get('a_subject.s_id'),
            a_author_id=validated_data.get('a_author.u_id'),
            a_title=validated_data.get('a_title'),
            a_text=validated_data.get('a_text')
        )

    def update(self, instance, validated_data):
        print(validated_data)
        instance.subject_id = validated_data.get('a_subject.s_id')
        instance.author_id = validated_data.get('a_author.u_id')
        instance.a_title = validated_data.get('a_title')
        instance.a_text = validated_data.get('a_text')
        instance.save()
        return instance


class ArticleHistorySerializer(serializers.HyperlinkedModelSerializer):
    article_id = serializers.IntegerField(source='ah_article.a_id')
    author_id = serializers.IntegerField(source='ah_author.u_id')

    class Meta:
        model = ArticleHistory
        fields = ['ah_id', 'article_id', 'author_id', 'ah_summary', 'ah_title', 'ah_text', 'ah_edit_time']

    def create(self, validated_data):
        return ArticleHistory.objects.create(
            ah_summary=validated_data['ah_summary'],
            ah_title=validated_data['ah_title'],
            ah_text=validated_data['ah_text'],
            ah_article_id=validated_data['ah_article']['a_id'],
            ah_author_id=validated_data['ah_author']['u_id']
        )
