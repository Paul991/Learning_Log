from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import Topic, Entry
from .forms import TopicForm, EntryForm

def index(request):
	"""The home page for Learning Log"""
	return render(request,'learning_logs/index.html')


def topics(request):
	"""Show all topics"""
	if request.user.is_authenticated:
		topics = Topic.objects.filter(owner=request.user, public=False).order_by('date_added')
		public_topics = Topic.objects.filter(public=True)
		context = {'topics': topics, 'public_topics': public_topics}
		return render(request, 'learning_logs/topics.html', context)
	else:
		public_topics = Topic.objects.filter(public=True).order_by('date_added')
		context = {'public_topics': public_topics}
		return render(request, 'learning_logs/topics.html', context)


def topic(request, topic_id):
	"""Show a single topic and all its entries."""
	topic = get_object_or_404(Topic, id=topic_id)
	# If the topic is private make sure the topic belongs to the current user

	if topic.public == False:
	  check_topic_owner(request, topic)

	entries = topic.entry_set.order_by('-date_added')
	context = {'topic': topic, 'entries': entries}
	return render(request,'learning_logs/topic.html', context)

@login_required 
def new_topic(request):
	"""Add a new topic"""
	if request.method != 'POST':
		# No data submitted; create a blank form.
		form = TopicForm
	else:
		# POST data submitted; process data.
		form = TopicForm(data=request.POST)
		if form.is_valid():
			new_topic = form.save(commit=False)
			new_topic.owner = request.user
			if request.POST['public'] == True:
				new_topic.public = True
			new_topic.save()
			return redirect('learning_logs:topics')

	# Display a blank or invalid form.
	context = {'form': form}
	return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
	"""Add a new entry for a particular topic"""
	topic = get_object_or_404(Topic, id=topic_id)
	# If the topic is private make sure the topic belongs to the current user

	if topic.public == False:
	  check_topic_owner(request, topic)
 
	if request.method != 'POST':
		# No data submited; create a blank form.
		form = EntryForm()
	else:
		# POST data submitted; process data.
		form = EntryForm(data=request.POST)
		if form.is_valid():
			new_entry = form.save(commit=False)
			new_entry.topic = topic
			new_entry.save()
			return redirect('learning_logs:topic', topic_id=topic_id)

	# Display a blank valid form
	context = {'topic': topic, 'form': form}
	return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
	"""Edit and existing entry"""
	entry = get_object_or_404(Entry, id=entry_id)
	topic = entry.topic
	check_topic_owner(request, topic)

	if request.method !='POST':
		# Initial request; pre-fill form with the current entry
		form = EntryForm(instance=entry)
	else:
		# POST data submitted; process data
		form = EntryForm(instance=entry, data=request.POST)
		if form.is_valid():
			form.save()
			return redirect('learning_logs:topic', topic_id=topic.id)

	context = {'entry':entry, 'topic':topic, 'form':form}
	return render(request, 'learning_logs/edit_entry.html', context)

def check_topic_owner(request, topic):
	"""Make sure the topic belongs to the current user"""
	if topic.owner != request.user:
		raise Http404
