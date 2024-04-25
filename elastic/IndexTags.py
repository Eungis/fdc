import csv
import os
import elasticsearch
from collections import deque
from elasticsearch import helpers
from dotenv import load_dotenv

load_dotenv()


def readMovies():
    csvfile = open("./data/ml-latest-small/movies.csv", "r")

    reader = csv.DictReader(csvfile)

    titleLookup = {}

    for movie in reader:
        titleLookup[movie["movieId"]] = movie["title"]

    return titleLookup


def readTags():
    csvfile = open("./data/ml-latest-small/tags.csv", "r")

    titleLookup = readMovies()

    reader = csv.DictReader(csvfile)
    for line in reader:
        tag = {}
        tag["user_id"] = int(line["userId"])
        tag["movie_id"] = int(line["movieId"])
        tag["title"] = titleLookup[line["movieId"]]
        tag["tag"] = line["tag"]
        tag["timestamp"] = int(line["timestamp"])
        yield tag


es = elasticsearch.Elasticsearch(
    ["https://localhost:9200"], ca_certs="./http_ca.crt", basic_auth=("elastic", os.environ["ELASTIC_PASSWORD"])
)
es.indices.delete(index="tags", ignore=404)
deque(helpers.parallel_bulk(es, readTags(), index="tags", request_timeout=300), maxlen=0)
es.indices.refresh()
