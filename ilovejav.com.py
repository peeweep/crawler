#!/usr/bin/env python
import csv
import requests
from bs4 import BeautifulSoup

send_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0",
    "Connection": "keep-alive",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"}


def dict2csv(dict, file):
    with open(file, 'wb') as f:
        w = csv.writer(f)
        # write all keys on one row and all values on the next
        w.writerow(str(dict.keys()))
        w.writerow(str(dict.values()))


def get_max_page_index():
    soup = BeautifulSoup(requests.get(
        "https://ilovejav.com/?page=1", headers=send_headers).text, 'html.parser')
    pages = []
    pagination = soup.select(".pagination")[0]
    for i in range(len(pagination.find_all('a'))):
        # <a href="?page=4108">...</a>
        pages.append(int(pagination.find_all('a')[i]['href'].lstrip('?page=')))
    pages.sort(reverse=True)
    return pages[0]  # 4108


def get_magnet_link(video_url):
    soup = BeautifulSoup(requests.get(video_url).text, 'html.parser')
    if 'magnet:?xt=urn:btih:' in str(soup.select('h1.entry-title:nth-child(4)')):
        return soup.select('h1.entry-title:nth-child(4) > a:nth-child(1)')[0]['href']

    elif "xpressdl.com" in str(soup.select('h1.entry-title:nth-child(4)')):
        xpressdl_magnet_link = soup.select(
            'h1.entry-title:nth-child(4) > a:nth-child(1)')[0]['href']
        return "https://xpressdlbase.s3.amazonaws.com/ilovejav-" + str(xpressdl_magnet_link).split('xpressdl.com/download/')[1] + ".torrent"

    elif "xpressdl.com" in str(soup.select('h1.entry-title:nth-child(3)')):
        xpressdl_magnet_link = soup.select(
            'h1.entry-title:nth-child(3) > a:nth-child(1)')[0]['href']
        return "https://xpressdlbase.s3.amazonaws.com/ilovejav-" + str(xpressdl_magnet_link).split('xpressdl.com/download/')[1] + ".torrent"

    else:
        return "magnet not found"


def parse_page(url, videos):
    soup = BeautifulSoup(requests.get(
        url, headers=send_headers).text, 'html.parser')
    articles = soup.find_all("article")
    print("parse " + url)
    for i in range(len(articles)):
        # 获得视频标题
        video_title = articles[i].h4.string
        # 获得视频页链接
        video_url = "https://ilovejav.com" + articles[i].h4.a['href']
        # 进入视频页，获得种子链接
        video_magnet = get_magnet_link(video_url)
        print("Get: " + video_title)
        videos.append(
            {'Title': video_title, 'Video Page': video_url, "Torrent Link": video_magnet})


if __name__ == "__main__":

    max_page = get_max_page_index()  # 获得最大页数
    videos = []

    for index in range(max_page):
        # 解析每一页
        index += 1
        parse_page("https://ilovejav.com/?page=" + str(index), videos)

    csv_columns = ['Title', 'Video Page', 'Torrent Link']

    csv_file = "ilovejav.com.csv"

    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in videos:
                writer.writerow(data)
        print("write all data to " + csv_file)
    except IOError:
        print("I/O error")
