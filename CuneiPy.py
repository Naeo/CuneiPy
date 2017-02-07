#!/usr/bin/python3
"""
This is a program to re-implement Steve Tinney's
Cuneify program, hosted at:
    http://oracc.museum.upenn.edu/saao/knpp/cuneiformrevealed/cuneify/index.html
"""

import argparse
from pprint import pprint
import pickle
import re
from sys import stdin

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
        
def dictmap_findall(row, m):
    """A version of dictmap, but rather than using
    a dictionary, it uses a list of tuples.  This allows
    multiple sign readings to be preserved, and this function
    is only used with the --showall/-a flag due to much
    larger computational overhead.
    """
    new_row = ""
    for i in row:
        if len(i) > 1 and i[-1] in "!#*?":
            i = i[:-1]
        i = i.strip()
        i = i.strip("[]()/\\")
        # look for unicode first, then ascii, then nocomma, then same order
        # with case swapped
        tmp_vals = [[j for j in M if j[0] == i] for M in m]
        # check for sign names
        tmp_vals += [[j for j in M if j[1] == i] for M in m]
        # check swapped case
        tmp_vals += [[j for j in M if j[0] == i] for M in m]
        for tmp in tmp_vals:
            if tmp != []:
                i = tmp[0][2]
                break
        new_row += i + ' '
    return new_row

def showall(row, m):
    """Returns all possible characters that could phonetically match each input segment
    of row.
    """
    found = []
    for i in row:
        found += [i, sorted(set([tuple(j) for j in m if re.match("{}[0-9x]*$".format(i), asciify(j[0]), re.IGNORECASE)]))]
    return found

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
    P.add_argument("--outfile", "-o", default="", 
                   help="--outfile [file]. Specify an output file.  Prints to stdout if not specified.")
    P.add_argument("--allsigns", "-a", action="store_true", default=False, 
                   help="Show all combinations of characters that could phonetically match the given text.")
    args = P.parse_args()
    # Gather text
    text = ""
    if args.file and args.stdin == False:
        for i in args.file.split(" "):
            text += open(i, "r", encoding="utf8").read()
    if args.text and args.stdin == False:
        text += args.text
    if args.stdin == True:
        text = stdin.readline().strip()
    
    l = pickle.load(open("signs.p", "rb"))
    d = [{i[0]:i[1:] for i in j} for j in l]
    text = [re.split("[\s\-\[\]\\\\/]+", i) for i in text.split('\n')]
    if args.allsigns == True:
        text_new = [showall(i, d[0]) for i in text]
    else:
        text_new = "\n".join(dictmap(i, d) for i in text)
    if args.outfile != "":
        with open(args.outfile, "a", encoding="utf8") as F:
            F.write(text_new + '\n')
    else:
        pprint(text_new)
