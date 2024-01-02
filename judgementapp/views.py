# Create your views here.
from io import StringIO
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import Context, loader, RequestContext
# from django.core.servers.basehttp import FileWrapper
from django.shortcuts import render, get_object_or_404
from wsgiref.util import FileWrapper

from judgementapp.models import *

def index(request):
    queries = Query.objects.order_by('qId')
    output = ', '.join([q.text for q in queries])

    # template = loader.get_template('judgementapp/index.html')
    context = {'queries': queries}
    # return HttpResponse(template.render(request, context))
    return render(request, 'judgementapp/index.html', context)

def qrels(request):
    judgements = Judgement.objects.exclude(relevance=-1)

    response = HttpResponse(judgements, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=qrels.txt'
    #response['X-Sendfile'] = myfile
    # It's usually a good idea to set the 'Content-Length' header too.
    # You can also set any other required headers: Cache-Control, etc.
    return response

def query_list(request):
    queries = Query.objects.order_by('qId')

    # return render('judgementapp/query_list.html', { 'queries': queries}, context_instance=RequestContext(request))
    return render(request, 'judgementapp/query_list.html', {'queries': queries})

def query(request, qId):
    query = Query.objects.get(qId=qId)
    judgements = Judgement.objects.filter(query=query.id)

    if "difficulty" in request.POST:
        query.difficulty = int(request.POST['difficulty'])
        if "comment" in request.POST:
            query.comment = request.POST['comment']
        query.save()

    query.length = len(query.text)

    # return render('judgementapp/query.html', {'query': query, 'judgements': judgements}, context_instance=RequestContext(request))
    return render(request, 'judgementapp/query.html', {'query': query, 'judgements': judgements})


def document(request, qId, docId):
    document = Document.objects.get(docId=docId)
    query = Query.objects.get(qId=qId)

    judgements = Judgement.objects.filter(query=query.id)
    judgement = Judgement.objects.filter(query=query.id, document=document.id)[0]
    rank = -1
    for (count, j) in enumerate(judgements):
        if j.id == judgement.id:
            rank = count+1
            break


    prev = None
    try:
        prev = Judgement.objects.filter(query=query.id).get(id=judgement.id-1)
    except:
        pass

    next = None
    try:
        next = Judgement.objects.filter(query=query.id).get(id=judgement.id+1)
    except:
        pass

    content = document.get_content()

    return render(request, 'judgementapp/document.html', 
            {'document': document, 'query': query, 
                'judgement': judgement, 'next': next, 'prev': prev, 
                'rank': rank, 'total_rank': judgements.count(), 
                'content': content.strip()
            })

def judge(request, qId, docId):
    query = get_object_or_404(Query, qId=qId)
    document = get_object_or_404(Document, docId=docId)
    relevance = request.POST['relevance']
    comment = request.POST['comment']

    judgements = Judgement.objects.filter(query=query.id)
    judgement, created = Judgement.objects.get_or_create(query=query.id, document=document.id)
    judgement.relevance = int(relevance)
    if comment != 'Comment':
        judgement.comment = comment
    judgement.save()


    next = None
    try:
        next = Judgement.objects.filter(query=query.id).get(id=judgement.id+1)
        if 'next' in request.POST:
            document = next.document
            judgement = next
            next = Judgement.objects.filter(query=query.id).get(id=judgement.id+1)
    except:
        pass

    prev = None
    try:
        prev = Judgement.objects.filter(query=query.id).get(id=judgement.id-1)
    except:
        pass

    rank = -1
    for (count, j) in enumerate(judgements):
        if j.id == judgement.id:
            rank = count+1
            break


    content = document.get_content()

    # return render(request, 'judgementapp/upload.html', context)
    return render(request, 'judgementapp/document.html', 
            {'document': document, 'query': query, 
                'judgement': judgement, 'next': next, 'prev': prev, 
                'rank': rank, 'total_rank': judgements.count(), 
                'content': content.strip()
            }) 


def upload(request):
    context = {}
    if 'queryFile' in request.FILES:
        f = request.FILES['queryFile']

        qryCount = 0
        for query in f:
            qid, txt = query.decode().strip().split("\t", 1)
            qryCount = qryCount + 1
            query = Query(qId=qid,text=txt)
            query.save()
        context['queries'] = qryCount

    if 'resultsFile' in request.FILES:
        f = request.FILES['resultsFile']

        docCount = 0
        for result in f:
            qid, z, doc, rank, score, desc = result.decode().strip().split()
            docCount = docCount + 1
            doc = doc.replace('corpus/', '')
            
            document, created = Document.objects.get_or_create(docId=doc)
            document.text = "TBA"

            query = Query.objects.get(qId=qid)
            document.save()

            judgement = Judgement()
            judgement.query = query
            judgement.document = document
            judgement.relevance = -1
            
            judgement.save()
                
        context['results'] = docCount

    return render(request, 'judgementapp/upload.html', context)
