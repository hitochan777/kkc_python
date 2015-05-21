#!/usr/bin/python3

#=====================================================================================
#                           kkc.py
#                           by Otsuki Hitoshi
#                           Last change : 21 May 2015
#=====================================================================================

# Function : Conversion of kana to kanji using a statistical method
#
# Usage : kkc.py (TRAINING CORPUS) < (a file containing kana characters you want to convert to kanji)
#
# Example : kkc.py ../corpus/L.wordkkci < ../corpus/T.kkci
#
# Note  : The input sequence you want to convert to kanji must be given to standard input
#
# Reference : http://plata.ar.media.kyoto-u.ac.jp/mori/research/

import math
import sys
from collections import defaultdict
import argparse

def KKCInput():
    """ Function: Returns a list of input symbols
    """
    LATINU = "Ａ Ｂ Ｃ Ｄ Ｅ Ｆ Ｇ Ｈ Ｉ Ｊ Ｋ Ｌ Ｍ Ｎ Ｏ Ｐ Ｑ Ｒ Ｓ Ｔ Ｕ Ｖ Ｗ Ｘ Ｙ Ｚ".split(" ")
    NUMBER = "０ １ ２ ３ ４ ５ ６ ７ ８ ９".split(" ")
    HIRAGANA = "ぁ あ ぃ い ぅ う ぇ え ぉ お か が き ぎ く ぐ け げ こ ご さ ざ し じ す ず せ ぜ そ ぞ た だ ち ぢ っ つ づ て で と ど な に ぬ ね の は ば ぱ ひ び ぴ ふ ぶ ぷ へ べ ぺ ほ ぼ ぽ ま み む め も ゃ や ゅ ゆ ょ よ ら り る れ ろ ゎ わ ゐ ゑ を ん".split(" ")
    OTHERS =  \
    "ヴ ヵ ヶ".split(" ") +  \
    "ー ＝ ￥ ｀ 「 」 ； ’ 、 。".split(" ") + \
    "！ ＠ ＃ ＄ ％ ＾ ＆ ＊ （ ） ＿ ＋ ｜ 〜 ｛ ｝ ： ” ＜ ＞ ？".split(" ") +  \
    "・".split(" ")
    return LATINU + NUMBER + HIRAGANA + OTHERS

def kkConv(sent):
    """ Function: convert sent(sequence of kana)to kanji
        Note    : node = (prev, pair, logP)
                  Parameters are given as global variables
    """
    sent = sent.strip()
    POSI = len(sent)                     
    VTable = [[] for i in range(0,POSI+1)]          # Viterbi Table
    VTable[0].append((None, BT, 0));                # leftmost position of DP table
    # print(totalFreq)
    for posi in range(1,POSI+1):                    # end position to analyse
        for start in range(0,posi):                 # start position to analyse
            kkci = sent[start:posi]
            for pair in freqDict[kkci]:             # loop for known words
                if pairFreq[pair] == 0:             
                    continue
                # sys.stderr.write("%s%s(%d)\n" % (" "*start, pair, pairFreq[pair]))
                best = (None,None,0)                # best node
                for node in VTable[start]:
                    logP = node[2] - math.log(pairFreq[pair]/totalFreq)
                    if best[1] == None or logP < best[2]:
                        best = (node,pair,logP)
                        # sys.stderr.write("%s -> %s (%5.2f)\n" % (node[1], pair, logP));
                if best[1] != None:                 # if best node is found
                    VTable[posi].append(best)       # add best node to DP table
            if posi - start <= UTMAXLEN:            # create 
                best = (None,None,0)                # best node
                for node in VTable[start]:
                    logP = node[2] - math.log(pairFreq[UT]/totalFreq) + (posi - start + 1) * charLogP
                    if best[1] == None or logP < best[2]:
                        pair = "/".join([kkci,UT])
                        best =(node,pair,logP)
                        # sys.stderr.write("%s -> %s (%5.2f)\n" % (node[1], pair, logP))
                if best[1] != None:                 # If best node is found
                    VTable[posi].append(best);      # add best node to DP table 
    best = (None,None,0)                            # best node
    for node in VTable[POSI]:                       # obtain the best transition to BT
        logP = node[2]-math.log(pairFreq[BT]/totalFreq)
        if best[1] == None or logP < best[2]:
            best = (node, BT, logP)
    
    # 逆向きの探索と変換結果の表示
    result = []                                   # Result ["word1/kkci1","word2/kkc2",...]
    node = best[0]                                # Rightmost node
    while node[0] != None:                        # Traverse nodes toward left
        result.append(node[1])                    # store pair in result
        node = node[0];

    result.reverse()
    return result

BT = "BT"  # End of sentence 
UT = "UT"  # Unknown symbol

UTMAXLEN = 4                                      # maximum length of unknown words
kkcInput = KKCInput();                            # a list containing input symbols
charLogP = math.log(1+len(kkcInput));             # -(log of 0-gram probability)

#-------------------------------------------------------------------------------------
#                        Generation of language model "pairFreq" 
#-------------------------------------------------------------------------------------

pairFreq = defaultdict(int) #Word/Sequence of input symbols => Frequency

parser = argparse.ArgumentParser()
parser.add_argument("trainingFile",help="training file", type=str)
args = parser.parse_args()

try:
    with open(args.trainingFile,"r") as train:
        for line in train:
            for e in line.strip().split(" "):
                pairFreq[e] += 1    # Increment the frequency of each pair
            pairFreq[BT] += 1       # Increment the frequence of end of sentence symbol
        sys.stderr.write("counting frequency done\n")
except IOError:
    exit("Cannot open file " + args.trainingFile)

#-------------------------------------------------------------------------------------
#                        Smoothing
#-------------------------------------------------------------------------------------

totalFreq = 0   # totalFreq = \sum pairFreq
UTcount = 0     # frequency of unknown token
for key in pairFreq:
    freq = pairFreq[key]
    totalFreq += freq
    if freq == 1:           # If frequency is 1
        UTcount += 1        # Increment frequency of UT by 1
        pairFreq[key] = 0   # zero the frequency of "key"
pairFreq[UT] = UTcount
#-------------------------------------------------------------------------------------
#                Create conversion dictionary "d" of kana to kanji
#-------------------------------------------------------------------------------------

freqDict = defaultdict(list)                    # kkci => [word1/kkci,word2/kkci,...]
for key in pairFreq:                            # loop for f(pair) > 0 
    if key==BT or key==UT or pairFreq[key]==0:  # don't put special symbols to dictionary
        continue
    kkci = key.split("/")[1]                
    freqDict[kkci].append(key)                  # add key to freqDict[kkci]
    
#-------------------------------------------------------------------------------------
#                        main
#-------------------------------------------------------------------------------------

for line in sys.stdin:
    result = kkConv(line)
    # print(result)
    out = [s.split("/")[0] for s in result] # Extract only converted parts of the result and join them
    print("".join(out))
