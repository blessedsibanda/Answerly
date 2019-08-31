from datetime import date    
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from elasticsearch import Elasticsearch

from qanda.factories import QuestionFactory
from qanda.models import Question
from qanda.views import DailyQuestionList

QUESTION_CREATED_STRFTIME = '%Y-%m-%d %H:%M'


class QuestionSaveTestCase(TestCase):
    """
    Tests Question.save()
    """
    @patch('qanda.service.elasticsearch.Elasticsearch')
    def test_elasticsearch_upsert_on_save(self, ElasticsearchMock):
        user = get_user_model().objects.create(
            username='unittest',
            password='unittest',
        )
        question_title = 'Unit test'
        question_body = 'some long text'
        q = Question(
            title=question_title,
            question=question_body,
            user=user
        )
        q.save()

        self.assertIsNotNone(q.id)
        self.assertTrue(ElasticsearchMock.called)
        mock_client = ElasticsearchMock.return_value
        mock_client.update.assert_called_once_with(
            settings.ES_INDEX,
            'doc',
            id=q.id,
            body={
                'doc': {
                        'text': '{}\n{}'.format(question_title, question_body),
                        'question_body': question_body,
                        'title': question_title,
                        'id': q.id,
                        'created': q.created,
                },
                'doc_as_upsert': True,
            }
        )


class DailyQuestionListTestCase(TestCase):
    """
    Tests the DailyQuestionList view
    """
    QUESTION_LIST_NEEDLE_TEMPLATE = '''
    <li>
        <a href="/q/{id}" >{title}</a>
        by {username} on {date}
    </li>
    '''
    REQUEST = RequestFactory().get(path='/q/2030-12-31')
    TODAY = date.today()

    def test_GET_on_day_with_many_questions(self):
        todays_questions = [QuestionFactory() for _ in range(10)]

        response = DailyQuestionList.as_view()(
            self.REQUEST,
            year=self.TODAY.year,
            month=self.TODAY.month,
            day=self.TODAY.day  
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(10, response.context_data['object_list'].count())
        rendered_content = response.rendered_content
        print(rendered_content)
        for question in todays_questions:
            needle = self.QUESTION_LIST_NEEDLE_TEMPLATE.format(
                id=question.id,
                title=question.title,
                username=question.user.username,
                date=question.created.strftime(QUESTION_CREATED_STRFTIME)
            )
            self.assertInHTML(needle, rendered_content)














