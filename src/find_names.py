#!/usr/bin/env python3

import argparse
import urllib.request
import re
import random

from bs4 import BeautifulSoup, Comment

import nltk
from nltk.tag.stanford import NERTagger

URLTEMPLATE = "http://archiveofourown.org/works/{0}?view_adult=true&view_full_work=true"

def get_html(workid):
    """Given an AO3 work id number, return the HTML text from the corresponding
    page."""
    url = URLTEMPLATE.format(workid)
    resp = urllib.request.urlopen(url)
    data = resp.read()
    text = data.decode('utf-8')
    return text

def normalize_quotes(text):
    punctuation = { 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22 }
    return text.translate(punctuation)

def get_text(workid):
    """Given an AO3 work id number, get the text out of it."""
    html = get_html(workid)
    soup = BeautifulSoup(html)

    # drop dem comments.
    comments = soup.find_all(text=lambda thing:isinstance(thing, Comment))
    for comment in comments:
        comment.extract() 

    chapters = soup.find(id='chapters')
    if chapters is None:
        print("CHAPTERS IS NONE")
        print(html)
        return None
    text = chapters.get_text("\n\n")
    text = normalize_quotes(text)
    ## print("[[[START TEXT]]]")
    ## print(text)
    ## print("[[[END TEXT]]]")
    return text

def set_of_named_entities(tagged_sentences):
    """ """
    out = set()
    entities = []
    for ts in tagged_sentences:
        entity = ()
        entity_tag = None
        for tok,tag in ts:
            if tag != entity_tag:
                if entity_tag:
                    entities.append((entity_tag, entity))
                entity = ()
                entity_tag = None
            if tag != 'O':
                entity = entity + (tok,)
                entity_tag = tag
            else:
                entity = []
                entity_tag = None
        if entity_tag:
            entities.append((entity_tag, entity))
    return set(entities)

def get_argparser():
    """Build the argument parser for main."""
    parser = argparse.ArgumentParser(description='remix')
    parser.add_argument('--workid', type=int, required=True)
    return parser

def main():
    parser = get_argparser()
    args = parser.parse_args()

    ner = NERTagger('lib/english.all.3class.distsim.crf.ser.gz',
                    'lib/stanford-ner-2013-06-20.jar',
                    encoding='utf-8')
    text = get_text(args.workid)

    sentences = nltk.sent_tokenize(text)
    tokenized_sentences = [nltk.word_tokenize(s) for s in sentences]

    tagged_sentences = ner.batch_tag(tokenized_sentences)
    print(set_of_named_entities(tagged_sentences))

if __name__ == "__main__": main()
