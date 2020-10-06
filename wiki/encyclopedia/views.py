from django.shortcuts import render
from django import forms
import random
from . import util

class SearchForm(forms.Form):
    query = forms.CharField(label="",
        widget=forms.TextInput(attrs={'placeholder': 'Search Wiki', 
            'style': 'width:100%'}))

class CreateForm(forms.Form):
    title = forms.CharField(label="",
        widget=forms.TextInput(attrs={'placeholder': 'Enter Title', 
            'style': 'width:50%'}))
    content = forms.CharField(label="",
        widget=forms.Textarea(attrs={'placeholder': 'Enter Content', 
            'style': 'width:50%'}))

class EditForm(forms.Form):
    edit = forms.CharField(label="",
        widget=forms.Textarea(attrs={'placeholder': 'Edit Content', 
            'style': 'width:50%'}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

def entry(request, title):
    return render(request, "encyclopedia/entry.html", {
        "entry": util.get_entry(title),
        "title": title,
        "form": SearchForm()
    })

def search(request):
    if request.method == "POST":
        matching = []
        form = SearchForm(request.POST)
        articles = util.list_entries()
        if form.is_valid():
            query = form.cleaned_data["query"]
            for entry in articles:
                if query.lower() == entry.lower():
                    title = entry
                    entry = util.get_entry(title)
                    return render(request, "encyclopedia/entry.html", {
                        "entry": util.get_entry(title),
                        "title": title,
                        "form": SearchForm()
                    })
                if query.lower() in entry.lower():
                    matching.append(entry)
            return render(request, "encyclopedia/search.html", {
                "results": matching,
                "query": query,
                "form": SearchForm()
            })
    return render(request, "encyclopedia/search.html", {
        "results": "",
        "query": "",
        "form": SearchForm()
    })

def create(request):
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            articles = util.list_entries()
            for article in articles:
                if article.lower() == title.lower():
                    return render(request, "encyclopedia/create.html", {
                        "form": SearchForm(),
                        "createForm": CreateForm(),
                        "error": "Entry already exists."
                    })
            util.save_entry(title, content)
            entry = util.get_entry(title)
            return render(request, "encyclopedia/entry.html", {
                "entry": util.get_entry(title),
                "title": title,
                "form": SearchForm()
            })
    return render(request, "encyclopedia/create.html", {
        "form": SearchForm(),
        "createForm": CreateForm()
    })

def edit(request, title):
    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["edit"]
            util.save_entry(title, content)
            entry = util.get_entry(title)
            return render(request, "encyclopedia/entry.html", {
                "entry": util.get_entry(title),
                "title": title,
                "form": SearchForm()
            })
    else:
        content = util.get_entry(title)
        initial = {"edit": content}
        editpage = EditForm(initial=initial)
        return render(request, "encyclopedia/edit.html", {
            "form": SearchForm(),
            "editForm": editpage,
            "title": title,
            "content": content
        })

def randomPage(request):
    articles = util.list_entries()
    entry = articles[random.randrange(len(articles))]
    content = util.get_entry(entry)
    return render(request, "encyclopedia/random.html", {
        "title": entry,
        "entry": content,
        "form": SearchForm()
    })