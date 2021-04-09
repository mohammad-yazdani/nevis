#!/usr/bin/bash

COMMANDS_PHASE0=(
  "g2p.py --train cmudict --devel 5% --write-model model-1"

  # "g2p.py --train cmudict --devel 5% --write-model model-1"
  # "g2p.py --model model-1 --test cmudict > model-1-test"

  # "g2p.py --model model-1 --ramp-up --train cmudict --devel 5% --write-model model-2"
  # "g2p.py --model model-2 --test cmudict > model-2-test"

  # Milestone

  # "g2p.py --model model-2 --ramp-up --train cmudict --devel 5% --write-model model-3"
  # "g2p.py --model model-3 --test cmudict > model-3-test"

  # "g2p.py --model model-3 --ramp-up --train cmudict --devel 5% --write-model model-4"
  # "g2p.py --model model-4 --test cmudict > model-4-test"

  # "g2p.py --model model-4 --ramp-up --train cmudict --devel 5% --write-model model-5"
  # "g2p.py --model model-5 --test cmudict > model-5-test"

  # "g2p.py --model model-5 --ramp-up --train cmudict --devel 5% --write-model model-6"
  # "g2p.py --model model-6 --test cmudict > model-6-test"

  # "g2p.py --model model-6 --ramp-up --train cmudict --devel 5% --write-model model-7"
  # "g2p.py --model model-7 --test cmudict > model-7-test"

  # MAIN
  # "g2p.py --model model-2 --apply words.txt > words.dic"
  # TEST-FAST
  # "g2p.py --model model-1 --apply words.txt > words.dic"
)

COMMANDS_PHASE01=(
  # "cat corpus.txt | tr '[:lower:]' '[:upper:]' > corpus_upper.txt"

  # "/usr/share/srilm/bin/i686-ubuntu/ngram-count -text corpus_upper.txt -order 3 -limit-vocab -vocab words.txt -unk -map-unk \"\" -wbdiscount -interpolate -lm lm.arpa"
  # "/workspace/srilm/bin/i686-ubuntu/ngram-count -text corpus_upper.txt -order 3 -limit-vocab -vocab words.txt -unk -map-unk \"\" -kndiscount -interpolate -lm lm.arpa"
  "rm -rf data/local/lm/3gram-mincount/lm_unpruned"
  "gunzip -k data/local/lm/3gram-mincount/lm_unpruned.gz"
)

COMMANDS_PHASE1=(
  "python mergedicts.py ../data/local/dict/lexicon4_extra.txt ../data/local/lm/3gram-mincount/lm_unpruned words.dic lm.arpa merged-lexicon.txt merged-lm.arpa"
)

COMMANDS_PHASE2=(
  "mkdir -p new/local/dict"
  "cp -rf data/local/dict/* new/local/dict/"
  "cp new/merged-lexicon.txt new/local/dict/lexicon.txt"
  "mkdir -p new/local/lang"
  "cp new/merged-lm.arpa new/local/lang/lm.arpa"

  # Set up the environment variables (again)
  ". cmd.sh"
  ". path.sh"
)

COMMANDS_PHASE3=(
)

date >"/tmp/retrain.log"

# Begin
cd /opt/kaldi/egs/aspire/s5/data/local/dict/cmudict/sphinxdict

for c in "${COMMANDS_PHASE0[@]}"; do
  $c
  if [[ $? -eq 1 ]]; then
    echo "Failed!"
    exit 1
  else
    echo "Success!"
  fi
done

g2p.py --model model-1 --apply words.txt >words.dic
if [[ $? -eq 1 ]]; then
  echo "Failed!"
  exit 1
else
  echo "Success!"
fi
ls

cat corpus.txt | tr '[:lower:]' '[:upper:]' >corpus_upper.txt
if [[ $? -eq 1 ]]; then
  echo "Failed!"
  exit 1
else
  echo "Success!"
fi

/usr/share/srilm/bin/i686-ubuntu/ngram-count -text corpus_upper.txt -order 3 -limit-vocab -vocab words.txt -unk -map-unk \"\" -wbdiscount -interpolate -lm lm.arpa
if [[ $? -eq 1 ]]; then
  echo "Failed!"
  exit 1
else
  echo "Success!"
fi

cd /opt/kaldi/egs/aspire/s5/

for c in "${COMMANDS_PHASE01[@]}"; do
  $c
  if [[ $? -eq 1 ]]; then
    echo "Failed!"
    exit 1
  else
    echo "Success!"
  fi
