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
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class WebSearcher:
    def __init__(self, keyword, item_count=10, content_length=None):
        self.keyword = keyword
        self.item_count = item_count
        self.content_length = content_length
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102 Safari/537.36"
        }
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

    #制限のある場合はseleniumで
    def scraping_with_selenium(self, url):
        content = self.scraping_return_content(url)
        soup = BeautifulSoup(content, "html.parser")
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

    def scraping_return_content(self, url):
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            # User-Agentのリスト
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/102.0.1245.33 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"
            ]
            options.add_argument(f"user-agent={random.choice(user_agents)}")

            # WebDriverのインスタンスを作成
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(10)  # ページが完全に読み込まれるまで待機
            content = driver.page_source
            driver.quit()
            return content
        except Exception as e:
            print(f"[ERROR] scraping_return_content failed for {url}: {e}")

    #links(検索結果)から一つずつ本文をとってくる return:list 本文<body>
    def fetch_article_content(self, url):
        try:
            timeout_seconds = 10
            if url.endswith('.pdf'):
                response = requests.get(url, headers=self.headers, timeout=timeout_seconds)
                pdf_document = fitz.open(stream=response.content, filetype="pdf")
                content = ""
                for page in pdf_document:
                    content += page.get_text()
                pdf_document.close()
            else:
                response = requests.get(url, headers=self.headers, timeout=timeout_seconds)
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
            if "Additional Verification Required" in content or "Enable JavaScript" in content:
                content = self.scraping_with_selenium(url)
            return content
        except requests.exceptions.Timeout:
            content = self.scraping_with_selenium(url)
            return content
        except Exception as e:
            print(f"[ERROR] fetch_article_content failed for {url}: {e}")
            return ""

    #DuckDuckGoで検索結果を取得する return:list link
    def duckduckgo_search(self, query):
        query_results = []
        for q in query:
            try:
                url = f"https://duckduckgo.com/html/?q={q.replace(' ', '+')}"
                content = self.scraping_return_content(url)
                soup = BeautifulSoup(content, "html.parser")
                query_result = {"query": q, "results": []}
                for result in soup.select(".result__title")[:self.item_count]:
                    link = result.find("a")["href"]
                    parsed = urllib.parse.urlparse("https:" + link)
                    query = urllib.parse.parse_qs(parsed.query)
                    real_url = query["uddg"][0]
                    content = self.fetch_article_content(real_url)
                    if self.content_length is None:
                        limit_content = content
                    else:
                        limit_content = content[:self.content_length]
                    query_result["results"].append({
                        "link": real_url,
                        "content": limit_content
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


if __name__ == "__main__":
    keyword = {
        "enterprise": "製造業　求人　自動車",
        "product": []
    }
    #件数を指定(１０件以内)
    item_count = 2
    #内容の文字数指定
    # content_length = 500
    searcher = WebSearcher(keyword, item_count)
    print(searcher.results)

# #ウェブ検索(キーワード有りのみ)
# """
# 与えられたキーワードに対してウェブ検索を行う
# """
# import requests
# from bs4 import BeautifulSoup
# import time
# import urllib.parse
# import fitz  # PyMuPDF
# import random

# class WebSearcher:
#     def __init__(self, keyword):
#         self.keyword = keyword
#         self.headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102 Safari/537.36"
#         }
#         try:
#             self.results = self.total_actions()
#         except Exception as e:
#             print(f"[ERROR] total_actions failed: {e}")
      
#     #queryのテンプレートが決まっていればここで作成
#     def marge_keyword(self):
#         try:
#             query = []
#             query.append(self.keyword["enterprise"])
#             for product in self.keyword["product"]:
#                 query.append(self.keyword["enterprise"] + "+" + product)
#             return query
#         except Exception as e:
#             print(f"[ERROR] marge_keyword failed: {e}")

#     #links(検索結果)から一つずつ本文をとってくる return:list 本文<body>
#     def fetch_article_content(self, url):
#         try:
#             if url.endswith('.pdf'):
#                 response = requests.get(url, headers=self.headers)
#                 pdf_document = fitz.open(stream=response.content, filetype="pdf")
#                 content = ""
#                 for page in pdf_document:
#                     content += page.get_text()
#                 pdf_document.close()
#             else:
#                 response = requests.get(url, headers=self.headers)
#                 soup = BeautifulSoup(response.content, "html.parser")
#                 body = soup.body
#                 tables = ''.join([str(table) for table in body.find_all('table')])
#                 for table in body.find_all('table'):
#                     table.extract()
                
#                 # headerとfooterを削除
#                 for header in body.find_all('header'):
#                     header.decompose()
#                 for footer in body.find_all('footer'):
#                     footer.decompose()
#                 text = body.get_text(strip=True, separator="\n")
#                 content = text + "\n" + tables
#             return content
#         except Exception as e:
#             print(f"[ERROR] fetch_article_content failed for {url}: {e}")

#     #DuckDuckGoで検索結果を取得する return:list link
#     def duckduckgo_search(self, query):
#         query_results = []
#         for q in query:
#             try:
#                 url = f"https://duckduckgo.com/html/?q={q.replace(' ', '+')}"
#                 response = requests.get(url, headers=self.headers)
#                 soup = BeautifulSoup(response.text, "html.parser")
#                 query_result = {"query": q, "results": []}
#                 for result in soup.select(".result__title")[:2]:
#                     link = result.find("a")["href"]
#                     parsed = urllib.parse.urlparse("https:" + link)
#                     query = urllib.parse.parse_qs(parsed.query)
#                     real_url = query["uddg"][0]
#                     content = self.fetch_article_content(real_url)
#                     query_result["results"].append({
#                         "link": real_url,
#                         "content": content
#                     })
#                 query_results.append(query_result)
#                 time.sleep(random.uniform(10, 12))
#             except Exception as e:
#                 print(f"[ERROR] duckduckgo_search failed for query '{q}': {e}")
#         return query_results

#     #全体実行
#     def total_actions(self):
#         try:
#             query = self.marge_keyword()
#             results = self.duckduckgo_search(query)
#             return results
#         except Exception as e:
#             print(f"[ERROR] total_actions failed: {e}")


# if __name__ == "__main__":
#     keyword = {
#         "enterprise": "日本碍子株式会社",
#         "product": ["エネセラ"]
#     }
#     searcher = WebSearcher(keyword)
#     print(searcher.results)