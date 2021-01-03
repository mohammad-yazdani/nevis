cd /opt/kaldi/egs/vystadial_en/s5/common

grep -oE "[A-Za-z\\-\\']{3,}" /tmp/results/aspire/0/0/trans | tr '[:lower:]' '[:upper:]' | sort | uniq > words.txt

g2p.py --train cmudict.ext --devel 5% --write-model model-1
 
g2p.py --train cmudict.ext --devel 5% --write-model model-1
g2p.py --model model-1 --test cmudict.ext > model-1-test
 
g2p.py --model model-1 --ramp-up --train cmudict.ext --devel 5% --write-model model-2
g2p.py --model model-2 --test cmudict.ext > model-2-test
 
g2p.py --model model-2 --ramp-up --train cmudict.ext --devel 5% --write-model model-3
g2p.py --model model-3 --test cmudict.ext > model-3-test
 
g2p.py --model model-3 --ramp-up --train cmudict.ext --devel 5% --write-model model-4
g2p.py --model model-4 --test cmudict.ext > model-4-test
 
g2p.py --model model-4 --ramp-up --train cmudict.ext --devel 5% --write-model model-5
g2p.py --model model-5 --test cmudict.ext > model-5-test
 
g2p.py --model model-5 --ramp-up --train cmudict.ext --devel 5% --write-model model-6
g2p.py --model model-6 --test cmudict.ext > model-6-test
 
g2p.py --model model-6 --ramp-up --train cmudict.ext --devel 5% --write-model model-7
g2p.py --model model-7 --test cmudict.ext > model-7-test

g2p.py --model model-7 --apply words.txt > words.dic

cat /tmp/results/aspire/0/0/trans | tr '[:lower:]' '[:upper:]' > trans_upper

/usr/share/srilm/bin/i686-ubuntu/ngram-count -text trans_upper -order 3 -limit-vocab -vocab words.txt -unk -map-unk "" -wbdiscount -interpolate -lm lm.arpa

./merge.py /workspace/models/aspire/data/local/dict/lexicon4_extra.txt /workspace/models/aspire/data/local/lm/3gram-mincount/lm_unpruned words.dic lm.arpa merged-lexicon.txt merged-lm.arpa


mkdir -p new/local/dict
cp /workspace/models/aspire/data/local/dict/* new/local/dict/
cp merged-lexicon.txt new/local/dict/lexicon.txt
mkdir -p new/local/lang
cp lm.arpa new/local/lang/

cd /workspace/models/aspire

# Set up the environment variables (again)
. cmd.sh
. path.sh
 
# Set the paths of our input files into variables
model=exp/tdnn_7b_chain_online
phones_src=exp/tdnn_7b_chain_online/phones.txt
dict_src=new/local/dict
lm_src=new/local/lang/lm.arpa
 
lang=new/lang
dict=new/dict
dict_tmp=new/dict_tmp
graph=new/graph
 
# Compile the word lexicon (L.fst)
utils/prepare_lang.sh --phone-symbol-table $phones_src $dict_src "" $dict_tmp $dict
 
# Compile the grammar/language model (G.fst)
gzip  $lm_src.gz
utils/format_lm.sh $dict $lm_src.gz $dict_src/lexicon.txt $lang
 
# Finally assemble the HCLG graph
utils/mkgraph.sh --self-loop-scale 1.0 $lang $model $graph
 
# To use our newly created model, we must also build a decoding configuration, the following line will create these for us into the new/conf directory
steps/online/nnet3/prepare_online_decoding.sh --mfcc-config conf/mfcc_hires.conf $dict exp/nnet3/extractor exp/chain/tdnn_7b new

# Release new training
RETRAINED_MODEL_PATH=/workspace/models/aspire/retrained
mkdir -p $RETRAINED_MODEL_PATH
cp /workspace/models/aspire/new/graph/words.txt $RETRAINED_MODEL_PATH
cp /workspace/models/aspire/new/conf/online.conf $RETRAINED_MODEL_PATH
cp /workspace/models/aspire/exp/tdnn_7b_chain_online/final.mdl $RETRAINED_MODEL_PATH
cp /workspace/models/aspire/new/graph/HCLG.fst $RETRAINED_MODEL_PATH

