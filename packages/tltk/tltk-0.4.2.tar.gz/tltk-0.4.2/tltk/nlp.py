#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################
## Thai Language Toolkit : version  0.4
## Chulalongkorn University
## word_segmentation, syl_segementation written by Wirote Aroonmanakun
## Implemented :
##      chunk, ner_tag, segment, pos_tag, pos_tag_wordlist, word_segment, syl_segment, word_segment_mm, word_segment_nbest,
##      read_thaidict, reset_thaidict, check_thaidict
##      spell_candidates,
## To be inplemented
#### transcribe(ThaiText)  =>  IPA
#### pronounce(ThaiWord)  สหกิจ => สะหะกิด
#### spelling(Sound)  sat2 => สัตว์ สัด
#### spell_variants(ThaiWord)  โอเค => โอเช เคร
#### spell_correction(Word) => correct word
#### parse(ThaiText)  => dependency tree

#########################################################

#import codecs
import re
import math
import os
from copy import deepcopy
from collections import defaultdict
#import pkg_resources
import pickle
from nltk.tag.perceptron import PerceptronTagger

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline

from sklearn_crfsuite import CRF

##########################################################
## Read Dictionary in a text format one word per one line
##########################################################
def read_thaidict(Filename):
    global TDICT
#    ATA_PATH = pkg_resources.resource_filename('tltk', '/')

    if not os.path.exists(Filename):
        path = os.path.abspath(__file__)
        ATA_PATH = os.path.dirname(path)
        Filename = ATA_PATH + '/' + Filename
    file1 = open(Filename, 'r', encoding ='cp874')
    for line in  file1:
        w = line.rstrip()
        w = re.sub(r'\.','\\\.',w)
        TDICT[w] = 1
    return(1)

def read_thdict(Filename):
    global TDICT
    fileObject = open(Filename,'rb')  
    TDICT = pickle.load(fileObject)


##########################################################
## Clear Dictionary in a text format one word per one line
##########################################################
def reset_thaidict():
    global TDICT
    TDICT.clear()
    return(1)

#### Check whether the word existed in the dictionary 
def check_thaidict(Word):
    global TDICT
    if Word in TDICT:
        return(1)
    else:
        return(0)
    
    
####################################################################
##  spelling correction modified from Peter Norvig  http://norvig.com/spell-correct.html
####################################################################

#def P(word, N=sum(TDICT.values())):
#    global TDICT
#    "Probability of `word`."
#    return TDICT[word] / N

#def spell_correction(word): 
#    "Most probable spelling correction for word."
#    return max(candidates(word), key=P)

def spell_candidates(word): 
    return (known([word]) or known(edits1(word)) or known(edits2(word)) )

def known(words):
    global TDICT
    return list(w for w in words if w in TDICT)

def edits1(word):
#    letters    = 'abcdefghijklmnopqrstuvwxyz'
    letters = [chr(i) for i in range(ord('ก'),ord('์')+1)]
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return list(deletes + transposes + replaces + inserts)

def edits2(word): 
    return list(e2 for e1 in edits1(word) for e2 in edits1(e1))

##########################################################################
## POS tagging using nltk.tag.perceptron
#########################################################################
def pos_tag(Input,Option=""):
    global tagger
    results = []
    if Option == 'mm':
        out = word_segment_mm(Input)
    else: 
        out = word_segment(Input)
    try:
      tagger
    except NameError:
      pos_load()
#    print('worsseg in pos tag',out)
    for x in out.split('<s/>'):
        tag_result = []
        if x != '':
            sent = x.split('|')
            if '' in sent:
                sent.remove('')
            for (w,pos) in tagger.tag(sent):
                if w == ' ':
                    w = '<s/>'
                pos = change_tag(w,pos)
                tag_result.append((w,pos))
            tag_result.append(('<s/>','PUNCT'))    
            results.append(tag_result)
    return(results)

## pos tag on a list of words  [w1,w2,w3,...]
def pos_tag_wordlist(sent):
    global tagger
    results = []
    for (w,pos) in tagger.tag(sent):
        pos = change_tag(w,pos)
        results.append((w,pos))    
    return(results)

def pos_load():
    global tagger
    tagger = PerceptronTagger(load=False)
    path = os.path.abspath(__file__)
    ATA_PATH = os.path.dirname(path)
    filehandler = open(ATA_PATH +'/' + 'tnc-tagger.pick', 'rb') 
    tagger = pickle.load(filehandler)

def change_tag(w,pos):
    if re.match(r'[a-zA-Z0-9-_]+$',w):
        pos = 'X'
    elif re.match(r'[\#\+\-\_\=\*\&\^\%\$\@\}\{\]\[\<\>\/]$',w):
        pos = 'SYM'
    elif re.match(r'[\,\;\:\.\(\)\'\"\!\?]$',w):
        pos = 'PUNCT'
    elif re.match(r'[\<\>a-zA-Z\/]+$',w):
        pos = 'SYM'        
    return(pos)


