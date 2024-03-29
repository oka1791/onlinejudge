from django.shortcuts import render, get_object_or_404
from .models import Problem, Submission
from .form import SubmissionForm
from django.utils import timezone
from django.shortcuts import redirect
import requests
import json
import time
import sys

def problem_list(request):
    problems = Problem.objects.all()
    return render(request, 'onlinejudge/problem_list.html', {'problems':problems})

def problem_detail(request, pk):
    if request.method =="POST":
        form = SubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.submitteddate = timezone.now()
            ml = Problem.objects.get(pk=pk)
            submission.title = ml.title
            submission.result = 'wj'
            caseslist = ml.gettestcase()
            flagac = True
            for i in range(5):
                url1 = 'http://api.paiza.io/runners/create'
                query = {
                    'source_code': submission.code,
                    'language': submission.language,
                    'input': caseslist[i][0],
                    'api_key': 'guest', 
                    'longpoll': True,
                }
                response1 = requests.post(url1, json=query)
                id = response1.json()['id']
                params = {
                    'id': id,
                    'api_key': 'guest',
                }
                url2 = 'http://api.paiza.io/runners/get_details'
                response2 = requests.get(url2,json=params)
                result =response2.json()
                if( result['build_result'] == 'failure'):
                    submission.result = 'CE'
                    flagac = False
                    break
                elif(result['build_result'] == 'timeout'):
                    submission.result = 'CE'
                    flagac = False
                    break
                elif(result['result'] == 'failure'):
                    submission.result = 'RE'
                    flagac = False
                    break
                elif(result['result'] == 'timeout'):
                    submission.result = 'TLE'
                    flagac = False
                    break              
                elif(result['stdout'] != caseslist[i][1]+'\n'):
                    submission.result = 'WA'
                    flagac = False
                    break
            if(flagac == True):
                submission.result = 'AC'
            #print(submission.result)
            submission.save()
            return redirect ('submission_list')
    else:
        problem = get_object_or_404(Problem, pk=pk)
        form = SubmissionForm()
    return render(request, 'onlinejudge/problem_detail.html', {'problem': problem, 'form' : form})

def submission_list(request):
    submissions = Submission.objects.order_by('-submitteddate')
    return render(request,'onlinejudge/submission_list.html', {'submissions':submissions})