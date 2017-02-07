"""
This is a one-time-run file to generate a Python dictionary
for looking up transliterated signs and their corresponding
Unicode codepoints.  It uses the xml file provided by ORACC,
and riginally created by Steve Tinney:
    https://github.com/oracc/coredata/blob/master/sign/ogsl-sl.xml
"""

import pickle
from pprint import pprint
import sys
import xml.etree.ElementTree as ET

def fixer(string):
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

if __name__ == "__main__":
    f = ET.parse("prettify.txt")
    root = f.getroot()
    # namespace strings
    xml = "{http://www.w3.org/XML/1998/namespace}"
    g = "{-}"
    s = "{-}"
    xmlns = "{}"
    sign_data = [["value", "form", "character", "language"]]
    cur_items = []
    cur_form = ""
    cur_var = ""
    cur_lang = ""
    cur_literal = ""
    cur_vals = []
    for i in root.getiterator():
        if i.tag == "{-}w":
            # pull form and lang information from <g:w>
            cur_form = i.get("form")
            cur_lang = i.get("{}lang".format(xml)) # namespace stuff in XML
        elif i.tag == "utf8":
            # pull literal cuneiform from <g:s>, <g:c>
            cur_literal = i.text.strip()
        elif i.tag in ["list", "v"]:
            # pull sign values from <list>, <v>
            cur_vals.append(i.get("n"))
        elif i.tag in ["sign", "form"]:
            # end of block, update dict and start again
            sign_data += [[i+cur_var, cur_form, cur_literal, cur_lang] for i in cur_vals]
            cur_form = ""
            cur_var = i.get("var", "")
            cur_lang = ""
            cur_literal = ""
            cur_vals = []
    # remove signs with no unicode symbol
    sign_data = [i for i in sign_data if i[2] not in [None, "X", ""]]
    with open("signs.txt", "w") as F:
        for line in sign_data:
            F.write("{0:20s}\t{1:20s}\t{2:20s}\t{3:<20s}".format(*line) + '\n')
                
    signs = [sign_data[:], sign_data[:], sign_data[:]]
    for i in range(len(signs[1])):
        # ascii-fy all the characters we can
        signs[1][i][0] = fixer(signs[1][i][0])
        # remove commas where redundant/unnecessary
        for j in "cCtThHjJX()[]":
            signs[2][i][0] = signs[2][i][0].replace(j+',', j)
    
    pickle.dump(signs, open("signs.p", "wb"))
