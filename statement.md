# Problem Statement

## Title
Wikipedia Search Engine (Desktop GUI)

## Objective
Build a desktop application that allows a user to search Wikipedia for
any topic and view the results — including a text summary and a
thumbnail image — without leaving the app, while still providing a
one-click way to open the full article in a browser.

## Problem

Searching Wikipedia normally requires a web browser, and jumping
between a browser and other work can be a distraction. A lightweight,
always-available desktop tool that surfaces just the summary and a
representative image lets a user quickly check a fact or get an
overview of a topic without a full browsing session.

## Requirements

1. **Search** — The user can type a topic into a text field and submit
   it (via button or Enter key).
2. **Summary Display** — The app fetches and displays a multi-sentence
   summary of the most relevant Wikipedia article.
3. **Image Display** — The app fetches and displays the article's
   thumbnail image, if one exists.
4. **Disambiguation Handling** — If the search term is ambiguous
   (matches multiple articles), the app lists the possible options
   instead of failing.
5. **Error Handling** — Network failures, missing pages, or empty
   queries should show a clear message rather than crashing the app.
6. **Open in Browser** — The user can open the full Wikipedia article
   for the current result in their default web browser.
7. **Clear/Reset** — The user can clear the search field, results, and
   image with one click.
8. **Responsiveness** — The UI must remain responsive (not freeze)
   while a search is in progress, since network calls can be slow.

## Non-Goals

- No user accounts, history, or persistent storage of past searches.
- No support for languages other than English (can be extended later
  via `wikipedia.set_lang`).
- No offline mode / caching of previous results.

## Success Criteria

- Typing a well-known topic (e.g. "Albert Einstein") and pressing
  Enter returns a readable summary and an image within a few seconds.
- Typing an ambiguous term (e.g. "Mercury") shows a list of possible
  matches rather than an error or a random guess.
- Typing a nonsense term shows a friendly "No results found" message.
- The window never freezes/becomes unresponsive during a search.
