import argparse
import json
from dataclasses import dataclass
from typing import Optional

import requests
from ascii_graph import sys
from bs4 import BeautifulSoup, ResultSet

parser = argparse.ArgumentParser(description="sum the integers at the command line")
parser.add_argument(
    "file",
    nargs="?",
    default=sys.stdout,
    type=argparse.FileType("w"),
    help="path to file",
)
args = parser.parse_args()

URL = "https://www.rottentomatoes.com"

best_tv_shows = requests.get(URL + "/browse/tv_series_browse/sort:popular")

soup = BeautifulSoup(best_tv_shows.text, "html.parser")
shows: ResultSet[BeautifulSoup] = soup.find_all(
    "a", attrs={"data-qa": "discovery-media-list-item-caption"}
)


@dataclass
class Show:
    title: str
    critics_score: Optional[int]
    audience_score: Optional[int]
    url: str

    @classmethod
    def parse_score(cls, score: str) -> Optional[int]:
        score = score.strip()
        if len(score) > 0:
            return int(score[:-1])
        return None


output = []

for show in shows:
    title = show.find("span", attrs={"data-qa": "discovery-media-list-item-title"})
    critics_score = show.find("rt-text", attrs={"slot": "criticsScore"})
    audience_score = show.find("rt-text", attrs={"slot": "audienceScore"})
    url = URL + show.attrs["href"]

    assert title and url and critics_score and audience_score

    show = Show(
        title=title.text.strip(),
        url=url,
        critics_score=Show.parse_score(critics_score.text),
        audience_score=Show.parse_score(audience_score.text),
    )
    output.append(show.__dict__)

json.dump(output, args.file)
