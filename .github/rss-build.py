#!/usr/bin/env python3

from xml.etree import ElementTree as ET
from os import listdir
from os.path import isfile, join, basename
from datetime import datetime as dt
from datetime import timezone
from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo
from argparse import ArgumentParser

ATOM_NS: str = "http://www.w3.org/2005/Atom"
DC_NS: str = "http://purl.org/dc/elements/1.1/"

TITLE: str = "the blog"
DESCRIPTION: str = "the blog"
AUTHOR: str = "jaiden riordan"

# Missing link and feed URL

def rfc822(dt: dt) -> str:
    dt = dt.replace(tzinfo=ZoneInfo("America/Chicago"))
    dt = dt.astimezone(timezone.utc)
    ctime = dt.ctime()
    return (f'{ctime[0:3]}, {dt.day:02d} {ctime[4:7]}'
                + dt.strftime(' %Y %H:%M:%S %z'))

def buildRSS(baseURL: str, posts: list[(str, str, dt, str)]):
    ET.register_namespace("atom", ATOM_NS)
    ET.register_namespace("dc", DC_NS)
    feed = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(feed, "channel")
    ET.SubElement(channel, "title").text = TITLE
    ET.SubElement(channel, "link").text = baseURL + "blog.html"
    ET.SubElement(channel, f"{{{ATOM_NS}}}link", {"rel": "self", "type": "application/rss+xml", "href": baseURL + "feed.rss"})
    ET.SubElement(channel, "description").text = DESCRIPTION
    ET.SubElement(channel, "language").text = "en"

    if posts:
        ET.SubElement(channel, "lastBuildDate").text = rfc822(posts[0][2])
    else:
        ET.SubElement(channel, "lastBuildDate").text = rfc822(dt.now(tz=timezone.utc))

    for post in posts:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = post[0]
        link = "{link}{slug}".format(
            link = baseURL,
            slug = f"blog/{post[1]}"
        )
        ET.SubElement(item, "link").text = link
        ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = link
        ET.SubElement(item, "pubDate").text = rfc822(post[2])
        ET.SubElement(item, f"{{{DC_NS}}}creator").text = AUTHOR
        ET.SubElement(item, "description").text = post[3]

    ET.indent(feed, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(feed, encoding="unicode")

def parsePost(post):
    with open(post, 'r') as f:
        soup = BeautifulSoup(f, features="html.parser")

        # Post Title
        title = soup.find("h1")
        if title:
            title = title.string

        # Post Date
        date = soup.find("subtitle")
        if date:
            date = date.string

        date = dt.strptime(date, "%B %d %Y")

        # Description
        desc = soup.find_all("p")
        if desc:
            desc = " ".join(desc[0].string.split())

        return (title, basename(post), date, desc)

def getListOfBlogPosts(blogDir):
    return [file for file in listdir(blogDir) if isfile(join(blogDir, file)) and file.endswith('.html')]

def main():
    parse = ArgumentParser(prog='RSS Generator')
    parse.add_argument('blogDir')
    parse.add_argument('--baseUrl')
    parse.add_argument('--output')
    args = parse.parse_args()

    blogDir = args.blogDir
    baseUrl = args.baseUrl
    posts = getListOfBlogPosts(blogDir)
    posts = [parsePost(join(blogDir, post)) for post in getListOfBlogPosts(blogDir)]
    with open(args.output, 'w') as f:
        f.write(buildRSS(baseUrl, posts) + '\n')

main()
