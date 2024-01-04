import json
from django.conf import settings
from django.db import models

# Create your models here.
class Document(models.Model):
	docId = models.CharField(max_length=100)
	text = models.TextField()

	def __str__(self):
		return self.docId

	def get_content(self):
		content = ""
		try:
			with open(settings.DATA_DIR+"/"+self.docId) as f:
			    read = f.read()
			    try:
			        self.text = json.loads(read)['metadata']
			        content += json.loads(read)['contents']
			    except:
			        content += read
		except Exception:
			content = "Could not read file %s" % settings.DATA_DIR+"/"+self.docId
		return content


def default_query_categories():
    return {str(i): 0 for i in range(10)}

class Query(models.Model):
	# qId = models.IntegerField()
	qId = models.CharField(max_length=100)
	text = models.CharField(max_length=250)
	category = models.JSONField(default=default_query_categories)
	comment = models.TextField(default="", null=True)

	instructions = models.TextField(blank=True, null=True)
	criteria = models.TextField(blank=True, null=True)
	example = models.TextField(blank=True, null=True)

	def __str__(self):
		return '%s: %s' % (self.qId, self.text)

	def num_unjudged_docs(self):
		unjugded = [judgement for judgement in self.judgements() if judgement.relevance < 0]
		return len(unjugded)

	def num_judgements(self):
		return len(self.judgements())

	def judgements(self):
		return Judgement.objects.filter(query=self.id)

class Judgement(models.Model):

	labels = {-1: 'Unjudged', 0: 'Not relvant', 1: 'Somewhat relevant', 2:'Highly relevant'}

	query = models.ForeignKey(Query, on_delete=models.CASCADE)
	document = models.ForeignKey(Document, on_delete=models.CASCADE)
	comment = models.TextField(default="", null=True)
	relevance = models.IntegerField()

	def __str__(self):
		return '%s Q0 %s %s\n' % (self.query.qId, self.document.docId, self.relevance)

	def label(self):
		return self.labels[self.relevance]
