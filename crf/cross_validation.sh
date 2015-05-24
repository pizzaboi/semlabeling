#! bin/sh

## Parse arguments. This script does not parse currently.
dir=ver2.1_allsent
corpus=../data/JFEcorpus_ver2.1/
fold=10

## Make directory for working, separated data, extracted features, learned models, tags from CRFSuite.
mkdir $dir
cd $dir
mkdir dataset
mkdir features
mkdir model
mkdir tagged
cd ..

dataset=${dir}/dataset
features=${dir}/features
model=${dir}/model
tagged=${dir}/tagged

## Split data for cross-validation, storing list of splitted files into dataset directory.
python split.py ${corpus} ${dir}/

## Extract features from each dataset in dataset directory, storing features into fetures directory.
echo -n Extracting features...
for index in `seq 0 9`
    do
        python feature.py ${corpus} -o < ${dataset}/${index} > ${features}/${index}.f
        echo -n "${index} "
    done
echo done

## Cross-validate with CRFSuite, storing resulted tags into tagged directory.
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
    cat "${trains[@]}" | crfsuite learn -m ${model}/${test}.m - > logs
    crfsuite tag -r -m ${model}/${test}.m < ${features}/${test}.f > ${tagged}/${test}.t
    echo -n "${test} "
done
echo done

## Make data for evaluation, writing result as crf.eval.
python data4eval.py $corpus $tagged/ > $dir/crf.eval

## Evaluate Eval.py.
python ../lib/Eval.py < $dir/crf.eval
