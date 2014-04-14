In this project, spell checker for English language is implemented.  

The module named "spelling_corrector" tries to correct misspelled words in English.

Function which is named as "correct_word" will have single misspelled word and return at most five probable suggestions and their probabilities from your system:

> correct_word(word)

The system is trained with Brown Corpus which has over one million tokens.

### Example usage: 

> correct_word('said')

> [('said',0.9902),('aids',0.0049),('maids',0.0049)]


For further information and complete analysis of proposed method: [Implementation Details](https://github.com/cornetto/SpellChecker/wiki/Implementation-Details)  
