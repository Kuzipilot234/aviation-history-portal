import random

from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_POST

from core.services.content import HISTORICAL_FIGURES, WW2_TIMELINE

FIRST_YEAR = next(iter(WW2_TIMELINE))
FIGURE_NAMES = [figure["answer"] for figure in HISTORICAL_FIGURES]


def _current_figure(request):
    """The visitor's hidden figure. Only its index is kept in the session."""
    index = request.session.get("figure_index")
    if index is None or not 0 <= index < len(HISTORICAL_FIGURES):
        index = random.randrange(len(HISTORICAL_FIGURES))
        request.session["figure_index"] = index
    return HISTORICAL_FIGURES[index]


def _timeline_context(year):
    title, text = WW2_TIMELINE[year]
    return {"years": list(WW2_TIMELINE), "year": year, "title": title, "text": text}


def history(request):
    context = _timeline_context(FIRST_YEAR)
    context.update(clues=_current_figure(request)["clues"], names=FIGURE_NAMES)
    return render(request, "games/history.html", context)


def timeline(request, year):
    if year not in WW2_TIMELINE:
        raise Http404("Unknown year")
    return render(request, "games/_timeline.html", _timeline_context(year))


@require_POST
def guess(request):
    choice = request.POST.get("guess", "")
    answer = _current_figure(request)["answer"]
    return render(
        request,
        "games/_guess_result.html",
        {"choice": choice, "answer": answer, "correct": choice == answer},
    )


@require_POST
def next_figure(request):
    previous = request.session.get("figure_index")
    choices = [i for i in range(len(HISTORICAL_FIGURES)) if i != previous]
    request.session["figure_index"] = random.choice(choices)
    return render(
        request,
        "games/_who_am_i.html",
        {"clues": _current_figure(request)["clues"], "names": FIGURE_NAMES},
    )
