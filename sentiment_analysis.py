# -*- coding: utf-8 -*-
"""sentiment analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15ESrou1hIhrNHDmTrTwMuCAYQBe0DjZT
"""

!pip install praw

# Commented out IPython magic to ensure Python compatibility.
# data manipulations
import pandas as pd
import numpy as np
# date manipulation, data structures and chain iterators
import datetime as dt
from pprint import pprint
from itertools import chain
# reddit API wrapper
import praw
# Natural language toolkit to process text
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, RegexpTokenizer 
from nltk.corpus import stopwords
# numpy plotting
import matplotlib.pyplot as plt
# %matplotlib inline
plt.rcParams["figure.figsize"] = (10, 8)
# stats visualization
import seaborn as sns
sns.set(style='whitegrid', palette='Dark2')
# text visualization
from wordcloud import WordCloud

# nltk setup
nltk.download('vader_lexicon') 
# tokenizer
nltk.download('punkt') 
# stop words
nltk.download('stopwords')

# reddit client
r = praw.Reddit(user_agent = 'cryptosent',
                client_id = 'ialLiYAay-zBurlUIXhgRw',
                client_secret = 'ycu3NzpzaAFmyR6kIaG_WOt_Nx-G5Q',
                check_for_async = False)

# choose subreddit
subreddit = r.subreddit('CryptoCurrency')
query = 'news'
# search for news on subreddit
news = [*subreddit.search(query, sort='hot', time_filter='week', limit=None)]

# check
news0 = news[0]
print(news0.title)

# create a list of titles for each news
title = [news.title for news in news]

# create dataframe
news = pd.DataFrame({
    "title": title,
})
top5 = news.head()
print(top5)

# CHECK
sid = SentimentIntensityAnalyzer()

pos_text = "Vader is awesome"
cap_pos_text = "Vader is AWESOME!" 
neg_text = "Vader is bad"

print(sid.polarity_scores(pos_text))
print(sid.polarity_scores(cap_pos_text))
print(sid.polarity_scores(neg_text))

# calculate scores
res = [*news['title'].apply(sid.polarity_scores)]
pprint(res[:3])

# create dataframe by converting array 
sentiment_df = pd.DataFrame.from_records(res)
news = pd.concat([news, sentiment_df], axis=1, join='inner')
news.head()

THRESHOLD = 0.2

conditions = [
    (news['compound'] <= -THRESHOLD),
    (news['compound'] > -THRESHOLD) & (news['compound'] < THRESHOLD),
    (news['compound'] >= THRESHOLD),
    ]

values = ["neg", "neu", "pos"]
news['label'] = np.select(conditions, values)

news.head()

# check how vader works
sentence0 = news.title.iloc[0]
print(sentence0)
words0 = news.title.iloc[0].split()
print(words0)

pos_list, neg_list, neu_list = [], [], []

for word in words0:
  if (sid.polarity_scores(word)['compound']) >= THRESHOLD:
    pos_list.append(word)
  elif (sid.polarity_scores(word)['compound']) <= -THRESHOLD:
    neg_list.append(word)
  else:
    neu_list.append(word)                

print('\nPositive:',pos_list)        
print('Neutral:',neu_list)    
print('Negative:',neg_list) 
score = sid.polarity_scores(sentence0)

print(f"\nThis sentence is {round(score['neg'] * 100, 2)}% negative")
print(f"This sentence is {round(score['neu'] * 100, 2)}% neutral")
print(f"This sentence is {round(score['pos'] * 100, 2)}% positive")
print(f"The compound value : {score['compound']} <= {-THRESHOLD}")
print(f"\nThis sentence is NEGATIVE")

news.label.value_counts()

sns.histplot(news.label);

# aanother check
def news_title_output(df, label):
  res = df[df['label'] == label].title.values
  print(f'{"=" * 20}')
  print("\n".join(title for title in res))

# randomly sample
news_sub = news.groupby('label').sample(n = 5, random_state = 7)

print("Positive news")
news_title_output(news_sub, "pos")

print("\nNeutral news")
news_title_output(news_sub, "neu")

print("\nNegative news")
news_title_output(news_sub, "neg")

# download stopwords
stop_words = stopwords.words('english')
print(len(stop_words))
print(stop_words[:10])

def custom_tokenize(text):
  # remove single quote and dashes
  text = text.replace("'", "").replace("-", "").lower()

  # split on words only
  tk = nltk.tokenize.RegexpTokenizer(r'\w+')
  tokens = tk.tokenize(text)

  # remove stop words
  words = [w for w in tokens if not w in stop_words]
  return words
  print(custom_tokenize(text))

def tokens_2_words(df, label):
  # subset titles based on label
  titles = df[df['label'] == label].title
  # apply our custom tokenize function to each title
  tokens = titles.apply(custom_tokenize)
  # join nested lists into a single list
  words = list(chain.from_iterable(tokens))
  return words

pos_words = tokens_2_words(news, 'pos')
neg_words = tokens_2_words(news, 'neg')

pos_freq = nltk.FreqDist(pos_words)
pos_freq.most_common(20)

neg_freq = nltk.FreqDist(neg_words)
neg_freq.most_common(20)

def plot_word_cloud(words, colormap, stopwords = [], max_words = 100):
  text = " ".join(word for word in words)
  # generate word cloud 
  wordcloud = WordCloud(width=1000, height = 600,
                        max_words = max_words,
                        colormap=colormap,
                        stopwords = stopwords,
                        background_color="black").generate(text)

  # Display the generated image:
  plt.figure( figsize=(20,10), facecolor='k' )
  plt.imshow(wordcloud, interpolation='bilinear')
  plt.axis("off");

def extract_sentence_from_word(df, word, label, num = 3):
  contains_word = news['title'].str.contains(r"\b{}\b".format(word), case=False) # matches the word only
  label_type = news['label'] == label
  sent_list = news.loc[contains_word & label_type].title.values
  print("\n".join(sent for sent in sent_list[:num]))

custom_stopwords = ["new", "could", "say", "says"]
plot_word_cloud(pos_words, "Blues", custom_stopwords)

plot_word_cloud(neg_words, "Reds", custom_stopwords)

extract_sentence_from_word(news, "ignore", "neg")