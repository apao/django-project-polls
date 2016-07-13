from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello World! You're at the Polls index.")


def detail(request, question_id):
    return HttpResponse("You're looking at question {}.".format(question_id))


def results(request, question_id):
    response = "You're looking at the results of question {}.".format(question_id)

    return HttpResponse(response)


def vote(request, question_id):
    return HttpResponse("You're voting on question {}.".format(question_id))
