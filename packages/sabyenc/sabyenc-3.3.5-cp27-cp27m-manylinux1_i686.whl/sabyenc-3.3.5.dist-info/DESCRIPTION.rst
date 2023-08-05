yEnc Decoding for Python
---------------------------------

Mofied the original yenc module by Alessandro Duca for use within SABnzbd.

The module was extended to do header parsing and full yEnc decoding from a Python
list of chunks, the way in which data is retrieved from usenet.

Currently CRC-checking of decoded data is disabled to allow for increased performance.
It can only be re-enabled by locally altering 'sabyenc.h' and setting 'CRC_CHECK 1'.