###############################################################################################
### chunk parse  =  segment edu + word segment + pos tag + (ner)
### Input = Thai text
###
def chunk(txt):
    global SegSep
    global SSegSep
    global useg_model
    global tagger
    outs = ""
    out = ""
#    print(txt)
    ## do syllable segmentation
    sylseg = syl_segment(txt)
    sylseg = re.sub(' ','<s/>',sylseg)
    sylseg = re.sub(r'([^~])<s/>',r'\1~<s/>',sylseg)
    sylseg = re.sub(r'<s/>([^~])',r'<s/>~\1',sylseg)

    sylcopy = sylseg
    sylcopy = re.sub(r'~[0-9\.\,]+~','~DIGIT~',sylcopy)
    sylcopy = re.sub(r'~[a-zA-Z0-9\\\/\?\'\"\(\)\.]+~','~FOREIGN~',sylcopy)

    parcopy = sylcopy.split('~')
    par = sylseg.split('~')
#    print(sylcopy)
    ## do edu segmentation
    try:
      useg_model
    except NameError:
      useg_model_load()

    tags = useg_model.predict([features(parcopy, index) for index in range(len(par))])
    lst_tag = zip(par,tags)
    syl_seq = ''
    for (w,t) in lst_tag:
        if t == '<u/>':
            ## do word segmentation
            out = wordseg(syl_seq)
#            print('wordseg',out)
            ## do pos tagging
            try:
              tagger
            except NameError:
              pos_load()        
            tag_result = []
            if out != '':
                sent = out.split('|')
                if '' in sent:
                    sent.remove('')
                for (w,pos) in tagger.tag(sent):
                    pos = change_tag(w,pos)
                    ## do ner tagging
                    tag_result.append((w,pos))
#                print('pos tag',tag_result)    
                out = pack_ner(ner(tag_result))
                outs += out
            syl_seq = ''
            outs += '<u/>'
        else:
            syl_seq += w+'~'
    return(outs)
    

###################################################################################
## named entity recognition for Person, Location, Organization
## Input = list 0f (w,pos)
## Output = list of (w,pos,ner_tag)
## adapted from http://sklearn-crfsuite.readthedocs.io/en/latest/tutorial.html
def ner(sent):
    lx = []
    if sent[-1][0] == ' ': del(sent[-1]) 
    lx = sent2features(sent)
    try:
      ner_tagger
    except NameError:
      ner_load()

    p = ner_tagger.predict_single(lx)
    r = []
    for i in range(len(sent)):
        r.append(( sent[i][0], sent[i][1], p[i]))
    return (r)

def ner_load():
    global ner_tagger
    ner_tagger = CRF(algorithm='lbfgs',
          c1=10,
          c2=0.1,
          max_iterations=100,
          all_possible_transitions=False)
    path = os.path.abspath(__file__)
    ATA_PATH = os.path.dirname(path)
    filehandler = open(ATA_PATH +'/' + 'ner-tagger.pick', 'rb') 
    ner_tagger = pickle.load(filehandler)
    
def word2features(sent, i):
    word = sent[i][0]
    postag = sent[i][1]

    features = {
        'bias': 1.0,
        'word': word,
        'postag': postag,
    }
    if i > 0:
        word1 = sent[i-1][0]
        postag1 = sent[i-1][1]
        features.update({
            '-1:word': word1,
            '-1:postag': postag1,
        })
    else:
        features['BOS'] = True

    if i < len(sent)-1:
        word1 = sent[i+1][0]
        postag1 = sent[i+1][1]
        features.update({
            '+1:word': word1,
            '+1:postag': postag1,
        })
    else:
        features['EOS'] = True

    return features

def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    return [label for token, postag, label in sent]

def sent2tokens(sent):
    return [token for token, postag, label in sent]

def pack_ner(sent):
    out = ''
    flag = 'O'
    for (w,p,t) in sent:
        if re.match(r'[BI]-P',t) and flag == 'O':
            out += '<NEp>'+w+'/'+p+'|'
            flag = 'NEp'
            continue
        elif t == 'O' and flag == 'NEp':
            out += '</NEp>'+w+'/'+p+'|'
            flag = 'O'
            continue
        elif re.match(r'[BI]-O',t) and flag == 'O':
            out += '<NEo>'+w+'/'+p+'|'
            flag = 'NEo'
            continue
        elif t == 'O' and flag == 'NEo':
            out += '</NEo>'+w+'/'+p+'|'
            flag = 'O'
            continue
        elif re.match(r'[BI]-L',t) and flag == 'O':
            out += '<NEl>'+w+'/'+p+'|'
            flag = 'NEl'
            continue
        elif t == 'O' and flag == 'NEl':
            out += '</NEl>'+w+'/'+p+'|'
            flag = 'O'
            continue
        else:     
            out += w+'/'+p+'|'
    if flag == 'NEp':
        out += '</NEp>'
    elif flag == 'NEo':
        out += '</NEo>'
    elif flag == 'NEl':
        out += '</NEl>'
        
    return(out)

