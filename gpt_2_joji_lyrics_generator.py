# -*- coding: utf-8 -*-
"""GPT-2 Joji Lyrics Generator.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KSbzZ4DcraH9YZPrqNVRjS8V51t5tApg
"""

GENIUS_API_TOKEN='rT5RsoMPpem87a-w4QyqBY1-Bw37wsJaPItxns05NXH8FcYSSVkqlO5PJyur9yC-'

import requests
from bs4 import BeautifulSoup
import os
import re

# Get artist info using Genius API
def request_artist_info(artist_name, page):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + GENIUS_API_TOKEN}
    search_url = base_url + '/search?per_page=10&page=' + str(page)
    data = {'q': artist_name}
    response = requests.get(search_url, data=data, headers=headers)
    return response

# Get song url
def request_song_url(artist_name, song_cap):
    page = 1
    songs = []
    
    while True:
        response = request_artist_info(artist_name, page)
        json = response.json()
        song_info = []
        for hit in json['response']['hits']:
            if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
                song_info.append(hit)
        for song in song_info:
            if (len(songs) < song_cap):
                url = song['result']['url']
                songs.append(url)
            
        if (len(songs) == song_cap):
            break
        else:
            page += 1
        
    print('Found {} songs by {}'.format(len(songs), artist_name))
    return songs

# Scrape lyrics from song url
def scrape_song_lyrics(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find('div', class_='lyrics').get_text()
    #remove identifiers and newline
    lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)
    lyrics = os.linesep.join([s for s in lyrics.splitlines() if s])         
    return lyrics

def write_lyrics_to_file(artist_name, song_count):
    f = open(artist_name.lower() + '.txt', 'wb')
    urls = request_song_url(artist_name, song_count)
    for url in urls:
        lyrics = scrape_song_lyrics(url)
        f.write(lyrics.encode("utf8"))
    f.close()
    num_lines = sum(1 for line in open(artist_name.lower() + '.txt', 'rb'))
    print('Wrote {} lines to file from {} songs'.format(num_lines, song_count))

write_lyrics_to_file('Joji', 50)

# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 1.x
!pip install -q gpt-2-simple
import gpt_2_simple as gpt2
from datetime import datetime
from google.colab import files

gpt2.download_gpt2(model_name="124M")

"""The below cell (only work in Colaboratory) will mount personal Google Drive in the VM, which later cells can use to get data in/out."""

gpt2.mount_gdrive()

file_name = "joji.txt"

sess = gpt2.start_tf_sess()

gpt2.finetune(sess,
              dataset=file_name,
              model_name='124M',
              steps=1000,
              restore_from='fresh',
              run_name='run1',
              print_every=10,
              learning_rate=1e-5,
              sample_every=200,
              save_every=500
              )

gpt2.copy_checkpoint_to_gdrive(run_name='run1')

gpt2.generate(sess, run_name='run1')