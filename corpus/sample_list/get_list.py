#! /usr/bin/python
# -*- coding: utf-8 -*-

 ## diffファイルから、対象のファイル名だけを抽出する

import sys

def getter():
	for line in sys.stdin:
		if line.startswith("# S-ID"):
			print line.strip("\n").split(" ")[2]

if __name__ == "__main__":
	getter()
