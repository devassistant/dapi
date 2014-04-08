from haystack import forms as haystack_forms

def search_form(request):
    return {'search_form': haystack_forms.SearchForm()}
