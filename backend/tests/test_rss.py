from types import SimpleNamespace

from app.connectors.rss import RSSConnector


def test_discovers_publisher_feed_and_extracts_item_image(monkeypatch):
    class Response(SimpleNamespace):
        def raise_for_status(self):
            pass

    page = Response(
        content=b'<html><head><link rel="alternate" type="application/rss+xml" href="/feed.xml"></head></html>',
        text='<html><head><link rel="alternate" type="application/rss+xml" href="/feed.xml"></head></html>',
        headers={"content-type": "text/html"},
        url="https://publisher.example/news",
    )
    feed = Response(
        content=b"""<?xml version="1.0"?><rss version="2.0"><channel><title>Publisher</title>
        <item><title>New science story</title><link>https://publisher.example/story</link>
        <description><![CDATA[<img src="/images/story.jpg">A short source preview.]]></description>
        <pubDate>Mon, 24 Nov 2025 10:00:00 GMT</pubDate></item></channel></rss>""",
        headers={"content-type": "application/rss+xml"},
        url="https://publisher.example/feed.xml",
    )
    calls = []

    def get(url, **kwargs):
        calls.append(url)
        return page if url == "https://publisher.example/news" else feed

    monkeypatch.setattr("app.connectors.rss.httpx.get", get)
    items = RSSConnector({"category": "science"}, "https://publisher.example/news").fetch()
    assert calls == ["https://publisher.example/news", "https://publisher.example/feed.xml"]
    assert len(items) == 1
    assert items[0].category == "science"
    assert items[0].image_url == "https://publisher.example/images/story.jpg"
