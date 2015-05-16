#!/usr/bin/env python3

import math
import sys
from collections import defaultdict
import argparse

def getMatchNum(str1,str2):
    len1 = len(str1)
    len2 = len(str2)
    dp = [[0]*(len2+1) for i in range(len1+1)]

    for pos1 in range(1,len1+1):
        for pos2 in range(1,len2+1):
            if str1[pos1-1] == str2[pos2-1]:
                dp[pos1][pos2] = dp[pos1-1][pos2-1]+1
            else:
                dp[pos1][pos2] = max(dp[pos1-1][pos2],dp[pos1][pos2-1])

    return dp[len1][len2]

parser = argparse.ArgumentParser()
parser.add_argument("converted",help="converted file", type=str)
parser.add_argument("test",help="test file",type=str)
args = parser.parse_args()

try:
    with open(args.converted,"r") as train, open(args.test) as test:
        suc = 0
        nm1 = 0
        nm2 = 0
        nmm = 0
        num = 0 # the smaller of the number of lines of two files
        while True:
            line1 = train.readline().strip()
            line2 = test.readline().strip()
            if line1=="" or line2=="":
                break
            num += 1
            len1 = len(line1)
            len2 = len(line2)
            match = getMatchNum(line1,line2)
            print(match)
            nm1 += len1
            nm2 += len2
            nmm += match
            if len1==match and len2==match:
                suc += 1
            else:
                print(line1)
                print(line2)
    print("Intersection/%s = %d/%d = %5.2f%%" % (args.converted, nmm,nm1, 100*nmm/nm1))
    print("Intersection/%s = %d/%d = %5.2f%%" % (args.test,      nmm,nm2, 100*nmm/nm2))
    print("Sentence Accuracy = %d/%d = %5.2f%%\n" % (suc,num,100*suc/num))

except IOError:
    exit("Cannot open file")
