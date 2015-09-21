#! bin/sh

usage_exit() {
    echo "Usage: $0 [-d dir] [-c corpus]" 1>&2
    exit 1
}

FOLD=10
DIR=`date '+%Y%m%d%H%m'`

# options:
# d -- directory
# c -- corpus
# k -- validation fold
while getopts d:c:k:h OPT
do
    case $OPT in
        d) FLG_D="TRUE"; DIR="$OPTARG" ;;
        c) FLG_C="TRUE"; CORPUS="$OPTARG" ;;
        k) FLG_K="TRUE"; FOLD="$OPTARG" ;;
        h) usage_exit ;;
        \?) usage_exit ;;
    esac
done

if [ "$FLG_C" != "TRUE" ]; then
    echo "$0 requires -c option"; usage_exit
fi

## 作業ディレクトリの作成
mkdir $DIR
cd $DIR
mkdir dataset; dataset=${DIR}/dataset
mkdir features; features=${DIR}/features
mkdir model; model=${DIR}/model
mkdir tagged; tagged=${DIR}/tagged
cd ..

## データの分割
#python scripts/split.py ${CORPUS} ${DIR}/

## 素性抽出
#echo -n Extracting features...
#for index in `seq 0 9`
#    do
#        python scripts/feature.py ${CORPUS} < ${dataset}/${index} > ${features}/${index}.f
#        echo -n "${index} "
#    done
#echo done

### Cross-validate with CRFSuite, storing resulted tags into tagged directory.
echo -n Running cross validation...
for test in `seq 0 9`
do
    trains=()
    for train in `seq 0 9`
    do
        if [ $test -ne $train ] ; then
            trains+=(${features}/${train}.f)
        fi
    done
    cat "${trains[@]}" | /usr/local/bin/crfsuite learn -m ${model}/${test}.m - > logs
    /usr/local/bin/crfsuite tag -r -m ${model}/${test}.m < ${features}/${test}.f > ${tagged}/${test}.t
    echo -n "${test} "
done
echo done

### Make data for evaluation, writing result as crf.eval.
##python data4eval.py $corpus $tagged/ > $dir/crf.eval
#
### Evaluate Eval.py.
##python ../lib/Eval.py < $dir/crf.eval
