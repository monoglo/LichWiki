from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from .models import Article, ArticleHistory
from .serializers import ArticleSerializer, ArticleHistorySerializer


class ArticleList(generics.ListCreateAPIView):
    """
            List all articles, or create a new article.
            列出所有词条，或者创建一个新词条。
    """
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.filter(
            a_subject__s_name=self.kwargs['subject_name'],
        )


class ArticleDetail(APIView):
    """
        Get one article, or update or delete a existed article.
        获取、更新或删除一个现有的词条。
    """

    def get_object(self, subject_name, article_title):
        try:
            return Article.objects.get(a_subject__s_name=subject_name, a_title=article_title)
        except Article.DoesNotExist:
            raise Http404

    def get(self, request, subject_name, article_title):
        print(request.user)
        article = self.get_object(subject_name, article_title)
        serializer = ArticleSerializer(article, context={'request': request})
        return Response(serializer.data)

    def put(self, request, subject_name, article_title):
        article = self.get_object(subject_name, article_title)
        article_serializer = ArticleSerializer(article, data=request.data, context={'request': request})
        if article_serializer.is_valid():
            article_history_data = {
                'article_id': request.data.get('a_id'),
                'article_name': request.data.get('a_title'),
                'article_subject_name': request.data.get('subject_name'),
                'author_id': request.data.get('author_id'),
                'author_name': request.data.get('author_name'),
                'ah_summary': request.data.get('ah_summary'),
                'ah_title': request.data.get('a_title'),
                'ah_text': request.data.get('a_text'),
            }
            article_history_serializer = ArticleHistorySerializer(data=article_history_data)
            if article_history_serializer.is_valid():
                article_serializer.save()
                article_history_serializer.save()
                data = article_history_serializer.data
                data.pop('ah_text')
                return Response(data)
            else:
                return Response(article_history_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(article_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleHistoryList(APIView):
    """
        List a specific article's history.
        列出某一词条的所有历史。
    """

    def get_objects(self, subject_name, article_title):
        try:
            return ArticleHistory.objects.filter(
                ah_article__a_subject__s_name=subject_name,
                ah_article__a_title=article_title
            )
        except ArticleHistory.DoesNotExist:
            raise Http404

    def get(self, request, subject_name, article_title):
        article_history_queryset = self.get_objects(subject_name, article_title)
        serializer = ArticleHistorySerializer(article_history_queryset, context={'request': request}, many=True)
        data = serializer.data
        for item in data:
            item.pop('ah_text')
        return Response(data)


class ArticleHistoryListByEditor(APIView):
    """
        List a specific article's history.
        列出某一词条的所有历史。
    """

    def get_objects(self, ah_author_id):
        try:
            return ArticleHistory.objects.filter(
                ah_author_id=ah_author_id
            )
        except ArticleHistory.DoesNotExist:
            raise Http404

    def get(self, request, ah_author_id):
        article_history_queryset = self.get_objects(ah_author_id)
        serializer = ArticleHistorySerializer(article_history_queryset, context={'request': request}, many=True)
        data = serializer.data
        for item in data:
            item.pop('ah_text')
        return Response(data)


class ArticleHistoryDetail(APIView):
    """
        Get one article's history.
        根据词条记录ID获取一个词条的记录。
    """

    def get_object(self, ah_id):
        try:
            return ArticleHistory.objects.get(ah_id=ah_id)
        except ArticleHistory.DoesNotExist:
            raise Http404

    def get(self, request, subject_name, article_title, ah_id):
        article_history = self.get_object(ah_id=ah_id)
        serializer = ArticleHistorySerializer(article_history, context={'request': request})
        return Response(serializer.data)


class GetLatestUpdateInfo(APIView):
    def get(self, request, subject_name, article_title):
        article_history = ArticleHistory.objects.filter(ah_article__a_subject__s_name=subject_name,
                                                        ah_article__a_title=article_title).last()
        serializer = ArticleHistorySerializer(article_history, context={'request': request})
        data = serializer.data
        data.pop('ah_text')
        return Response(data)


class RollbackArticleHistory(APIView):
    def post(self, request):
        article_history = ArticleHistory.objects.get(ah_id=request.data['ah_id'])
        if article_history:
            article = Article.objects.get(a_id=article_history.ah_article_id)

            article.a_text = article_history.ah_text
            article.a_length = article_history.ah_length
            article.save()
            new_article_history = ArticleHistory.objects.create(ah_summary='回滚页面到(' + article_history.ah_summary + ')',
                                                                ah_title=article_history.ah_title,
                                                                ah_text=article_history.ah_text,
                                                                ah_length=article_history.ah_length,
                                                                ah_article_id=article_history.ah_article_id,
                                                                ah_author_id=request.data['u_id'])
            serializer = ArticleHistorySerializer(new_article_history)
            return Response(serializer.data)
        else:
            return Http404