###############################################################################################




###############################################################################################
###  segment discourse unit + word segmentation
###  Input = Thai text,  syllable segments will be used to determine edu
###  then, syllable list in each edu will be passed to word segmentation
###  The output is a list of word segments marked with '|' and edu segments marked with '<u/>' 
def segment(txt):
    global SegSep
    global SSegSep
    global useg_model
    output = ""
    out = ""
    
#    print(txt)
    sylseg = syl_segment(txt)
    sylseg = re.sub(' ','<s/>',sylseg)
    sylseg = re.sub(r'([^~])<s/>',r'\1~<s/>',sylseg)
    sylseg = re.sub(r'<s/>([^~])',r'<s/>~\1',sylseg)

    sylcopy = sylseg
    sylcopy = re.sub(r'~[0-9\.\,]+~','~DIGIT~',sylcopy)
    sylcopy = re.sub(r'~[a-zA-Z0-9\\\/\?\'\"\(\)\.]+~','~FOREIGN~',sylcopy)

    parcopy = sylcopy.split('~')
    par = sylseg.split('~')
#    print(sylcopy)
    
    
    try:
      useg_model
    except NameError:
      useg_model_load()

    tags = useg_model.predict([features(parcopy, index) for index in range(len(par))])
    lst_tag = zip(par,tags)
    syl_seq = ''
    for (w,t) in lst_tag:
        if t == '<u/>':
            out = wordseg(syl_seq)
            output += out+'<u/>'
            syl_seq = ''
        else:
#            lst_syl.append(w)
            syl_seq += w+'~'
    return(output)

def useg_model_load():
    global useg_model
    useg_model = Pipeline([
    ('vectorizer', DictVectorizer(sparse=False)),
    ('classifier', RandomForestClassifier(n_jobs=2, random_state=0))])

    path = os.path.abspath(__file__)
    ATA_PATH = os.path.dirname(path)
    filehandler = open(ATA_PATH +'/' + 'sent_segment_rfs.pick', 'rb') 
    useg_model = pickle.load(filehandler)
    
def untag(tagged_sentence):
    return [w for w, t in tagged_sentence]

def transform_to_dataset(tagged_sentences):
    X, y = [], []
    for index in range(len(tagged_sentences)):
        X.append(features(untag(tagged_sentences), index))
        y.append(tagged_sentences[index][1]) 
    return X, y

## This function will get features from each token  sentence = list of tokens
def features(sentence, index):
    return {
        'word': sentence[index],
        'prev_word': '' if index == 0 else sentence[index - 1],
        'prev_biword' : '' if index <= 1 else sentence[index - 2]+sentence[index - 1],
        'next_word': '' if index == len(sentence) - 1 else sentence[index + 1],
        'next_biword': '' if index >= len(sentence) - 2 else sentence[index + 1]+sentence[index + 2],
        'has_hyphen': '-' in sentence[index],
        'is_numeric': sentence[index] == 'DIGIT',
        'is_space' : '<s/>' in sentence[index],
        'after_space' : False if index == 0 else sentence[index-1] == '<s/>',
        'before_space' : False if index == len(sentence) - 1 else sentence[index+1] == '<s/>',
        'dist_space' : 0 if '<s/>' not in sentence[:index] else distance(sentence,index),
        'Mai_yamok' : 'ๆ' in sentence[index],
        'after_FOR' : False if index == 0 else sentence[index-1] == 'FOREIGN',
        'before_FOR' : False if index == len(sentence) - 1 else sentence[index+1] == 'FOREIGN',
        'after_DIG' : False if index == 0 else sentence[index-1] == 'DIGIT',
        'before_DIG' : False if index == len(sentence) - 1 else sentence[index+1] == 'DIGIT',
    }

def distance(sentence,index):
    i = index-1
    while sentence[i] != '<s/>' and i > 0:
        i-=1
    return(index-i)    


#############################################################################################################
###  Word Segmentation for Thai texts
### Input = a paragraph of Thai texts
def word_segment(Input):
    global SegSep
    global SSegSep
    output = ""
    out = ""
    
    Input = preprocess(Input)
    sentLst = Input.split(SegSep)
    for s in sentLst:
#        print "s:",s
        inLst = s.split(SSegSep)
        for inp in inLst:
            if inp == '': continue            
#            print "inp:",inp
#            objMatch = re.match(r"[a-zA-Z0-9\-\_\+\=\(\)\*\&\^\%\$\#\@\!\~\{\}\[\]\'\"\:\;\<\>\?\/\\\. ]+",inp)
            objMatch = re.match(r"[^ก-์]+",inp)
            if objMatch:
                out = inp
            else:
                y = sylseg(inp)
                out = wordseg(y)
            output = output+out+WordSep
#        output = output.rstrip(WordSep)
        output = output+'<s/>'    ####write <s/> output for SegSep   
    return(output)        



