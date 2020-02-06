#!/usr/bin/env python
import datetime
import requests
import requests.sessions
from bs4 import BeautifulSoup
import sqlite3

send_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0",
    "Connection": "keep-alive",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"}


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


def get_magnet_link(video_url, s):
    soup = BeautifulSoup(requests.get(
        video_url, cookies=s.cookies, headers=send_headers).text, 'html.parser')
    if 'magnet:?xt=urn:btih:' in str(soup.select('h1.entry-title:nth-child(4)')):
        video_magnet = soup.select(
            'h1.entry-title:nth-child(4) > a:nth-child(1)')[0]['href']
        print(video_magnet)
        return video_magnet

    elif 'magnet:?xt=urn:btih:' in str(soup.select('h1.entry-title:nth-child(3)')):
        video_magnet = soup.select(
            'h1.entry-title:nth-child(3) > a:nth-child(1)')[0]['href']
        print(video_magnet)
        return video_magnet

    elif "xpressdl.com" in str(soup.select('h1.entry-title:nth-child(4)')):
        video_magnet = "https://xpressdlbase.s3.amazonaws.com/ilovejav-" + \
            str(soup.select('h1.entry-title:nth-child(4) > a:nth-child(1)')
                [0]['href']).split('xpressdl.com/download/')[1] + ".torrent"
        print(video_magnet)
        return video_magnet

    elif "xpressdl.com" in str(soup.select('h1.entry-title:nth-child(3)')):
        video_magnet = "https://xpressdlbase.s3.amazonaws.com/ilovejav-" + \
            str(soup.select('h1.entry-title:nth-child(3) > a:nth-child(1)')
                [0]['href']).split('xpressdl.com/download/')[1] + ".torrent"
        print(video_magnet)
        return video_magnet

    elif 'avgle.com' in str(soup.select('h1.entry-title:nth-child(4)')):
        video_magnet = soup.select('h1.entry-title:nth-child(4)')[0].a['href']
        print(video_magnet)
        return video_magnet

    else:
        magnet_not_found = "magnet not found"
        print(magnet_not_found)
        return str(soup.select('h1.entry-title:nth-child(4)'))


def parse_page(url, c, s, number):
    soup = BeautifulSoup(requests.get(
        url, cookies=s.cookies, headers=send_headers).text, 'html.parser')
    articles = soup.find_all("article")
    print("[START] " + url)
    for i in range(len(articles)):
        # 获得视频标题
        video_title = articles[i].h4.string
        # 获得视频页链接
        video_url = "https://ilovejav.com" + articles[i].h4.a['href']
        # 进入视频页，获得种子链接
        video_magnet = get_magnet_link(video_url, s)
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        number += 1
        try:
            c.execute("INSERT INTO ilovejav_com VALUES (" + str(number) + ", '" +
                      video_title + "', '" + video_url + "', '" + video_magnet + "')")
            print(dt + "\tNo." + str(number) + "\t" + video_title)
        except Exception as e:
            print("ERROR: Can't append \tNo." + str(number))
            print('Reason:', e)
    return number


if __name__ == "__main__":

    conn = sqlite3.connect(':memory:')
    print("Opened database successfully")
    c = conn.cursor()
    # Create table
    c.execute('''CREATE TABLE ilovejav_com (
        ID INT,
        TITLE TEXT,
        URL TEXT,
        TORRENT TEXT
    );''')

    max_page = get_max_page_index()  # 获得最大页数
    number = 0

    user_email = input(' Input your email:\t')
    user_password = input(' Input your passowrd:\t')

    Data = {'action': 'signin', 'target': '',
            'email': user_email, 'password': user_password}

    # login session
    s = requests.session()
    signin_url = "https://ilovejav.com/signin"
    login = s.post(signin_url, data=Data, headers=send_headers)

    for index in range(max_page):
        # 解析每一页
        index += 1
        number = parse_page("https://ilovejav.com/?page=" +
                            str(index), c, s, number)

    with sqlite3.connect('ilovejav.com.db') as new_db:
        new_db.executescript("".join(conn.iterdump()))

    conn.close()
