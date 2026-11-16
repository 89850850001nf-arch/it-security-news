from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
import html
from collector import fetch_news

app = Flask(__name__)
DB_NAME = 'news.db'

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 🛡️ Безопасное построение запроса с учетом фильтров
    query = "SELECT title, link, source, date, category FROM news WHERE 1=1"
    params = []
    
    if search_query:
        query += " AND title LIKE ?"
        params.append('%' + search_query + '%')
        
    if category_filter:
        query += " AND category = ?"
        params.append(category_filter)
        
    query += " ORDER BY id DESC LIMIT 30"
    
    c.execute(query, params)
    news = c.fetchall()
    conn.close()

    html_content = """
    <html>
    <head>
        <title>IT Security News</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #121212; color: #e0e0e0; padding: 20px; margin: 0; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #00ffcc; text-align: center; text-shadow: 0 0 10px rgba(0,255,204,0.5); }
            .search-bar { display: flex; justify-content: center; margin-bottom: 20px; gap: 10px; }
            input[type="text"] { padding: 10px; border-radius: 5px; border: 1px solid #444; background: #222; color: white; width: 60%; }
            button { padding: 10px 20px; background: #00ffcc; border: none; border-radius: 5px; color: #121212; font-weight: bold; cursor: pointer; }
            .filters { display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
            .filter-btn { padding: 5px 15px; background: #333; color: white; text-decoration: none; border-radius: 20px; font-size: 14px; }
            .filter-btn:hover, .filter-btn.active { background: #00ffcc; color: #121212; }
            .news-card { background: #1e1e1e; border-radius: 8px; padding: 20px; margin-bottom: 15px; border-left: 4px solid #00ffcc; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: transform 0.2s; }
            .news-card:hover { transform: translateX(5px); background: #252525; }
            .news-card a { color: #4da6ff; text-decoration: none; font-size: 18px; font-weight: bold; }
            .meta { font-size: 12px; color: #888; margin-top: 10px; display: flex; justify-content: space-between; }
            .category-badge { background: #444; padding: 2px 8px; border-radius: 4px; font-size: 10px; text-transform: uppercase; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ IT Security News</h1>
            
            <div class="search-bar">
                <form method="GET" action="/" style="width: 100%; display: flex; justify-content: center; gap: 10px;">
                    <input type="text" name="search" placeholder="Поиск по новостям..." value="{search_query}">
                    <button type="submit">Найти</button>
                </form>
            </div>
            
            <div class="filters">
                <a href="/" class="filter-btn">Все</a>
                <a href="/?category=Безопасность" class="filter-btn">Безопасность</a>
                <a href="/?category=IT Новости" class="filter-btn">IT Новости</a>
                <a href="/?category=Технологии" class="filter-btn">Технологии</a>
                <a href="/update" style="background:#00ffcc; color:#121212; padding:5px 15px; border-radius:20px; text-decoration:none; font-weight:bold;">🔄 Обновить</a>
            </div>
    """.replace("{search_query}", html.escape(search_query))
    
    if not news:
        html_content += "<p style='text-align:center; color: #ff5555;'>Новостей не найдено.</p>"
        
    for item in news:
        safe_title = html.escape(item[0])
        safe_link = html.escape(item[1])
        
        html_content += f"""
        <div class="news-card">
            <a href="{safe_link}" target="_blank">{safe_title}</a>
            <div class="meta">
                <span>Источник: {html.escape(item[2])}</span>
                <span class="category-badge">{html.escape(item[4])}</span>
                <span>{item[3]}</span>
            </div>
        </div>
        """
        
    html_content += "</div></body></html>"
    return html_content

@app.route('/update')
def update_news():
    print("Запуск обновления новостей...")
    fetch_news() 
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
