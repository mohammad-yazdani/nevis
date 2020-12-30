from deepsegment import DeepSegment
# The default language is 'en'
segmenter = DeepSegment('en')
print(segmenter.segment('I am Batman i live in gotham'))
# ['I am Batman', 'i live in gotham']
