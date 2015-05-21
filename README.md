# SIMPLE
This is a python3 version of [SIMPLE](http://plata.ar.media.kyoto-u.ac.jp/mori/research/) input method.

###Training
		kkc.py ../corpus/L.wordkkci < ../corpus/T.kkci

### Evaluation
		bin/accuracy.py T.conv T.sent
		
### TODO
- Implementation of n-gram model combined with smoothing techniques(such as KN smoothing)
- k-best
