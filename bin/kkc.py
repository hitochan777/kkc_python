#!/usr/bin/python3

import math
import sys
from collections import defaultdict
import argparse

def KKCInput():
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
    POSI = len(sent)                      # 解析位置 posi の最大値
    VTable = [[] for i in range(0,POSI+1)] # Viterbi Table
    VTable[0].append((None, BT, 0));               # DP左端

    for posi in range(1,POSI+1):
        for start in range(0,posi):
            kkci = sent[start:posi]
            for pair in d[kkci]:
                if pairFreq[pair] == 0:
                    continue
                best = (None,None,0)
                for node in VTable[start]:
                    logP = node[2] - math.log(pairFreq[pair]/totalFreq)
                    if best[1] == None or logP < best[2]:
                        best = (node,pair,logP)
                if best[1] != None:
                    VTable[posi].append(best)
                print(best)
            if posi - start <= UTMAXLEN:
                best = (None,None,0)
                for node in VTable[start]:
                    logP = node[2] - math.log(pairFreq[UT]/totalFreq) + (posi - start + 1) * charLogP
                    if best[1] == None or logP < best[2]:
                        pair = "/".join([kkci,UT])
                        best =(node,pair,logP)
                if best[1] != None:              # 最良のノードがある場合
                    VTable[posi].append(best); # best をコピーして参照を記憶
                print(best)
    best = (None,None,0)
    for node in VTable[posi-1]:             # BT への遷移
        logP = node[2]-math.log(pairFreq[BT]/totalFreq)
        if best[1] == None or logP < best[2]:
            best = (node, BT, logP)
    
# 逆向きの探索と変換結果の表示
    result = []                                 # 結果 <word, kkci>+
    node = best[0]                             # 右端のノード
    while node[0] != None:                # ノードを左向きにたどる
        result.append(node[1])                # pair を配列に記憶していく
        node = node[0];

    result.reverse()
    return result

BT = "EOS" # 文末記号
UT = "UT"  # 未知語記号

UTMAXLEN = 4                                    # 未知語の最大長
kkcInput = KKCInput();                            # 入力記号集合
charLogP = math.log(1+len(kkcInput));             # 入力記号0-gram確率の負対数値

#-------------------------------------------------------------------------------------
#                        言語モデル pairFreq の生成
#-------------------------------------------------------------------------------------

pairFreq = defaultdict(int)

parser = argparse.ArgumentParser()
parser.add_argument("trainingFile",help="training file", type=str)
args = parser.parse_args()

try:
    with open(args.trainingFile,"r") as train:
        for line in train:
            for e in line.strip().split(" "):
                pairFreq[e] += 1
                pairFreq[BT] += 1
        sys.stderr.write("counting frequency done\n")
except IOError:
    exit("Cannot open file " + args.trainingFile)

#-------------------------------------------------------------------------------------
#                        Smoothing
#-------------------------------------------------------------------------------------

totalFreq = 0
pairFreq[UT] = 0
for key in pairFreq:
    freq = pairFreq[key]
    totalFreq += freq
    if freq == 1:
        pairFreq[UT] += 1
        pairFreq[key] = 0

#-------------------------------------------------------------------------------------
#                        仮名漢字変換辞書 d の作成
#-------------------------------------------------------------------------------------

d = defaultdict(list)
for key in pairFreq:
    if key==BT or key==UT:
        continue
    kkci = key.split("/")[1]
    d[kkci].append(key)
    
#-------------------------------------------------------------------------------------
#                        main
#-------------------------------------------------------------------------------------

for line in sys.stdin:
    result = kkConv(line)
    print(result)
    out = [s.split("/")[0] for s in result]
    print("".join(out))