###################################################################
###### Thai word segmentation using maximum collocation approach
###### Input is a list of syllables
###### also add each syllable as a potential word
def wordseg(Input):
    global TDICT
    global EndOfSent
    global chart
    global SegSep
    global WordSep
    global CollocSt
    
    part = []
    chart = defaultdict(dict)
    SylSep = '~'
    outx = ""
    chart.clear()
    CollocSt = defaultdict(float)
    
    part = Input.split(SegSep)
    for inx in part:
        SylLst = inx.split(SylSep)
        EndOfSent = len(SylLst)
        ######### Gen unknown word by set each syllable as a potential word
        gen_unknown_thaiw(SylLst)
        ############################################################
        for i in range(EndOfSent):
            for j in range(i,EndOfSent+1):
                wrd = ''.join(SylLst[i:j])
                if wrd in TDICT:
                    chart[i][j] = [wrd]
                    if j > i+1:   ### more than one syllable, compute St
                        St = 0.0
                        NoOfSyl = len(SylLst[i:j])
                        for ii in range(i,j-1):
                            St += compute_colloc("mi",SylLst[ii],SylLst[ii+1])
#                            xx = compute_colloc("mi",SylLst[ii],SylLst[ii+1])
#                            print (SylLst[ii],SylLst[ii+1],xx)
                        CollocSt[(i,j)] = St    #### Compute STrength of the word
#                        print(i,j,wrd,CollocSt[(i,j)])
                    else:   ### one sylable word St = 0
                        CollocSt[(i,j)] = 0.0
        if chart_parse():
            outx += WordSep.join(chart[0][EndOfSent])
            return(outx)
        else:
            return("<Fail>"+Input+"</Fail>")
        

####################################################################
#### Word segmentation using Dictionary lookup 
#### Input = Thai string,  method = syl | word  output = n-best segmentations
#### n-best segmentation is determined from the number of words. The fewer the better.
#### Output is a list of n-best segmentation [ [seg1, seg2, seg3, seg4, .... ] ]
#### If input is a multiple chunks of text, the output is the list of chunks' outputs.
#### e.g. [ [c1seg1, c1seg2, c1seg3, c1seg4, .... ] , [c2seg1, c2seg2, c2seg3, c2seg4, .... ] ]
######################################################################
def word_segment_nbest(Input,nbest):
    global SegSep
    global SSegSep
    output = []
    out = []
    
    Input = preprocess(Input)
    sentLst = Input.split(SegSep)
    for s in sentLst:
        inLst = s.split(SSegSep)
        for inp in inLst:
            if inp == '': continue            
            objMatch = re.match(r"[^ก-์]+",inp)  ## not Thai text
            if objMatch:
                out = [inp]
            else:
                out = wordsegmm_bn(inp,nbest)
            output.append(out)    
    return(output)

def wordsegmm_bn(Input,nbest):    
    global TDICT
    global EndOfSent
    global chartnb
    global SegSep
    global WordSep


    part = []
    chartnb = defaultdict(dict)
    outx = []
    chartnb.clear()
    
    part = Input.split(SegSep)
    for inx in part:
        SylLst = list(inx)
        EndOfSent = len(SylLst)
        ## look for all possible words in the string input
        for i in range(EndOfSent):
            for j in range(i,EndOfSent+1):
                wrd = ''.join(SylLst[i:j])
                if wrd in TDICT and wrd != '':
#                    print('wrd',wrd,i,j,SylLst[i:j])
                    chartnb[(i,j)][wrd] = 1
        ## chart parse            
        if chartparse_mm_bn():
            i = 1
            for seg1 in sorted(chartnb[(0,EndOfSent)], key=chartnb[(0,EndOfSent)].get):
#                print(i,seg1)
                outx.append(seg1)
                i += 1
                if i > nbest:
                    break     
        else:
            outx += ["<Fail>"+Input+"</Fail>"]
    return(outx)        


def chartparse_mm_bn():
    global chartnb
    global WordSep
    
    for j in range(EndOfSent):
        chartx = deepcopy(chartnb)
        if j in [ key[1] for key in chartnb if key[0] == 0 ]:
            for s1 in chartnb[(0,j)]:  # get the first part
                for k in [ key[1] for key in chartnb if key[0] == j ]:  # connecting paths 
                     for s2 in chartnb[(j,k)]:  # get the second part
                        path = s1+WordSep+s2
                        if path not in chartnb[(0,k)]:
                            chartx[(0,k)][path] = chartx[(0,j)][s1] + chartx[(j,k)][s2]  ## sum the number of words from s1 and s2
#                            print("New =>",0,j,k,chartx[(0,k)])
        chartnb = deepcopy(chartx)
    if chartnb[(0,EndOfSent)]:
        return(1)
    else:
        return(0)



####################################################################
#### Word segmentation using Maximal Matching (minimal word) approach
#### Input = Thai string,  method = syl | word
######################################################################
def word_segment_mm(Input):
    global SegSep
    global SSegSep
    output = ""
    out = ""
    
    Input = preprocess(Input)
    sentLst = Input.split(SegSep)
    for s in sentLst:
