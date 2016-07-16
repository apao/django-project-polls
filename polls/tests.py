import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Question


def create_question(question_text, days):
    """Create a question with the given 'question_text' and published the given number of 'days' offset to now (negative for questions published in the past, positive for questions that have yet to be published)."""

    time = timezone.now() + datetime.timedelta(days=days)

    return Question.objects.create(question_text=question_text, pub_date=time)


def create_question_with_choices(question_text, days, choice_text_as_list):
    """Create a question with the given 'question_text' and choices as shown in 'choice_text_as_list' and published the given number of 'days' offset to now (negative for questions published in the past, positive for questions that have yet to be published)."""

    time = timezone.now() + datetime.timedelta(days=days)
    current_question = Question.objects.create(question_text=question_text, pub_date=time)
    for choice_text in choice_text_as_list:
        current_question.choice_set.create(choice_text=choice_text, votes=0)

    return current_question


class QuestionViewTests(TestCase):

    def text_index_view_with_no_questions(self):
        """If no questions exist, an appropriate message should be displayed."""

        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """Questions with no choices with a pub date in the past should not be displayed."""

        # Create one question published in the past
        create_question(question_text="Test past question?", days=-10)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question_with_choices(self):
        """Questions with choices with a pub date in the past should be displayed, up to the five most recent questions."""

        # Create one question with choices published in the past
        create_question_with_choices(question_text="Test past question?", days=-10, choice_text_as_list=['Choice A', 'Choice B', 'Choice C'])
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Test past question?>'])

    def test_index_view_with_a_future_question(self):
        """Questions with a pub date in the future should not be displayed."""

        # Create one question to be published in the future
        create_question(question_text="Test future question?", days=25)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_future_question_with_choices(self):
        """Questions with choices with a pub date in the future should not be displayed."""

        # Create one question to be published in the future
        create_question_with_choices(question_text="Test future question?", days=25, choice_text_as_list=['Choice A', 'Choice B', 'Choice C'])
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_both_future_and_past_questions_with_choices(self):
        """Questions with choices with a pub date in the past should be displayed but the question with choices with pub date in the future should not be displayed."""

        # Create one question with choices published in the past
        create_question_with_choices(question_text="Test past question?", days=-29, choice_text_as_list=['Choice A', 'Choice B', 'Choice C'])
        # Create one question with choices to be published in the future
        create_question_with_choices(question_text="Test future question?", days=29, choice_text_as_list=['Choice A', 'Choice B', 'Choice C'])
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Test past question?>'])

    def test_index_view_with_both_future_and_past_questions(self):
        """Questions with a pub date in the past should be displayed but the question with pub date in the future should not be displayed."""

        # Create one question published in the past
        create_question(question_text="Test past question?", days=-29)
        # Create one question to be published in the future
        create_question(question_text="Test future question?", days=29)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_two_past_questions_with_choices(self):
        """Index page may display multiple questions with choices."""

        # Create two questions with choices published in the past
        create_question_with_choices(question_text="Test first past question?", days=-29, choice_text_as_list=['Choice A', 'Choice B', 'Choice C'])
        create_question_with_choices(question_text="Test second past question?", days=-5, choice_text_as_list=['Choice A', 'Choice B', 'Choice C'])
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Test second past question?>', '<Question: Test first past question?>'])

    def test_index_view_with_two_past_questions(self):
        """Index page does not display multiple questions without choices."""

        # Create two questions published in the past
        create_question(question_text="Test first past question?", days=-29)
        create_question(question_text="Test second past question?", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])


class QuestionIndexDetailTests(TestCase):

    def test_detail_view_with_a_future_question(self):
        """Detail view of a question with a future pub_date should return a 404 not found."""

        # Create one question to be published in the future
        future_question = create_question(question_text="Test future question?", days=29)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """Detail view of a question with a past pub_date should display the question's text."""

        # Create a question published in the past
        past_question = create_question(question_text="Test first past question?", days=-29)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_future_question_with_choices(self):
        """Detail view of a question with choices with a future pub_date should return a 404 not found."""

        # Create one question with choices to be published in the future
        future_question = create_question_with_choices(question_text="Test future question?", days=29, choice_text_as_list=['Choice A', 'Choice B', 'Choice C'])
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question_with_choices(self):
        """Detail view of a question with choices with a past pub_date should display the question's text."""

        # Create a question with choices published in the past
        past_question = create_question_with_choices(question_text="Test first past question?", days=-29, choice_text_as_list=['Choice A', 'Choice B', 'Choice C'])
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionResultsTests(TestCase):

    def test_results_view_with_a_future_question(self):
        """Results view of a question with a future pub_date should return a 404 not found."""

        # Create one question to be published in the future
        future_question = create_question(question_text="Test future question?", days=29)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_past_question(self):
        """Results view of a question with a past pub_date should display the question's results."""

        # Create a question published in the past
        past_question = create_question(question_text="Test first past question?", days=-29)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_future_question_with_choices(self):
        """Results view of a question with choices with a future pub_date should return a 404 not found."""

        # Create one question with choices to be published in the future
        future_question = create_question_with_choices(question_text="Test future question?", days=29, choice_text_as_list=['Choice A', 'Choice B', 'Choice C'])
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_past_question_with_choices(self):
        """Results view of a question with choices with a past pub_date should display the question's results."""

        # Create a question with choices published in the past
        past_question = create_question_with_choices(question_text="Test first past question?", days=-29, choice_text_as_list=['Choice A', 'Choice B', 'Choice C'])
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for choice in past_question.choice_set.all():
            self.assertContains(response, choice.choice_text)


class QuestionMethodTests(TestCase):

    def test_was_published_recently_with_future_date(self):
        """was_published_recently() should return False for questions whose pub_date is in the future."""

        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)

        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_date(self):
        """was_published_recently() should return True for questions whose pub_date is within the last day."""

        time = timezone.now() - datetime.timedelta(hours=13)
        recent_question = Question(pub_date=time)

        self.assertEqual(recent_question.was_published_recently(), True)

    def test_was_published_recently_with_old_date(self):
        """was_published_recently() should return False for questions whose pub_date is in the past and not within the last day."""

        time = timezone.now() - datetime.timedelta(days=2)
        old_question = Question(pub_date=time)

        self.assertEqual(old_question.was_published_recently(), False)

    def test_has_choice_set_with_no_choices(self):
        """has_choice_set() should return False for questions with no choices."""

        past_question = create_question(question_text="Test first past question?", days=-29)
        self.assertEqual(past_question.has_choice_set(), False)

    def test_has_choice_set_with_choices(self):
        """has_choice_set() should return True for questions with choices."""

        past_question = create_question_with_choices(question_text="Test first past question?", days=-29, choice_text_as_list=['Choice A', 'Choice B', 'Choice C'])
        self.assertEqual(past_question.has_choice_set(), True)
