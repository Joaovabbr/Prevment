import sqlite3
from pathlib import Path

# Caminhos dos bancos
facebook_db = Path("facebook/facebook_posts.db")
bing_db = Path("bing_google/dados_bing_google.db")
x_db = Path("X/x_posts.db")

# Caminho da base unificada
union_db_path = Path("geral/dbs_union.db")
conn_union = sqlite3.connect(union_db_path)
cursor_union = conn_union.cursor()

# Cria a tabela unificada
cursor_union.execute("""
CREATE TABLE IF NOT EXISTS posts_unificados (
    id TEXT PRIMARY KEY,
    entity TEXT,
    user TEXT,
    text TEXT,
    title TEXT,
    url TEXT,
    owner TEXT,
    likes INTEGER,
    shares INTEGER,
    coments INTEGER,
    views INTEGER,
    date TEXT,
    origem TEXT
)
""")

# Definição das origens com queries adaptadas
origens = [
    {
        "nome": "facebook",
        "caminho": facebook_db,
        "query": """
            SELECT id, entity, user, text, NULL as title, NULL as url, NULL as owner,
                   likes, shares, coments, NULL as views, NULL as date, 'facebook' as origem
            FROM posts
        """
    },
    {
        "nome": "x",
        "caminho": x_db,
        "query": """
            SELECT id, entity, user, text, NULL as title, NULL as url, NULL as owner,
                   likes, shares, coments, views, NULL as date, 'x' as origem
            FROM posts
        """
    },
    {
        "nome": "bing_google",
        "caminho": bing_db,
        "query": """
            SELECT id, entity, NULL as user, NULL as text, title, url, owner,
                   NULL as likes, NULL as shares, NULL as coments, NULL as views, date, 'bing_google' as origem
            FROM noticias
        """
    }
]

# Inserção dos dados unificados
for origem in origens:
    print(f"Unindo dados de: {origem['nome']}")
    conn_orig = sqlite3.connect(origem["caminho"])
    cursor_orig = conn_orig.cursor()

    try:
        rows = cursor_orig.execute(origem["query"]).fetchall()
        cursor_union.executemany("""
            INSERT OR IGNORE INTO posts_unificados (
                id, entity, user, text, title, url, owner,
                likes, shares, coments, views, date, origem
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
    except Exception as e:
        print(f"Erro em {origem['nome']}: {e}")
    finally:
        conn_orig.close()

conn_union.commit()
conn_union.close()
print("União concluída e salva em 'geral/dbs_union.db'")
