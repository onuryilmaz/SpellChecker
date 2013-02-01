# Onur Yilmaz

# Imports
import re, collections
import nltk
import string
from nltk.corpus import brown
import operator

def words(text): return re.findall('[a-z]+', text.lower()) 

# Training function which adds 1 if not exists
def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model

# Train for Brown's all categories
words = [w.lower() for w in brown.words(categories='news') if all(c in string.ascii_letters for c in w)]
NWORDS = train(words)

# Definition of alphabet
alphabet = 'abcdefghijklmnopqrstuvwxyz'

# Assumed that if the controlled word is already found,
# number of occurrences will be counted x100 (100%) so that
# its probability will calculated as increased
weight_0away = 100

# Distance weights gathered from
# "Design of an interactive spell checker: optimizing the list of
# offered words" by Garfinkel, Fernandez, Gopal
weight_1away = 95
weight_2away = 4
weight_3away = 1

# 1-away edit function, gathered from the file in COW
def edits1(word):
    # Split for helper
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    # Deleting a letter
   deletes    = [a + b[1:] for a, b in splits if b]
    # Transposing 2 letters
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    # Replacing a letter with another letter
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    # Inserting a letter into word
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
    # Return complete set
   return set(deletes + transposes + replaces + inserts)

# 2-away edit function, it uses 1-away edit function twice
def edits2(word):
    return set(two_away for one_away in edits1(word) for two_away in edits1(one_away))

# Function for words that are 1-away in distance
# Input:    Complete list of 1-away distant words
# Return:   Set of words that are already occurring in corpus
# Count of 1-away words is multiplied with "weight_1away" and
# count of original word is multiplied with "weight_0away"  
def found_1away_not_sorted(word):
    temp2 = dict([(x, NWORDS.get(x)*weight_1away) for x in edits1(word) if x in NWORDS])
    if word in NWORDS and word in temp2.keys():
        temp2[word] = temp2[word] * weight_0away
    return temp2

# Function for words that are 2-away in distance
# Input:    Complete list of 2-away distant words
# Return:   Set of words that are already occurring in corpus
# Count of 2-away words is multiplied with "weight_2away" and
# count of original word is multiplied with "weight_0away"
def found_2away_not_sorted(word):
    temp2 = dict([(x, NWORDS.get(x)*weight_2away) for x in edits2(word) if x in NWORDS])
    if word in NWORDS and word in temp2.keys():
        temp2[word] = temp2[word] * weight_0away
    return temp2

# Function for words that are 3-away in distance
# Return:   Set of words that are already occurring in corpus, sorted according to their counts
# Count of 3-away words is multiplied with "weight_3away" and
# count of original word is multiplied with "weight_0away"  
def found_3away_with_numbers(word):
    temp1 = [three_away for two_away in edits2(word) for three_away in edits1(two_away)]
    temp2 = [x for x in temp1 if x in NWORDS]
    temp3 = dict([(x, NWORDS.get(x)*weight_3away) for x in temp2]) 
    if word in NWORDS and word in temp3.keys():
        temp3[word] = temp3[word] * weight_0away
    return sorted(temp3.iteritems(), key=operator.itemgetter(1),reverse=True)

# If words is short (<4) then only consider 1-edit-away, otherwise:
# Firstly, if there are any, combines 1-edit-away and 2-edit-away known words
#       Then sorts and returns the top 5 according to their weighted counts
# If there is no 1 or 2 away known words, it returns the 3-edit-away words that already sorted
def found_all(word, limited):
    if len(word) < 4 and len(found_1away_not_sorted(word)) != 0:
        temp1 = dict(found_1away_not_sorted(word).items())
        return sorted(temp1.iteritems(), key=operator.itemgetter(1),reverse=True) [:5]        
    elif len(found_1away_not_sorted(word)) != 0 and len(found_2away_not_sorted(word)) != 0:
        temp1 = dict((found_2away_not_sorted(word).items() + found_1away_not_sorted(word).items()))
        return sorted(temp1.iteritems(), key=operator.itemgetter(1),reverse=True) [:5]
    elif len(found_2away_not_sorted(word)) != 0:
        temp1 = dict(found_2away_not_sorted(word).items())
        return sorted(temp1.iteritems(), key=operator.itemgetter(1),reverse=True) [:5]
    # Considering MemoryError where 3-edit-away 
    elif limited < 1:
         return found_3away_with_numbers(word) [:5]
    else:
        return []
    
# Correction function that returns words and their probabilities    
def correct_word(word):
    total_counts = sum(j for i, j in found_all(word,0))
    return [(x,round((float(y)/float(total_counts)),3)) for x,y in found_all(word,0)] [:5] 

# Correction function that returns words and their probabilities    
def correct_word_memory_error(word):
    total_counts = sum(j for i, j in found_all(word,1))
    return [(x,round((float(y)/float(total_counts)),3)) for x,y in found_all(word,1)] [:5] 

# End of code
