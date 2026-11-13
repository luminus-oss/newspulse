from flask import Flask, render_template, request
import feedparser
import re

app = Flask(__name__)

FEEDS = {
    "General": [
        ("BBC", "https://feeds.bbci.co.uk/news/rss.xml"),
        ("The Hindu", "https://www.thehindu.com/news/feeder/default.rss"),
        ("Indian Express", "https://indianexpress.com/section/india/feed/")
    ],

    "Technology": [
        ("BBC Technology",
         "https://feeds.bbci.co.uk/news/technology/rss.xml")
    ],

    "World": [
        ("BBC World",
         "https://feeds.bbci.co.uk/news/world/rss.xml")
    ],

    "Business": [
        ("BBC Business",
         "https://feeds.bbci.co.uk/news/business/rss.xml")
    ]
}

SOURCES = [
    "All",
    "BBC",
    "BBC Technology",
    "BBC World",
    "BBC Business",
    "The Hindu",
    "Indian Express"
]

CATEGORIES = [
    "All",
    "General",
    "Technology",
    "World",
    "Business"
]


def extract_image(article):

    if "media_content" in article:
        try:
            return article.media_content[0]["url"]
        except:
            pass

    if "media_thumbnail" in article:
        try:
            return article.media_thumbnail[0]["url"]
        except:
            pass

    summary = article.get("summary", "")

    match = re.search(
        r'<img[^>]+src="([^">]+)"',
        summary
    )

    if match:
        return match.group(1)

    return "https://picsum.photos/500/300"


def get_news(search_query="", category="All"):

    news = []

    if category == "All":

        selected_feeds = []

        for feeds in FEEDS.values():
            selected_feeds.extend(feeds)

    else:

        selected_feeds = FEEDS.get(category, [])

    for source, url in selected_feeds:

        try:

            feed = feedparser.parse(url)

            print(source, len(feed.entries))

            for article in feed.entries:

                title = article.get("title", "")
                summary = article.get("summary", "")

                if search_query:

                    text = (
                        title +
                        " " +
                        summary
                    ).lower()

                    if search_query.lower() not in text:
                        continue

                news.append({
                    "title": title,
                    "link": article.get("link", "#"),
                    "summary": summary,
                    "source": source,
                    "image": extract_image(article)
                })

        except Exception as e:

            print(e)

    return news


@app.route("/")
def home():

    query = request.args.get("search", "")
    category = request.args.get("category", "All")
    source_filter = request.args.get("source", "All")

    news = get_news(query, category)

    if source_filter != "All":

        news = [
            article
            for article in news
            if article["source"] == source_filter
        ]

    return render_template(
        "index.html",
        news=news,
        query=query,
        category=category,
        source_filter=source_filter,
        sources=SOURCES,
        categories=CATEGORIES
    )


if __name__ == "__main__":
    app.run(debug=True)