#ウェブ検索(キーワード有りのみ)
"""
与えられたキーワードに対してウェブ検索を行う
"""
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import fitz  # PyMuPDF
import random

class WebSearcher:
    def __init__(self, keyword):
        self.keyword = keyword
        try:
            self.results = self.total_actions()
        except Exception as e:
            print(f"[ERROR] total_actions failed: {e}")
      
    #queryのテンプレートが決まっていればここで作成
    def marge_keyword(self):
        try:
            query = []
            query.append(self.keyword["enterprise"])
            for product in self.keyword["product"]:
                query.append(self.keyword["enterprise"] + "+" + product)
            return query
        except Exception as e:
            print(f"[ERROR] marge_keyword failed: {e}")

    #links(検索結果)から一つずつ本文をとってくる return:list 本文<body>
    def fetch_article_content(self, url):
        try:
            if url.endswith('.pdf'):
                response = requests.get(url)
                pdf_document = fitz.open(stream=response.content, filetype="pdf")
                content = ""
                for page in pdf_document:
                    content += page.get_text()
                pdf_document.close()
            else:
                response = requests.get(url)
                soup = BeautifulSoup(response.content, "html.parser")
                body = soup.body
                tables = ''.join([str(table) for table in body.find_all('table')])
                for table in body.find_all('table'):
                    table.extract()
                
                # headerとfooterを削除
                for header in body.find_all('header'):
                    header.decompose()
                for footer in body.find_all('footer'):
                    footer.decompose()
                text = body.get_text(strip=True, separator="\n")
                content = text + "\n" + tables
            return content
        except Exception as e:
            print(f"[ERROR] fetch_article_content failed for {url}: {e}")

    #DuckDuckGoで検索結果を取得する return:list link
    def duckduckgo_search(self, query):
        query_results = []
        for q in query:
            try:
                url = f"https://duckduckgo.com/html/?q={q.replace(' ', '+')}"
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "html.parser")
                query_result = {"query": q, "results": []}
                for result in soup.select(".result__title")[:2]:
                    link = result.find("a")["href"]
                    parsed = urllib.parse.urlparse("https:" + link)
                    query = urllib.parse.parse_qs(parsed.query)
                    real_url = query["uddg"][0]
                    content = self.fetch_article_content(real_url)
                    query_result["results"].append({
                        "link": real_url,
                        "content": content
                    })
                query_results.append(query_result)
                time.sleep(random.uniform(10, 12))
            except Exception as e:
                print(f"[ERROR] duckduckgo_search failed for query '{q}': {e}")
        return query_results

    #全体実行
    def total_actions(self):
        try:
            query = self.marge_keyword()
            results = self.duckduckgo_search(query)
            return results
        except Exception as e:
            print(f"[ERROR] total_actions failed: {e}")