#        print "s:",s
        inLst = s.split(SSegSep)
        for inp in inLst:
            if inp == '': continue            
            objMatch = re.match(r"[^ก-์]+",inp)
            if objMatch:
                out = inp
            else:
                out = wordsegmm(inp)
            output = output+out+WordSep
#        output = output.rstrip(WordSep)
        output = output+'<s/>'    ####write <s/> output for SegSep   
    return(output)

def wordsegmm(Input):    
    global TDICT
    global EndOfSent
    global chart
    global SegSep
    global WordSep


    part = []
    chart = defaultdict(dict)
    outx = ""
    chart.clear()
    
    part = Input.split(SegSep)
    for inx in part:
        SylLst = list(inx)
        EndOfSent = len(SylLst)    
        for i in range(EndOfSent):
            for j in range(i,EndOfSent+1):
                wrd = ''.join(SylLst[i:j])
                if wrd in TDICT:
#                    words[(i,j)] = wrd
#                   print "word",wrd.encode('cp874'),i,j
                    chart[i][j] = [wrd]
        if chartparse_mm():
#            print '|'.join(chart[0][EndOfSent])
            outx += WordSep.join(chart[0][EndOfSent])
        else:
            outx += "<Fail>"+Input+"</Fail>"
#            GenUnknownThaiW(SylLst)
#            print "Try again with unknown words"
#            if ChartParseMM():
#                print '|'.join(chart[0][EndOfSent])            
#                outx += WordSep.join(chart[0][EndOfSent])
    return(outx)        

#########  Chart Parsing, ceate a new edge from two connected edges, always start from 0 to connect {0-j} + {j+k}
#########  If minimal word appraoch is chosen, the sequence with fewest words will be selected
def chartparse_mm():
    global chart
    
    for j in range(EndOfSent):
        chartx = deepcopy(chart)
        if j in chart[0]:
            s1 = chart[0][j]
            for k in chart[j]:
                    s2 = chart[j][k]
#                    print 0,j,k
                    if k not in chart[0]:                        
                        chartx[0][k] = s1+s2
                    else:
                        if len(s1)+len(s2) <= len(chart[0][k]):
                            chartx[0][k] = s1+s2
        chart = deepcopy(chartx)
    if EndOfSent in chart[0]:
        return(1)
    else:
        return(0)


##########################################
# Compute Collocation Strength between w1,w2
# stat = chi2 | mi | ll
##########################################
def compute_colloc(stat,w1,w2):
    global TriCount
    global BiCount
    global Count
    global BiType
    global Type
    global NoTrigram
    global TotalWord
    global TotalLex

    if BiCount[(w1,w2)] < 1 or Count[w1] < 1 or Count[w2] < 1:
        BiCount[(w1,w2)] +=1
        Count[w1] +=1
        Count[w2] +=1 
        TotalWord +=2
    
###########################
##  Mutual Information
###########################
    if stat == "mi":
        mi = float(BiCount[(w1,w2)] * TotalWord) / float((Count[w1] * Count[w2]))
        value = math.log(mi,2)
#########################
### Compute Chisquare
##########################
    if stat == "chi2":
        value=0
        O11 = BiCount[(w1,w2)]
        O21 = Count[w2] - BiCount[(w1,w2)]
        O12 = Count[w1] - BiCount[(w1,w2)]
        O22 = TotalWord - Count[w1] - Count[w2] +  BiCount[(w1,w2)]
        value = float(TotalWord * (O11*O22 - O12 * O21)**2) / float((O11+O12)*(O11+O21)*(O12+O22)*(O21+O22))

    return(value)
    
##############################################################################    
########  create each unit (char/syllable) as a possible edge for chart parsing
def gen_unknown_thaiw(SylLst):
    global chart
    for i in range(EndOfSent):
        chart[i][i+1] = [SylLst[i]]
    return(1)



#############################################################################################################
#########  Chart Parsing, ceate a new edge from two connected edges, always start from 0 to connect {0-j} + {j+k}
#########  If maximal collocation appraoch is chosen, the sequence with highest score will be selected
def chart_parse():
    global chart
    global CollocSt
    
    for j in range(EndOfSent):
        chartx = deepcopy(chart)
        if j in chart[0]:
            s1 = chart[0][j]
            for k in chart[j]:
                    s2 = chart[j][k]
                    if k not in chart[0]:                        
                        chartx[0][k] = s1+s2
#                        CollocSt[(0,k)] = (CollocSt[(0,j)] + CollocSt[(j,k)])/2.0
                        CollocSt[(0,k)] = CollocSt[(0,j)] + CollocSt[(j,k)]
                    else:
                        if CollocSt[(0,j)]+CollocSt[(j,k)] > CollocSt[(0,k)]:
