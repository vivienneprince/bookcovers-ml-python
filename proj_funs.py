import pandas as pd
import numpy as np
import string
import re
from ast import literal_eval

import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image

from collections import Counter
from stop_words import get_stop_words
# from nltk.corpus import stopwords  # I DONT KNOW WHY BUT THIS IS NOT WORKING :(

from joblib import Parallel, delayed

import requests
import os.path

STOP_WORDS = get_stop_words('english') 


def read_saved(df_filename):
    """import saved dfs for project

    Args:
        df_filename (str): file path from project folder
    """
    df = pd.read_csv(df_filename)
    df = df.drop(columns=["Unnamed: 0"])
    df['subjects'] = df['subjects'].apply(literal_eval)

    # === RETURN === 
    return(df)


def extract_subjects(k=1, row=None, n_works=1, collated=True, report_freq=1*10**4):
    """Extracts subjects from the 'subjects' column of 'works' table from Open Libaray dump

    Args:
        k (int): Current row index being processed
        row (pd.DataFrame): Current row being processed
        n_works (int): Number of rows to process
        collated (bool, optional): Extract collated or non-collated subjects (see comments below). Defaults to True.
        report_freq (int, optional): Freqency to print progress {k/n_works}. Defaults to 1*10**4.
    """

    if collated: 
        # === COLLATED ===
        # Preserves multi-word subjects in data
        # e.g. ["Body piercing", "History ."] = ["body-piercing", "history"]

        # convert all to lowercase
        curr_subjects = row["subjects"].lower() 
        # extract all subjects from each subject array (text between "'s)
        curr_subjects = re.findall('"([^"]*)"', curr_subjects)
        # convert to np.array
        curr_subjects = np.array(curr_subjects)

        # remove all punctuation and leading/ trailing whitespaces
        curr_subjects = [
            subj.translate(str.maketrans('', '', string.punctuation))
                .strip()
            for subj in curr_subjects]
        # remove any empty strings
        while("" in curr_subjects): curr_subjects.remove("")
        # replace all spaces with "-"
        curr_subjects = [subj.replace(' ', '-') for subj in curr_subjects]

    else: 
        # === SPLIT === 
        # Splits each subject in data into single words
        # Treats each word in subject field as one subject
        # e.g. ["Body piercing", "History ."] = ["body", "piercing", "history"]

        # convert all to lowercase
        curr_subjects = row["subjects"].lower() 
        # remove all punctuation 
        curr_subjects = curr_subjects.translate(str.maketrans('', '', string.punctuation))
        # exception: keep non-fiction words together
        curr_subjects = re.sub('non fiction', 'non-fiction', curr_subjects)
        # split processed subjects string into array of individual words
        curr_subjects = curr_subjects.split()
        # remove all stopwords
        curr_subjects = [subj for subj in curr_subjects if not subj in STOP_WORDS]

    # === PROGRESS REPORT === 
    if k % (report_freq) == 0:
        print('{0:-8} / {1:}'.format(k, n_works))

    # === RETURN === 
    return(curr_subjects)


def downloadImage(image_url, location):
    img_data = requests.get(image_url).content
    with open(location, 'wb') as handler:
        handler.write(img_data)


def save_covers(image_ids, size):
    for id in image_ids:
        # print("saving", id)
        cover_location = f"covers/{id}-{size}.jpg"
        if not os.path.isfile(cover_location):
            cover_url = f"https://covers.openlibrary.org/b/id/{id}-{size}.jpg"
            downloadImage(cover_url, cover_location)