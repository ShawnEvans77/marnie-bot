'''Constants used when generating word clouds.'''

from wordcloud import STOPWORDS

stopwords = STOPWORDS.union({
    "im", "ive", "ill", "id", "dont", "didnt", "doesnt", "cant", "couldnt",
    "thats", "theres", "youre", "youve", "youll", "theyre", "weve", "whats",
    "would", "could", "also", "like", "just", "yeah", "yes", "nah", "lol",
    "ok", "okay", "got", "get", "one", "two", "really", "much", "thing",
    "know", "new", "even", "people",
})
