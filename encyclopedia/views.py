from django.shortcuts import render, redirect, reverse, HttpResponseRedirect
from django.http import HttpResponse
from django.contrib import messages
from markdown2 import Markdown
from django import forms
from . import util


markdowner = Markdown()


class NewWikiForm(forms.Form):
    title = forms.CharField(label="title", max_length=50, required=True)
    description = forms.CharField(
        widget=forms.Textarea, label="description", max_length=600, required=True)


def index(request):
    entries = util.list_entries()
    return render(request, "encyclopedia/index.html", {
        "entries": entries})


def enter_page(request, title):
    entries = util.list_entries()
    # check for url regardless of lower or upper case
    already_present = False
    for entry in entries:
        check = util.check_case(title, entry)
        if check:
            already_present = check
            break
    if util.get_entry(already_present):
        return render(request, "encyclopedia/title.html",
                      {"wiki": markdowner.convert(util.get_entry(already_present)), "title": title})
    else:
        return render(request, "404.html", {"error": title})


def search(request):
    if request.method == 'GET' and 'q' in request.GET:
        # get lowercase query and files
        q = request.GET['q'].lower()
        entries = util.list_entries()
        # turn filenames to lowercase in new array to find match
        entries_lowercase = []
        for entry in entries:
            entries_lowercase.append(entry.lower())
        # find index if there is a match and redirect -
        # to site using index for original array
        if q in entries_lowercase:
            ind = entries_lowercase.index(q)
            return redirect(f'wiki/{entries[ind]}')

        # find substring match and add to search results list
        search_results = []
        for i, entry in enumerate(entries_lowercase):
            found = entry.find(q)
            # find returns int >=0 if found, -1 if not, so:
            if found >= 0:
                search_results.append(entries[i])
        if len(search_results) > 0:
            return render(request, "encyclopedia/search.html", {"titles": search_results})

        return render(request, "404.html", {"error": q})
    return render(request, "404.html", {"error": q})


def create_page(request):
    entries = util.list_entries()
    if request.method == "POST":
        form = NewWikiForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["description"]
            # check if exists already using title, regardless of case
            already_present = False
            for entry in entries:
                check = util.check_case(title, entry)
                if check:
                    already_present = check
                    break
            if already_present:
                messages.error(
                    request, f'Error, Entry "{already_present}" already exists!')
            else:
                util.save_entry(title, content)
                util.list_entries()
                return HttpResponseRedirect(f'/wiki/{title}')

    return render(request, "encyclopedia/new.html", {"form": NewWikiForm()})


def edit(request, title):
    entries = util.list_entries()
    wiki = util.get_entry(title)
    if request.method == "POST":
        form = NewWikiForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["description"]
            # check if exists already using title, regardless of case
            already_present = False
            for entry in entries:
                check = util.check_case(title, entry)
                if check:
                    already_present = check
                    break
                # if already present, overwrite the old file with new data
            if already_present:
                util.save_entry(title, content)
                return HttpResponseRedirect(f'/wiki/{already_present}')
            else:
                messages.error(
                    request, f'Error, Entry "{already_present}" does not exist!')
    if util.get_entry(title):
        return render(request, "encyclopedia/edit.html",
                      {"wiki": wiki, "title": title,
                       "form": NewWikiForm(initial={"title": title,
                                                    "description": wiki})})
    else:
        return render(request, "404.html", {"error": title})


def random(request):
    # refresh entries in case more added
    entries = util.list_entries()
    # use utility function to get random index from entries array
    random_wiki = util.random_int(len(entries)-1)
    return HttpResponseRedirect(f'wiki/{entries[random_wiki]}')