#                            CollocSt[(0,k)] = (CollocSt[(0,j)] + CollocSt[(j,k)])/2.0
                            CollocSt[(0,k)] = CollocSt[(0,j)] + CollocSt[(j,k)]
                            chartx[0][k] = s1+s2
        chart = deepcopy(chartx)
    if EndOfSent in chart[0]:
        return(1)
    else:
        return(0)


#############################################################################################################
###  Syllable Segmentation for Thai texts
### Input = a paragraph of Thai texts
def syl_segment(Input):
    global SegSep
    global SSegSep
    output = ""
    out = ""
    
    Input = preprocess(Input)
    sentLst = Input.split(SegSep)
    for s in sentLst:
#        print "s:",s
        inLst = s.split(SSegSep)
        for inp in inLst:
            if inp == '': continue            
            objMatch = re.match(r"[^ก-์]+",inp)
            if objMatch:
                out = inp
            else:
                out = sylseg(inp)
            output = output+out+SylSep
#        output = output.rstrip(SylSep)
        output = output+'<s/>'    ####write <s/> output for SegSep   
    return(output)        

#############################################################################################################
####### Segment syllable using trigram statistics, only strings matched with a defined syllable pattern will be created
####  Input = Thai string
def sylseg(Input):
    global SylSep
    global PRON
    
    schart = defaultdict(dict)
    probEnd = defaultdict(float)
    schartx = {}
    schart.clear()
    probEnd.clear()
    tmp = []
    
    EndOfInput = len(Input)
    for f in PRON:
        for i in range(EndOfInput):
            Inx = Input[i:]
            matchObj = re.match(f,Inx)
            if matchObj:
                k=i+len(matchObj.group())
                schart[i][k] = [matchObj.group()]
                probEnd[(i,k)] = prob_trisyl([matchObj.group()])
#                print("match",i,k, matchObj.group(),f,probEnd[(i,k)])
    
    for j in range(EndOfInput):
        schartx = deepcopy(schart)
        if j in schart[0]:
            s1 = schart[0][j]
            for k in schart[j]:
                    s2 = schart[j][k]
                    ####****** change this to merge only form, need to do this, otherwise probtrisyl is not correct.
                    tmp = mergekaran(s1+s2)
                    if k not in schart[0]:                        
#                        schartx[0][k] = s1+s2
#                        probEnd[k] = prob_trisyl(s1+s2)
                        schartx[0][k] = tmp
                        probEnd[(0,k)] = prob_trisyl(tmp)
#                        print("new",tmp,probEnd[k])
                    else:
#                        p = prob_trisyl(s1+s2)
                        p = prob_trisyl(tmp)
                        if p > probEnd[(0,k)]:
#                            print("replace",tmp,p,probEnd[(0,k)])
#                            schartx[0][k] = s1+s2 
                            schartx[0][k] = tmp 
                            probEnd[(0,k)] = p
        schart = deepcopy(schartx)
    if EndOfInput in schart[0]:    
        return(SylSep.join(schart[0][EndOfInput]))
    else:
        return('<Fail>'+Input+'</Fail>')

######################
def mergekaran(Lst):
####  reconnect karan part to the previous syllable for SylSegment
   rs = []
   Found = 'n'
   Lst.reverse()
   for s in Lst:
        if re.search(r"(.+)[ิุ]์",s):    # anything + i or u + Karan
            if len(s) < 4:
                Found = 'y'
                x = s
                continue
        elif  re.search(r"(.+)์",s):  # anything + Karan
            if len(s) < 4:
                Found = 'y'
                x = s
                continue
        if Found == 'y':
            s += x
            rs.append(s)
            Found = 'n'
        else:
            rs.append(s)
   rs.reverse()
   return(rs)


########################################
# calculate proability of each possible output
#  Version 1.6>  expect input = list of forms
########################################
def prob_trisyl(SylLst):
    global TriCount
    global BiCount
    global Count
    global BiType
    global Type
    global NoTrigram
    global TotalWord
    global TotalLex
    global SegSep
    Prob = defaultdict(float)
    
#    SegSep = chr(127)

    pw2 = SegSep
    pw1 = SegSep
    Probx = 1.0
    
    for w in SylLst:
        if (w,pw1,pw2) in Prob:
            Proba = Prob[(w,pw1,pw2)]
        else:
            Prob[(w,pw1,pw2)] = prob_wb(w,pw1,pw2)
            Proba = Prob[(w,pw1,pw2)]
#        Probx *= Proba
        Probx += Proba    ## prob is changed to log
        pw2 = pw1
        pw1 = w
#    print("prob ",Probx)
    
    return(Probx)

########################################
# p(w | pw2 pw1)   Smoothing trigram prob  Witten-Bell
#######################################
def prob_wb(w,pw1,pw2):
    global TriCount
    global BiCount
    global Count
    global BiType
    global Type
    global NoTrigram
    global TotalWord
    global TotalLex
    
    p3 = 0.0
    p2 = 0.0
    p1 = 0.0
    p = 0.0
    px1 = 0.0
    
