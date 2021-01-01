from spacy.lang.en import English

nlp = English()
sentencizer = nlp.create_pipe("sentencizer")
nlp.add_pipe(sentencizer)
doc = nlp("This is a sentence. This is another sentence.")
assert len(list(doc.sents)) == 2
print(list(doc.sents))
