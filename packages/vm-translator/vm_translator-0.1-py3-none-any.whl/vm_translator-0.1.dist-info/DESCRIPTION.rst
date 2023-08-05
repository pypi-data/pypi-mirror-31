VM Translator
==============

Translates a file containing VM (Virtual Machine) commands into a Hack assembly
language file. The VM specification can can be found in the section 7.2 of
Nisan, Noam. “The Elements of Computing Systems: Building a Modern Computer
from First Principles.”

Usage
-----

The assembler can be invoked via command line with the command:

``vm-translator fileName.vm``

, where the string fileName.vm is the translator’s input, i.e. the name of a
text file containing VM commands. The translator creates an output text file
named fileName.asm, containing Hack assembly commands. The output file is
stored in the same directory of the input file. The name of the input file may
contain a file path.

Reference
---------

http://www.nand2tetris.org/07.php


