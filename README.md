# Wikipedia Search Engine

A simple desktop GUI app (built with Tkinter) that searches Wikipedia,
shows the article summary and thumbnail image, and lets you jump
straight to the full article in your browser.

## Features

- Search any topic and view a 10-sentence summary
- Automatically fetches and displays the article's thumbnail image
- Handles disambiguation pages by listing the possible matches
- "Open Wikipedia" button opens the full article in your default browser
- Search runs on a background thread, so the UI never freezes while
  waiting on the network

## Project Structure

```
wiki_search_app/
├── main.py            # Entry point - creates the window and starts the app
├── gui.py              # Tkinter UI: widgets, layout, and event handlers
├── wiki_service.py      # Wikipedia search + image-fetching logic (no UI code)
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── statement.md         # Problem statement / project description
└── diagrams/
    ├── architecture_diagram.png   # Placeholder - module/component overview
    └── flow_diagram.png            # Placeholder - search request flow
```

## Setup

1. Make sure you have Python 3.8+ installed.
2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   > Note: Tkinter ships with most standard Python installs. On some
   > Linux distributions you may need to install it separately, e.g.
   > `sudo apt install python3-tk`.

## Running the App

```bash
python main.py
```

Type a search term into the box and press **Enter** or click **Search**.

## How It Works

1. `gui.py` reads the search box text and starts a background thread so
   the window doesn't freeze while Wikipedia is being queried.
2. `wiki_service.search_wikipedia()` looks up the term, loads the best
   matching page, and pulls a plain-text summary.
3. A separate request to Wikipedia's REST summary API fetches the
   page's thumbnail image, which is resized with Pillow.
4. Results are handed back to `gui.py`, which updates the text box and
   image label on the main thread.
5. If Wikipedia reports multiple possible matches (a disambiguation
   page), the app lists up to 20 options instead of an error.

## Notes / Possible Improvements

- Currently only the *first* search result is used automatically;
  disambiguation options are shown as text but aren't clickable yet.
- No caching - repeated searches for the same term re-fetch everything.
- Error handling is intentionally simple (catches broad `Exception`)
  to keep the UI from crashing on flaky network conditions.
