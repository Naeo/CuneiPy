# CuneiPy
Python standalone re-implementation of Steve Tinney's Cuneify tool, found here: https://github.com/oracc/oracc/blob/1c27d9cda5bb83f0f827ee33d66e48fbdbda2ae0/c/otf/gdl/cuneify.c

Web interface here: http://oracc.museum.upenn.edu/doc/tools/cuneify/index.html

## dictbuilder.py
Creates a .p file with a list of dictionaries that map transliterations to Unicode cuneiform symbols.  Each dictionary contains a different transliteration scheme: Unicode-compliant, ASCII-compliant, and ASCII-compliant without commas, where commas do not disambiguate different values.

To use: Download ORACC's XML sign list (https://github.com/oracc/coredata/tree/master/sign) to the same folder as dictbuilder.py, and run dictbuilder.py.

### CuneiPy.py
Does the main transcription.  This is designed to be run from the command line.

Usage:
python3 CuneiPy.py [--file inputfile] [--text text] [--stdin] [--showall] [--outfile file]

--file, -f          Specify a text file containing ATF transliterations to convert to Cuneiform.

--outfile, -o       Specify a destination file to append results to.  If not supplied, results are printed to stdout.

--text, -t          Manually supply text to transliterate as an argument.  If used with -f, text in file is processed first.

--stdin, -s         Read transliteration from stdin.  Mostly useful for piping output from another program through.

--showall, -a       Show all symbols that could be read as the target text.  E.g., "du" will return "du1", "du2", etc.  
                    [Currently a bit buggy]
