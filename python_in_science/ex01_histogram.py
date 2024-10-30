import argparse
import sys
import string
from tqdm import tqdm
from collections import defaultdict
from ascii_graph import Pyasciigraph
from ascii_graph import colors
from ascii_graph.colordata import vcolor

import collections
from _collections_abc import Iterable

collections.Iterable = Iterable  # pyright: ignore

parser = argparse.ArgumentParser(
    description="create histogram of words from given file"
)
parser.add_argument(
    "file",
    nargs="?",
    default=sys.stdin,
    type=argparse.FileType("r"),
    help="path to file",
)
parser.add_argument(
    "-N",
    "--number",
    default=10,
    type=int,
    help="number of words to show in histogram",
)
parser.add_argument(
    "-L",
    "--min-length",
    default=1,
    type=int,
    help="min length of words to show in histogram",
)
parser.add_argument(
    "--ignore",
    nargs="+",
    default=[],
    type=str,
    help="list of words to ignored",
)

args = parser.parse_args()
assert args.number > 0
assert args.min_length > 0

TRANS_TABLE = str.maketrans("", "", string.punctuation + string.whitespace)

counts = defaultdict(int)

with args.file as file:
    while line := file.readline():
        for word in line.split():
            word: str = word.translate(TRANS_TABLE).lower()
            if len(word) >= args.min_length and word not in args.ignore:
                counts[word] += 1

counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)[: args.number]
counts = vcolor(counts, [colors.BWhi, colors.BGre])

graph = Pyasciigraph()
for line in tqdm(graph.graph("word counts histogram", counts), ascii=True):
    print(line)