#    print "trigram ", pw2,pw1,w
#    print "count ",TriCount[(pw2,pw1,w)],BiCount[(pw1,w)],Count[w]
    if TriCount[(pw2,pw1,w)] > 0:
        p3 = float(TriCount[(pw2,pw1,w)]) / float( BiCount[(pw2,pw1)] + BiType[(pw2,pw1)])
    if BiCount[(pw1,w)] > 0:
        p2 = float( BiCount[(pw1,w)]) / float((Count[pw1] + Type[pw1]) )
    if Count[w] > 0:
        p1 = float( Count[w]) / float(TotalWord + TotalLex)
    p = 0.8 * p3 + 0.15 * p2 + 0.04 * p1 + 1.0 / float((TotalWord + TotalLex)**2)
### change to log to prevent underflow value which can cause incorrect syllable segmentation
    p = math.log(p)

    return(p)

    

###### Read syllable pattern
def read_sylpattern(Filename):
    global PRON
    
#    PRON = defaultdict(str)
    
    tmp = [] 
    file1 = open(Filename,'r',encoding = 'cp874')
    for line in file1:
        if re.match(r'#',line):
            continue
        line = line.rstrip()
        tmp = line.split(',')
        tmp[0] = re.sub(r"X",u"([ก-ฮ])",tmp[0])
        tmp[0] = re.sub(r"C",u"([กขคจดตทบปผพฟสศซ])",tmp[0])
        tmp[0] = re.sub(r'Y',u"([ก-ฬฮ])",tmp[0])
        tmp[0] = re.sub(r'R',u"([รลว])",tmp[0])
        tmp[0] = re.sub(r'K',u"([ก-ฮ])",tmp[0])
        tmp[0] = re.sub(r'A',u"([กจฆดตบปอขฉฐถผฝศษสหคชพภทธมยรลวนณซญฑฏฌ])",tmp[0])
        tmp[0] = re.sub(r'Z',u"([กงดนมบรลฎฏจตณถพศทสชคภปญ])",tmp[0])
        tmp[0] = re.sub(r'D',u"([กงดนมบวยต])",tmp[0])
        tmp[0] = re.sub(r'W',u"[ก-ฮ]",tmp[0])
        tmp[0] = re.sub(r'\.',u"[\.]",tmp[0])
#        re.sub('Q',u"[\(\)\-\:\'\xCF\xE6]",tmp[0])
        if tmp[2] == "T":
            tmp[0] = re.sub(r"T",u"[่้๊๋]",tmp[0])
        else:
            tmp[0] = re.sub(r"T",u"[่้๊๋]*",tmp[0])
            
#       print tmp[0]
        PRON[tmp[0]] = tmp[1]
    
#    for x in PRON:
#        print x,PRON[x]

    return(1)


##########  Read syllanle dict, pronunciation not conformed to sylrule is specified here
def read_syldict(Filename):
    file1 = open(Filename,'r',encoding='cp874')
    for line in file1:
        if re.match(r'#',line):
            continue
        line = line.rstrip()
        tmp = line.split("\t")
        PRON[tmp[0]] = tmp[1]
    return(1)

####  read trigram statistics file
def read_stat(Filename):

    global TriCount
    global BiCount
    global Count
    global BiType
    global Type
    global TotalWord
    global TotalLex
    global TotalWord
    global TotalLex

    TriCount = defaultdict(int)
    BiCount = defaultdict(int)
    BiType = defaultdict(int)
    Count = defaultdict(int)
    Type = defaultdict(int)
    
    TotalWord = 0
    TotalLex = 0
    TriCount.clear()
    BiCount.clear()
    Count.clear()
    BiType.clear()
    Type.clear()

    fileObject = open(Filename,'rb')  
    TriCount = pickle.load(fileObject)
    for (X,Y,Z) in TriCount:
        BiType[(X,Y)] += 1
        BiCount[(X,Y)] += TriCount[(X,Y,Z)]
        Count[X] += TriCount[(X,Y,Z)]

    for (X,Y) in BiCount:
        Type[X] += 1
        
    for X in Count:
        TotalLex += 1
        TotalWord += Count[X]
        
    return(1)
    

########## Preprocess Thai texts  #### adding SegSep and <s> for speocal 
def preprocess(input):
    global SegSep
    global SSegSep

    input = re.sub(u" +ๆ",u"ๆ",input)

#    input = re.sub(u"เเ",u"แ",input)
####### codes suggested by Arthit Suriyawongkul #####
    NORMALIZE_DICT = [
        ('\u0E40\u0E40', '\u0E41'), # Sara E + Sara E -> Sara AE
        ('\u0E4D\u0E32', '\u0E33'), # Nikhahit + Sara AA -> Sara AM
        ('\u0E24\u0E32', '\u0E24\u0E45'), # Ru + Sara AA -> Ru + Lakkhangyao
        ('\u0E26\u0E32', '\u0E26\u0E45'), # Lu + Sara AA -> Lu + Lakkhangyao
    ]
    for k, v in NORMALIZE_DICT:
        input = input.replace(k, v)
