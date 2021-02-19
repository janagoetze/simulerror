#!/usr/bin/env bash
mkdir -p RESOURCES/Lexica/

echo Downloading lexicon data
cd RESOURCES/Lexica/

echo Downloading Norwegian
wget -q --show-progress http://www.nb.no/sbfil/leksikalske_databaser/leksikon/no.leksikon.tar.gz
gunzip no.leksikon.tar.gz
tar -xvf no.leksikon.tar
mv 'NSTs norske leksikon/nor030224NST.pron/nor030224NST.pron' nor030224NST.pron
rm no.leksikon.tar
rm -r 'NSTs norske leksikon'

echo Downloading Swedish
wget -q --show-progress http://www.nb.no/sbfil/leksikalske_databaser/leksikon/sv.leksikon.tar.gz
gunzip sv.leksikon.tar.gz
tar -xvf sv.leksikon.tar
mv 'NST svensk leksikon/swe030224NST.pron/swe030224NST.pron' swe030224NST.pron
rm sv.leksikon.tar
rm -r 'NST svensk leksikon'

echo Downloading English
wget -q --show-progress http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b
