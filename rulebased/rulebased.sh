#! /bin/sh

#オプション
#corpus=../data/JFEcorpus_ver2.0_append/
corpus=../data/JFEcorpus_ver2.1/
felist=fe_list
crlist=cr_list
ttjdict=ttj_dict.kch
fedict=fe_dict.kch
crdict=cr_dict.kch
ttjsrc=../src/ttj11core2seq

cd scripts
#
#----- つつじ辞書 -----
# echo -n constructing Tsustuji dictionary...
# python fe_db_builder.py ../$ttjdict --src=../$ttjsrc
# echo done
#
#----- 追加機能表現探索 -----
# echo -n searching new entries...
# python additional_entries.py ../$corpus ../$felist ../$crlist
# echo done
#
#----- 追加機能表現辞書 -----
# echo -n constructing FE dictionary...
# python fe_db_builder.py ../$fedict --src=../$ttjsrc --add=../$felist
# echo done
#
#----- 接続制約辞書 -----
# echo -n constructing Connect Rule dictionary...
# python cr_db_builder.py ../$crdict --add=../$crlist
# echo done
#
#----- 頻度情報 -----
# echo -n get frequency information...
# python Mostfreq.py -d > ../most_freq
# echo done

#----- 解析 -----
echo -n labeling...
#python rulebased.py ../$corpus ../$fedict ../$crdict #> ../rulebased_ver2.1_all_sent.eval
python rulebased2.py ../$corpus ../$fedict ../$crdict
echo done

cd ..

#----- 評価 -----
#python ../lib/Eval.py < rulebased_ver2.1_all_sent.eval
