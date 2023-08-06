
# Discovery and Representation of Open Making Related Terms

Bulent Ozel, UZH

```bulent.ozel@gmail.com```

-----------

The first objective of this module is to provide a customizable and standardized text preprocessing prior to further analyses where more advanced machine learning and or statistical techniques can be applied and compared with each other. In that sense, it provides a pipelined set of functionalities (i) to be able to inspect, organize, prune and merge texts around one or very few specific theme(s) or topic(s), (ii) remove unwanted terms or literals from the texts, (iii) tokenize the texts, (iv) count the terms in texts, and (v) when desired stem the tokenized terms.

The second objective of this module is to be able compare or score a foreground corpus or a specific corpus against a background corpus or reference corpus. Example use cases could be, for instance, exploring the language of a sub-culture, a community, or a movement looking at to what extend the specific use of the language of the group differentiates itself from the common language.

In cases when there are more than a few number of themes or topics, and where each topic is represented with a large set of documents that validates the employment of standardized matrix decomposition based methodologies, then the scoring option of this module can be skipped entirely. More specifically, in use cases where the objective is being able to classify and differentiate a number of topics or issues from each other and where there are sufficient data that fulfills
the underlining assumptions of NMF, LDA or LSI based approaches, then tools from, for instance, Python’s [sklearn.decomposition](http://scikit-learn.org/stable/modules/decomposition.html#non-negative-matrix-factorization-nmf-or-nnmf) package are suggested.

Nevertheless, the outputs of this module, such as its normalized term frequencies or the specificity scores it associates to them regarding to a reference background corpus, can be used as input to other matrix decomposition techniques.  

--------

Support for this work is partly covered by the OpenMaker Project: [http://openmaker.eu/](http://openmaker.eu/)

Collaborators(s):
   * Hamza Zeytinoglu

----------

## Install

### A. Via Python's standard distribution channel PyPI
```bash
pip install omterms
```
### B. Via from its GitHub source 
```bash
git clone https://github.com/bulentozel/omterms.git
```

```bash
cd omterms
```

```bash
pip install .
```

## A quick use
```python
>>> from omterms.interface import *
>>> extract_terms("Some input X text to process less then 3 seconds.").head()
Configuring the text cleaner ...
A single text is provided.
Extracting the terms ...
Tokenizing the input text ..
Done. Number of terms: 10
Cleaning process: Initial size of tokens = 10
Reduction due to punctuations and stopwords = 3.
Reduction due to all numeral terms = 1
Reduction due to short terms = 1
Reduction due to rare terms = 0
Reduction due to partially numeral terms = 0
Reduction due to terms with not allowed symbols = 0
The total term count reduction during this cleaning process = 5
Percentage = 50%
COMPLETED.
   TF     Term  wTF
0   1    input  0.2
1   1     text  0.2
2   1  process  0.2
3   1     less  0.2
4   1  seconds  0.2
>>> 

```
## More on usage
[Please see the tutorial.](https://github.com/bulentozel/omterms/blob/master/tutorial.ipynb)

-------------

--------------

# Roadmap on Keyword and Keyphrase Extraction

The method outlined here aims to set-up a base line for future improvements.

 * It uses a statistical approach combined with standardized procedures that are widely applied in standard NLP workflows.
 * In this base line, it aims to present a work flow that can be ablied to
     * different languages
     * differrent problem domains
     * analysis on a single theme with limited training set

## 1. Overall work flow
In short, the workflow presented on this notebook is the second stage on a workflow objective of which is being able to measure relevance of a given external input to a specific theme, issue or topic. The steps of the work flow is as follows.

1. Forming a specific corpus where the corpus consists of set of documents around a topic. The corpus could be
    - a set of blog articles around an issue let say green finance
    - or a set of Wikipedia articles around the same subject
    - or collection of news articles around the green finance
    - or collection of tweets around the same issue.
    
    At the moment we have another module that given a set of seed Wikipedia articles around an issue the crawler scrapes textual data from articles. For the details of the module please [see the scraper module.](https://github.com/bulentozel/OpenMaker/tree/master/Scraping). The output of that module is a set of input texts stored in a collection in JSON format. 

2. Given an input set of texts on a theme a concept or a topic identify set of terms that more likely or less likely can occur within a discussion on the topic. This module hereby presents one of the simple methods for this purpose.

3. Given a list of weighted terms which are more likely to occur or reprsent a theme, concept or topic and input query text measure the relevance of the input text to the topic/theme/concept. [The notebook in this link](https://github.com/bulentozel/OpenMaker/blob/master/Semantics/Score%20Text.ipynb) demonstrates one way doing such scoring of a given text against the curated set of terms of this particular module.


## 2. Suggested future work

* Comparing and combining this comparison based scoring with matrix decompostion based topic modelling approaches such as NMF, LDA, LSI.

* Using language specicif term frequency counts of Wikipedia itself for comparisons. In NLP terminology, the *foreground* corpus around a topic needs to be compared and contrasted to a *background* corpus.

* Improving the semantic crawler of the previous stage to be able to increase quality of the specific corpuses


### Methodological Improvements
* Instead of tokenizing all terms, examine possibilities of key-phrase extrcation combining with *tf-idf* and 
    - experiment with extracting noun phrases and words, for this use NLTK's regular expression module for POS (part of speeach) analysis.
    - extract n-grams where n=1,2,3

## 3. Definitions and assumptions

### Assumptions
* At the comparison stage, it is assumed that a document's terms tend to be relatively frequent within the document as compared to an external reference corpus. However, it should be noted this assumption is contested in the field. See the paper by Chuang et el.

* Condidering the fact that the crawler is used to aggregate semantically related set of documents into a single document, *tf x idf* is equivalent to *tf*. As can be seen below, we use a normalized version of *tf*: *ntS / NS*.

* Fewer number of but relatively more relevant training (input corpus) is prefered in order to reduce term extraction problems due to length of documents. However, it should be noted that the crawling depth of an identiefied wiki article from stage 1 of this document can be used as an additional weight on relevance/reprsesntation of keywords.

* We have limited ourselves to terms instead of n-grams and phrases or use of POS to be able to develop a base model that can work on different languages.
 
 
### Term
Given for instance a set of texts around open source software movement a term that is identified can be a word such as *openness*, a person such as *Stallman* a license type such as *GNU*, an acronym for an organization such as *FSF* the Free Software Foundation, or a technology such as *Emacs*.

### Likelihood ratio
It is a simple measure computed comparing frequency count of a term in a specific corpus versus its frequency count in the reference reference corpus. Here assumption is that the reference corpus is a large enough sample of the language at observing the occurance of a term. Then having a higher/lower observation frequency of a term in the specific corpus is a proxy indicator for the term choice while having a debate on the topic.

The likelihood ratio for a term $P_t$ is calculated as:

$P_t = log ( (ntS/NS) / (ntR/NR) )$

where

- *ntS* is the raw frequency count of the term in the entire specific corpus
- *ntR* is the raw frequenccy count of the term in the reference corpus
- *NS* is the total number of terms in the specific corpus
- *NR* is the total number of terms in the reference corpus

It should be noted that frequency counts are calculated after having applied the same tokenization and post processing such as excluding stop-words, pancuations, rare terms, etc both on the reference corpus and the specific corpus.


## 4. Some thoughts on a conceptual approach at using the extracted keywords or phrases to predict topical relevance of a new text

Using the outcome of this technique to score arbitrary input texts against a single issue such as financial sustainability or against a set of issues such as the 10 basic human values requires a set of normalization of the raw scores and their rescaling/transformation.

The factors that need to be considered are:

- **Differing document lengths:** The likelihood of repetion of a key phrase increases as the size of the input text gets larger. In more concrete terms, when a scoring that simply sums up detection of weighted keyphrases or words within a given input text would be very sensitive to the document length. For isntance, the an executive summary of an article would very likely get quite lower score than the full article on any issue.

    *Among other methods, this can simply be resolved by computing per word scores, where the word set to be conidered is the tokenized and cleaned set of words that represent the input text.*


- **Topical relevance:** This factor would be important when the subject matter of the inputs texts vary among each other. In other words, this factor would matter to a very high significance, let's say when one wants to compare perceptions of indivuduals on the role of traditions in the personal lives and when this question is not asked them in a uniform manner that under the same social, cultural, environmental and physical conditions.
    
    Let’s assume that issue under investigation is again the perception and role of traditions in personal lives. It is possible that the same blogger with a strong opinion on traditions (i) may not touch the issue while talking on data science, (ii) he would slightly touch the issue while he talks about her preferences in mobile devices (iii) He dives into subject using all keywords and phrases when he talks about impact of traditions on social order. In brief, it is necessary to offset the variability of the topical relavance of an input text to the issue under investigation when arbitrary text samples are used for scoring.
   
    *An offsetting scheme can be devised when opinion or perception of an actor is to be measured with respect to more than one factor that define the issue under investigation. For instance, when we want to measure the position of a political leader on individual liberties vs social security or when we want to profile discourse of the political leader as of a ten basic human values we could employ some simple statistical methods in order to offset the topical relevance of the discourses or the speeches of the political figure to what we would like to measure.*
    
    *A simple method could be rescaling the scores on each sub factor such as the scores of liberty and security that are measured from the same speech into a range of -1 to 1. This can simply be done by taking the mean of the two and then deducting the mean from each score and scaling them into a scala of -1 to 1. This way it may be possible to use multiple speeches of the same political figure on different topics to evalaute his or her postion on liberty vs security matter.*
   
   In statistical terms this problem corresponds to adjusting or normalizing ratings or scores measured on different scales to a notionally common scale. Given the fact that in most cases a normal distribution for underlying factors may not be assumed the quantile-normalization technique is suggested. The quantile normalization sorts and ranks the variables with a non-negative amplitudes. Then these rankings can be scaled to for instance to a 0-1 interval. 


- **Level of subjectivity**.  This is variability in terms of relevant importance attributed to each issue given a set of issues. For instance, according to a study (Schwartz 2012), it is seen that almost all cultures around the world attach a higher importance to ‘universalism’ human value than the ’power’ basic human value. So when the objective of the scoring is not simply to rank of importance attached to each of them, then a comparative importance with respect to overall observations needs to be tackled.

    *Observed variances in each query texts can be considered. That is, a simple statistical methods can be used for instance to be able to compare two or more query texts with respect to each other. A suggested method would be (1) estimate coefficient of variation for each input text using per-word scores (2) the rescale quantile-normalized scores that is suggested above using the estimated coefficient of variation in each case.*
    
    *When this rescaling is applied for instance to universalism versus power or liberty vs security the coeffcient of variation would act as a polarization measure.*

#### Scoring and value system profiling

When one attempts to use scores, for instance, around the basic ten human values and one wants to construct the value system of the person, then both ranking of the scores as well as the relevant importance of each score from a number of texts from the same person should be taken into consideration.

## 5. State of the art 

* Survey Paper: Kazi Saidul Hasan and Vincent Ng, 2014. “Automatic Keyphrase Extraction: A Survey of the State of the Art” Proceedings of the 52nd Annual Meeting of the Association for Computational Linguistics, pages 1262–1273.

* Survey Paper: Sifatullah Siddiqi and Aditi Sharan. Article: Keyword and Keyphrase Extraction Techniques: A Literature Review. International Journal of Computer Applications 109(2):18-23, January 2015

* Survey Paper: Z. A. Merrouni, B. Frikh, and B. Ouhbi. Automatic keyphrase extraction: An overview of the state of the art. In 2016 4th IEEE
Colloquium on Information Science and Technology
(CiSt), pages 306–313, Oct 2016

* PageRank - Topical: Zhiyuan Liu, Wenyi Huang, Yabin Zheng and Maosong Sun, 2010. “Automatic Keyphrase Extraction via Topic Decomposition”. Proceeding EMNLP '10 Proceedings of the 2010 Conference on Empirical Methods in Natural Language Processing Pages 366-376 

* RAKE (Rapid Automatic Keyword Extraction ): Stuart Rose, Dave Engel, Nick Cramer, and Wendy Cowley. Automatic
keyword extraction from individual documents. Text Mining, pages 1–20, 2010.

* TextRank - Graph Based : Rada Mihalcea and Paul Tarau. Textrank: Bringing order into texts.
Association for Computational Linguistics, 2004.

* STOPWORDS: S. Popova, L. Kovriguina, D. Mouromtsev, and I. Khodyrev. Stopwords
in keyphrase extraction problem. In 14th Conference

* Corpus Similarity - Keyword frequency based: Adam Kilgarriff. Using word frequency lists to measure corpus homogeneity and similarity between corpora. In Proceedings of ACLSIGDAT Workshop on very large corpora, pages 231–245, 1997.

* Recommendation - Keyphrase Based: F. Ferrara, N. Pudota and C. Tasso. A keyphrase-based paper recommender system. In: Digital Libraries and Archives. Springer Berlin Heidelberg, 2011. p. 14-25.

* Jason Chuang, Christopher D. Manning, Jeffrey Heer, 2012. "Without the Clutter of Unimportant Words": Descriptive Keyphrases for Text Visualization" ACM Trans. on Computer-Human Interaction, 19(3), 1–29.


------------------------------------------------------------
Learn more about the OpenMaker project: http://openmaker.eu/

------------------------------------------------------------

