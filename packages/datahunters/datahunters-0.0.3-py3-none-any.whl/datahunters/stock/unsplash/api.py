"""API for unplash.

https://unsplash.com/developers
"""

import json
import objectpath
import requests

from datahunters.stock.common import StockContent, StockImageAPIBase


class UnsplashImage(StockContent):
  collection = ""
  likes = 0

  def __str__(self):
    return "unsplash image: {}".format(self.full_url)


class UnsplashAPI(StockImageAPIBase):
  api_key = None
  base_url = "https://api.unsplash.com"

  def __init__(self, api_key):
    self.api_key = api_key

  def convert_raw_photo(self, raw_photo):
    """Convert raw photo json to stockimage object.
    """
    stock_img = UnsplashImage()
    stock_img.img_id = raw_photo["id"]
    stock_img.created_date = raw_photo["created_at"]
    stock_img.description = raw_photo["description"]
    stock_img.full_url = objectpath.Tree(raw_photo).execute("$.urls.full")
    stock_img.normal_url = objectpath.Tree(raw_photo).execute("$.urls.regular")
    stock_img.link = objectpath.Tree(raw_photo).execute("$.links.html")
    stock_img.owner = objectpath.Tree(raw_photo).execute("$.user.username")
    stock_img.likes = raw_photo["likes"]
    return stock_img

  def parse_img_res_headers(self, headers):
    """Extract info from response headers.
    """
    total_page_num = None
    next_page_link = None
    remain_limits = headers["X-Ratelimit-Remaining"]
    links = headers["Link"]
    link_parts = links.split(",")
    for link_part in link_parts:
      if link_part.find("last") != -1:
        page_info = link_part.split("&")[-2]
        total_page_num = int(page_info.split("=")[-1])
      if link_part.find("next") != -1:
        next_page_link = link_part.split(";")[0][1:-1]
    next_page_link = next_page_link.strip("<")
    next_page_link = next_page_link.strip(">")
    return total_page_num, next_page_link, remain_limits

  def get_imgs(self, start_page=-1):
    print("start fetching images...")
    if start_page == -1:
      start_page = 1
    next_page_link = "{}/photos?client_id={}&page={}&per_page=30".format(
        self.base_url, self.api_key, start_page)
    while next_page_link:
      try:
        res = requests.get(next_page_link)
        res_json = res.json()
        for raw_photo in res_json:
          cur_img_obj = self.convert_raw_photo(raw_photo)
          yield cur_img_obj
        # get next page link.
        _, next_page_link, remain_limits = self.parse_img_res_headers(
            res.headers)
        if remain_limits == 0:
          print("request limits exceeded.")
          break
      except Exception as ex:
        print("error processing get_imgs request {}: {}".format(
            next_page_link, ex))

  def get_random_imgs(self):
    """Fetch random images.
    """
    next_link = "{}/photos/random?client_id={}&count=30".format(
        self.base_url, self.api_key)
    while True:
      res = requests.get(next_link)
      res_json = res.json()
      for raw_photo in res_json:
        cur_img_obj = self.convert_raw_photo(raw_photo)
        yield cur_img_obj

  def search_imgs(self, keywords):
    next_page_link = "{}/search/photos?client_id={}&query={}&page=1&per_page=30".format(
        self.base_url, self.api_key, keywords)
    while next_page_link:
      res = requests.get(next_page_link)
      # get images.
      res_json = res.json()
      for raw_photo in res_json["results"]:
        cur_img_obj = self.convert_raw_photo(raw_photo)
        yield cur_img_obj
      # get link to next page.
      _, next_page_link = self.parse_img_res_headers(res.headers)


class UnsplashAPITest(object):
  """Class for testing api.
  """
  engine = None

  def __init__(self):
    with open("configs.json", "r") as f:
      configs = json.load(f)
    self.engine = UnsplashAPI(configs["api_key"])

  def test_get_imgs(self):
    img_gen = self.engine.get_imgs()
    print("fetching images...")
    for _ in range(100):
      cur_img = next(img_gen)
      print(cur_img)

  def test_search_imgs(self):
    img_gen = self.engine.search_imgs("people")
    print("searching images...")
    for i in range(10):
      cur_img = next(img_gen)
      print(cur_img)

  def test_random_imgs(self):
    img_gen = self.engine.get_random_imgs()
    for i in range(10):
      cur_img = next(img_gen)
      print(cur_img.full_url)


if __name__ == "__main__":
  api_tester = UnsplashAPITest()
  api_tester.test_get_imgs()