########################################################        
#    print input.encode('raw_unicode_escape')

  ##### change space\tab between [ET][ET] and [ET]  to be SegSep
#    input = re.sub(r"([^\s\t\u00A0][\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]*[^\s\t\u00A0][\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]*)[\s\t\u00A0]+([^\s\t\u00A0])",r"\1"+SegSep+r"\2",input)
    input = re.sub(r"([^\s\t\u00A0]{3,})[\s\t\u00A0]+([^\s\t\u00A0]+)",r"\1"+SegSep+r"\2",input)

    
   ##### change space\tab between [ET] and [ET][ET]  to be SegSep
#    input = re.sub(r"([^\s\t\u00A0][\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]*)[\s\t\u00A0]+([^\s\t\u00A0][\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]*[^\s\t\u00A0][\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]*)",r"\1"+SegSep+r"\2",input)
    input = re.sub(r"([^\s\t\u00A0]+)[\s\t\u00A0]+([^\s\t\u00A0]{3,})",r"\1"+SegSep+r"\2",input)

  ###  handle Thai writing one character one space by deleting each space
    pattern = re.compile(r'([ก-ฮเแาำะไใโฯๆ][\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]*) +([ก-ฮเแาำะไใโฯๆ\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]{,2}) +|([ก-ฮเแาำะไใโฯๆ][\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]*) +([ก-ฮเแาำะไใโฯๆ\ุ\ู\ึ\ั\ี\๊\้\็\่\๋\ิ\ื\์]{,2})$')
    while re.search(pattern, input):
        input = re.sub(pattern, r"\1\2", input,count=1)



        ### handle English and Thai mixed without a space inside $s by adding SSegSep (softSegSep)
    input = re.sub(r"([ก-์][ฯๆ])",r"\1"+SSegSep,input)
    input = re.sub(r"([\u0E01-\u0E5B์]+\.?)([^\.\u0E01-\u0E5B]+)",r"\1"+SSegSep+r"\2",input)
#    input = re.sub(r"([\u0E01-\u0E5B]+)([^\.\u0E01-\u0E5B]+)",r"\1"+SSegSep+r"\2",input)
    input = re.sub(r"([^\.\u0E01-\u0E5B]+)([\u0E01-\u0E5B]+)",r"\1"+SSegSep+r"\2",input)
    input = re.sub(r"(<.+?>)",SSegSep+r"\1",input)
    input = re.sub(r"([0-9a-zA-Z\.\-]{2,})([\u0E01-\u0E5B]+)",r"\1"+SSegSep+r"\2",input)
    input = re.sub(r"(\.\.\.+)",r""+SSegSep+r"\1"+SSegSep,input)    #  ....  add SSegSep after that
#    print "3. ",input

    return(input)


#############################################################################################################
### initialization by read syllable patterns, syllable trigrams, and satndard dictionary
def initial():
    global SylSep
    global WordSep
    global SegSep
    global SSegSep
    global TDICT
    global PRON

    PRON = {}    
    TDICT = {}
    
    SylSep = chr(126)
    WordSep = chr(124)
    SSegSep = chr(30)
    SegSep = chr(31)

    path = os.path.abspath(__file__)
    ATA_PATH = os.path.dirname(path)
    
#    try:
#        ATA_PATH = pkg_resources.resource_filename('tltk', '/')
    
    read_sylpattern(ATA_PATH + '/sylrule.lts')
    read_syldict(ATA_PATH +  '/thaisyl.dict')
    read_stat(ATA_PATH + '/sylseg.3g')
    read_thdict(ATA_PATH +  '/thdict')


    return(1)


############ END OF GENERAL MODULES ##########################################################################

initial()

#xx= word_segment_nbest('คนขับรถประจำทางหลวง',10)
#print(xx)
#print(TDICT['คนขับรถ'])
#print(TDICT['รถประจำทาง'])

#print(syl_segment('นายกรัฐมนตรีกล่าวกับคนขับรถประจำทางหลวงสายสองว่า อยากวิงวอนให้ใช้ความรอบคอบอย่าหลงเชื่อคำชักจูงหรือปลุกระดมของพวกหัวรุนแรงจากทางการไฟฟ้า'))

#print(word_segment_mm('นายกรัฐมนตรีกล่าวกับคนขับรถประจำทางหลวงสายสองว่า อยากวิงวอนให้ใช้ความรอบคอบอย่าหลงเชื่อคำชักจูงหรือปลุกระดมของพวกหัวรุนแรงจากทางการไฟฟ้า'))
#print(word_segment('นายกรัฐมนตรีกล่าวกับคนขับรถประจำทางหลวงสายสองว่า อยากวิงวอนให้ใช้ความรอบคอบอย่าหลงเชื่อคำชักจูงหรือปลุกระดมของพวกหัวรุนแรงจากทางการไฟฟ้า'))

