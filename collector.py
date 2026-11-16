import feedparser
import sqlite3
from datetime import datetime

# 🚀 ТЕПЕРЬ У НАС БОЛЬШЕ ИСТОЧНИКОВ И КАТЕГОРИИ
FEEDS = [
    ("https://feeds.feedburner.com/TheHackersNews", "Безопасность"),
    ("https://www.bleepingcomputer.com/feed/", "Безопасность"),
    ("https://habr.com/ru/rss/news/", "IT Новости"), # Русскоязычный источник
    ("https://www.techrepublic.com/rssfeeds/articles/", "Технологии")
]

def init_db():
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    # 🛡️ Обрати внимание: мы добавили колонку category
    c.execute('''CREATE TABLE IF NOT EXISTS news 
                 (id INTEGER PRIMARY KEY, title TEXT, link TEXT, source TEXT, date TEXT, category TEXT)''')
    conn.commit()
    conn.close()

def fetch_news():
    init_db()
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    
    count = 0
    for feed_url, category in FEEDS:
        print(f"Проверяю: {feed_url} ({category})")
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]: # Берем по 5 новостей с каждого
                title = entry.title
                link = entry.link
                source = feed.feed.title if hasattr(feed.feed, 'title') else "Unknown"
                date = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # Проверка на дубликаты
                c.execute("SELECT id FROM news WHERE link = ?", (link,))
                if c.fetchone() is None:
                    c.execute("INSERT INTO news (title, link, source, date, category) VALUES (?, ?, ?, ?, ?)", 
                              (title, link, source, date, category))
                    count += 1
        except Exception as e:
            print(f"Ошибка при чтении {feed_url}: {e}")
                
    conn.commit()
    conn.close()
    print(f"Добавлено новых новостей: {count}")

if __name__ == "__main__":
    fetch_news()
