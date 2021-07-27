
import random
from markdown import Markdown
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms
from . import util

markdowner = Markdown()


class NewPageForm(forms.Form):
    title = forms.CharField(label="Title ")
    textarea = forms.CharField(widget=forms.Textarea(), label='')

    # Form used to edit a entry/page


class SearchForm(forms.Form):
    search = forms.CharField(label='',
                             widget=forms.TextInput(attrs={'placeholder': 'Search Encyclopedia'}))


class EditForm(forms.Form):
    content = forms.CharField(label='',
                              widget=forms.Textarea(attrs={'placeholder': 'Enter content'}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def get_page(request, title):

    # get page from util.get_entry
    page = util.get_entry(title)
    # if no page found
    if not page:
        return render(request, "encyclopedia/error.html", {"message": "Error 404 : Page Not Found"})

    else:
        # convert the markdown to HTML
        page_converted = markdowner.convert(page)
        return render(request, "encyclopedia/entrypage.html", {
            "title": title,
            "content": page_converted
        })


def search(request):
    if request.method == "POST":
        q = request.POST['q'].upper()
        entries = util.list_entries()
        entries = [k.upper() for k in entries]
        res = list(filter(lambda x: q in x, entries))

        return render(request, "encyclopedia/search.html", {
            'q': q,
            'entries': entries,
            'res': res
        })

    else:
        return render(request, "encyclopedia/search.html", {
        })


def newpage(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["textarea"]
            entries = util.list_entries()
            if title in entries:
                return render(request, "encyclopedia/error.html", {"message": "Page already exist"})
            else:
                util.save_entry(title, content)
                page = util.get_entry(title)
                page_converted = markdowner.convert(page)
                return render(request, "encyclopedia/entrypage.html", {
                    "title": title,
                    "content": page_converted
                })

        else:
            return render(request, "encyclopedia/newpage.html", {
                "form": form
            })
    return render(request, "encyclopedia/newpage.html", {
        "form": NewPageForm()
    })

# Edit wiki entry


def editpage(request, title):
    if request.method == "GET":
        content = util.get_entry(title)
        return render(request, "encyclopedia/editpage.html", {
            "form": SearchForm(),
            "edit_page": EditForm(initial={'content': content})
        })

    else:
        content_form = EditForm(request.POST)
        if content_form.is_valid():
            content = content_form.cleaned_data["content"]
            util.save_entry(title, content)

            return get_page(request, title)


def random_title(request):
    if request.method == 'GET':
        entries = util.list_entries()
        rand = random.choice(entries)
        page = util.get_entry(rand)
        page_converted = markdowner.convert(page)
        context = {
            'content': page_converted,
            'title': rand
        }

        return render(request, "encyclopedia/entrypage.html", context)
