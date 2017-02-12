#!/usr/bin/python3
"""
This is a program to re-implement Steve Tinney's
Cuneify program, hosted at:
    http://oracc.museum.upenn.edu/saao/knpp/cuneiformrevealed/cuneify/index.html
"""

import argparse
from collections import OrderedDict
from pprint import pprint
import pickle
import re
from sys import exit

def asciify(string):
    """Takes a string and converts Unicode characters to ASCII,
    following the conventions on ORACC:
        http://oracc.museum.upenn.edu/doc/help/visitingoracc/unicode/index.html
    """
    unicode_chars = ["š", "Š", "ṣ", "Ṣ", "ṭ", "Ṭ", "ḫ", "Ḫ", "ŋ", "Ŋ",
                     "×", "ʾ", "ʿ", "₀", "₁", "₂", "₃", "₄", "₅", "₆",
                     "₇", "₈", "₉", "ₓ", "⸢", "⸣", "⸤", "⸥", "ʳ"
                    ]
    # comma-second convention
    ascii_chars = ["c,", "c,", "s,", "S,", "t,", "T,", "h,", "H,", "j,", "J,",
                   "X,", "),", "(,", "0", "1", "2", "3", "4", "5", "6", 
                   "7", "8", "9", "x", "[,", "],", "", "", ",r"
                  ]
    # using epsd notation
    for i in range(len(unicode_chars)):
        string = string.replace(unicode_chars[i], ascii_chars[i])
    return string

def dictmap(row, m):
    """Look up each character in row using m, a list of dictionaries,
    which is structured as [unicode, ascii, ascii_nocommas].  
    Look through in that order, then swap case if nothing is found
    and search again."""
    new_row = ""
    for i in row:
        if len(i) > 1 and i[-1] in "!?#*": i = i[:-1]
        i = i.strip()
        i = i.strip("[]\\/()")
        tmp_val = m[0].get(i, m[1].get(i, m[2].get(i, i)))
        if tmp_val == i:
            i = i.swapcase()
            tmp_val = m[0].get(i, m[1].get(i, m[2].get(i, i)))
        if tmp_val != i: tmp_val = tmp_val[1]
        new_row += tmp_val + ' '
    return new_row
        
def dictmap_findall(chars, m):
    """A version of dictmap, but rather than using
    a dictionary, it uses a list of tuples.  This allows
    multiple sign readings to be preserved, and this function
    is only used with the --showall/-a flag due to much
    larger computational overhead.
    
    :param chars: list of characters to search for.
    :param m: mapping to use.  Keys will be ASCII-fied.
    """
    matches = OrderedDict()
    for C in chars:
        i = C
        # clean up the character for comparison
        if len(i) > 1 and i[-1] in "!#*?":
            i = i[:-1]
        i = i.strip()
        i = i.strip("[]()/\\0123456789")
        i = asciify(i)
        matches[C] = [j for j in m[0] 
                      if re.match("^{}[0-9]*$".format(i), asciify(j[0]))
                     ]
        matches[C] = sorted(matches[C], key=lambda x: x[0])
    return matches

if __name__ == "__main__":
    # command line: parse infile arguments.
    # NOTE: --file and --text will work together!  --file will be processed first, then --text.
    P = argparse.ArgumentParser()
    P.add_argument("--file", "-f", 
                   help="--file [file]. Specify input file(s) containing transliterated text to convert.")
    P.add_argument("--text", "-t", 
                   help="--text [text]. Manually provide text to convert via stdin. (processed after -f)")
    P.add_argument("--stdin", "-s", action="store_true", default=False, 
                   help="Read from stdin.  Will override -f and -t options.  Useful for piping data through.")
    P.add_argument("--lang", "-l",
                   help="Supply the three-letter code of a language to only use signs from that language.")
    P.add_argument("--showall", "-a", action="store_true", default=False, 
                   help="Show all combinations of characters that could phonetically match the given text.")
    P.add_argument("--outfile", "-o", default="", 
                   help="--outfile [file]. Specify an output file.  Prints to stdout if not specified.")
    P.add_argument("--show-langs", action="store_true", default=False,
                   help="Print supported languages and exit.")
    args = P.parse_args()
    
    if args.show_langs == True:
        print("""Available languages:
        Hittite  (hit)
        Akkadian (akk)
        Sumerian (sux)
        
        Leave --lang argument blank to disregard the language of a sign.""")
        exit()
    
    if args.lang is not None and args.lang.lower() not in ["hit", "akk", "sux"]:
        raise ValueError("--lang {}: invalid language code.  Use --show-langs to see supported languages.")
    
    # Load the mappings
    l = pickle.load(open("signs.p", "rb"))
    d = [{i[0]:i[1:] for i in j} for j in l]
    
    # Gather text
    text = ""
    if args.file and args.stdin == False:
        for i in args.file.split(" "):
            text += open(i, "r", encoding="utf8").read()
    if args.text and args.stdin == False:
        text += args.text
    if args.stdin == True:
        text = stdin.readline().strip()
    
    # Line tokenize and character tokenize the text
    text = [re.split("[\s\-\[\]\\\\/]+", i) for i in text.split('\n')]
    
    # Check for --showall/-a
    if args.showall == True:
        # Flatten text, so it's no longer split by lines
        text = [i for j in text for i in j]
        text_new = dictmap_findall(text, l)
        # rebind print() to pprint() to make displaying the dictionary nicer.
        print = pprint
    else:
        text_new = "\n".join(dictmap(i, d) for i in text)
    
    if args.outfile != "":
        print(text_new, file=open(args.outfile, "a", encoding="utf8"))
#        with open(args.outfile, "a", encoding="utf8") as F:
#            F.write(text_new + '\n')
    else:
        print(text_new)
