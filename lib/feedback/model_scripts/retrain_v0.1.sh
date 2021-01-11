cd /opt/kaldi/egs/vystadial_en/s5/common

# grep -oE "[A-Za-z\\-\\']{3,}" /tmp/results/aspire/0/0/trans_feedback | tr '[:lower:]' '[:upper:]' | sort | uniq > /opt/kaldi/egs/vystadial_en/s5/common/words.txt

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

./merge.py /workspace/models/aspire/data/local/dict/lexicon4_extra.txt /workspace/models/aspire/data/local/lm/3gram-mincount/lm_unpruned words.dic lm.arpa /workspace/models/aspire/merged-lexicon.txt /workspace/models/aspire/merged-lm.arpa
cp -r lm.arpa /workspace/models/aspire/

cd /workspace/models/aspire/

mkdir -p new/local/dict
cp -rf /workspace/models/aspire/data/local/dict/* new/local/dict/
cp -r merged-lexicon.txt new/local/dict/lexicon.txt
mkdir -p new/local/lang
cp -r lm.arpa new/local/lang/

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
# ORIGINAL: utils/prepare_lang.sh --phone-symbol-table $phones_src $dict_src "" $dict_tmp $dict
utils/prepare_lang.sh --phone-symbol-table $phones_src $dict_src "" $dict_tmp $dict | grep "ERROR:" | awk '{print $4}' | grep \"
# Resolve conflicts between lexicon.txt and lexiconp.txt
python3 fix_lexicon.py
# Remove words returned above from new/local/dict/lexicon.txt
cp -r new/local/dict/lexiconp.txt new/local/dict/backup_lexiconp.txt 
cat new/local/dict/lexicon.txt | awk '$2="1.0 "$2' > new/local/dict/lexiconp.txt
# Resolved call
utils/prepare_lang.sh --phone-symbol-table $phones_src $dict_src "" $dict_tmp $dict

# Compile the grammar/language model (G.fst)
# ORIGINAL: gzip  $lm_src.gz
rm -rf new/local/lang/lm.arpa.gz
cp -r lm.arpa $lm_src
gzip $lm_src $lm_src.gz
# ORIGINAL: utils/format_lm.sh $dict $lm_src.gz $dict_src/lexicon.txt $lang
utils/format_lm.sh $dict $lm_src.gz $dict_src/lexicon.txt $lang 2>&1 | grep Invalid | awk '{print $4}'
# TODO : Resolve errors in lm.arpa. While this command returns a number x:
#                                       1. Remove line x from lm.apra
#                                       2. cp lm.arpa $lm_src
#                                       3. gzip $lm_src $lm_src.gz
#                                       4. Retry

# Finally assemble the HCLG graph
utils/mkgraph.sh --self-loop-scale 1.0 $lang $model $graph 
# To use our newly created model, we must also build a decoding configuration, the following line will create these for us into the new/conf directory
steps/online/nnet3/prepare_online_decoding.sh --mfcc-config conf/mfcc_hires.conf $dict exp/nnet3/extractor exp/chain/tdnn_7b new

# Release new training
mkdir -p /workspace/retrained_model/
cp /workspace/models/aspire/new/graph/words.txt /workspace/retrained_model/
cp /workspace/models/aspire/new/conf/online.conf /workspace/retrained_model/
cp /workspace/models/aspire/exp/tdnn_7b_chain_online/final.mdl /workspace/retrained_model/
cp /workspace/models/aspire/new/graph/HCLG.fst /workspace/retrained_model/