done

cp /opt/kaldi/egs/aspire/s5/data/local/dict/cmudict/sphinxdict/words.dic /opt/kaldi/egs/aspire/s5/new/
cp /opt/kaldi/egs/aspire/s5/data/local/dict/cmudict/sphinxdict/lm.arpa /opt/kaldi/egs/aspire/s5/new/

cd /opt/kaldi/egs/aspire/s5/new/

for c in "${COMMANDS_PHASE1[@]}"; do
  $c
  if [[ $? -eq 1 ]]; then
    echo "Failed!"
    exit 1
  else
    echo "Success!"
  fi
done

cp /opt/kaldi/egs/aspire/s5/new/lm.arpa /opt/kaldi/egs/aspire/s5/

cd /opt/kaldi/egs/aspire/s5/
for c in "${COMMANDS_PHASE2[@]}"; do
  $c
  if [[ $? -eq 1 ]]; then
    echo $c
    echo "Failed!"
    exit 1
  else
    echo "Success!"
  fi
done

cat new/local/dict/lexicon.txt | awk '$2="1.0 "$2' >new/local/dict/lexiconp.txt
if [[ $? -eq 1 ]]; then
  echo "Failed!"
  exit 1
else
  echo "Success!"
fi

for c in "${COMMANDS_PHASE3[@]}"; do
  $c
  if [[ $? -eq 1 ]]; then
    echo $c
    echo "Failed!"
    exit 1
  else
    echo "Success!"
  fi
done

model=exp/tdnn_7b_chain_online
phones_src=exp/tdnn_7b_chain_online/phones.txt
dict_src=new/local/dict
lm_src=new/local/lang/lm.arpa
lang=new/lang dict=new/dict
dict_tmp=new/dict_tmp
graph=new/graph

# PHASE 3
utils/prepare_lang.sh --phone-symbol-table $phones_src $dict_src "" $dict_tmp $dict | grep "ERROR:" | awk '{print $4}' | grep \"

python3 fix_lexicon.py
if [[ $? -eq 1 ]]; then
  echo "Failed!"
  exit 1
else
  echo "Success!"
fi

cp new/local/dict/lexiconp.txt new/local/dict/backup_lexiconp.txt
if [[ $? -eq 1 ]]; then
  echo "Failed!"
  exit 1
else
  echo "Success!"
fi

utils/prepare_lang.sh --phone-symbol-table $phones_src $dict_src "" $dict_tmp $dict
if [[ $? -eq 1 ]]; then
  echo "Failed!"
  exit 1
else
  echo "Success!"
fi

rm -rf new/local/lang/lm.arpa.gz
if [[ $? -eq 1 ]]; then
  echo "Failed!"
  exit 1
else
  echo "Success!"
fi

cp lm.arpa $lm_src
if [[ $? -eq 1 ]]; then
  echo "cp lm.arpa $lm_src"
  echo "Failed!"
  exit 1
else
  echo "Success!"
fi

gzip $lm_src $lm_src.gz
if [[ $? -eq 1 ]]; then
  echo "gzip $lm_src $lm_src.gz"
  echo "Failed!"
  exit 1
else
  echo "Success!"
fi

utils/format_lm.sh $dict $lm_src.gz $dict_src/lexicon.txt $lang 2>&1 | grep Invalid | awk '{print $4}'

utils/mkgraph.sh --self-loop-scale 1.0 $lang $model $graph
if [[ $? -eq 1 ]]; then
  echo "utils/mkgraph.sh --self-loop-scale 1.0 $lang $model $graph"
  echo "Failed!"
  exit 1
else
  echo "Success!"
fi

steps/online/nnet3/prepare_online_decoding.sh --mfcc-config conf/mfcc_hires.conf $dict exp/nnet3/extractor exp/chain/tdnn_7b new
if [[ $? -eq 1 ]]; then
  echo "steps/online/nnet3/prepare_online_decoding.sh --mfcc-config conf/mfcc_hires.conf $dict exp/nnet3/extractor exp/chain/tdnn_7b new"
  echo "Failed!"
  exit 1
else
  echo "Success!"
fi

# Release new trainingutils/prepare_lang.sh --phone-symbol-table exp/tdnn_7b_chain_online/phones.txt new/local/dict "" new/dict_tmp new/dict | grep "ERROR:" | awk '{print }' | grep "
