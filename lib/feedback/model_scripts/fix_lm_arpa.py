import os
import shutil
import subprocess

query_command = "utils/format_lm.sh $dict $lm_src.gz $dict_src/lexicon.txt $lang 2>&1 | grep Invalid | awk '{print $4}'"
output_model = "new/local/lang/lm.arpa"
gzip_command = "gzip " + output_model + " " + output_model + ".gz"
compile_command = "utils/format_lm.sh $dict $lm_src.gz $dict_src/lexicon.txt $lang"
HCLG_graph_command = "utils/mkgraph.sh --self-loop-scale 1.0 $lang $model $graph"
prep_decode_command = "steps/online/nnet3/prepare_online_decoding.sh --mfcc-config conf/mfcc_hires.conf $dict exp/nnet3/extractor exp/chain/tdnn_7b new"

model = open("lm.arpa", "r")
lines = model.readlines()
model.close()

LEXICON_ENV = {}
LEXICON_ENV.update(os.environ)
LEXICON_ENV["model"] = "exp/tdnn_7b_chain_online"
LEXICON_ENV["phones_src"] = "exp/tdnn_7b_chain_online/phones.txt"
LEXICON_ENV["dict_src"] = "new/local/dict"
LEXICON_ENV["lm_src"] = "new/local/lang/lm.arpa"

LEXICON_ENV["lang"] = "new/lang"
LEXICON_ENV["dict"] = "new/dict"
LEXICON_ENV["dict_tmp"] = "new/dict_tmp"
LEXICON_ENV["graph"] = "new/graph"

shutil.copy("lm.arpa", output_model)

ngram_3_query = "grep -n \"3-gram\" " + output_model
p = subprocess.Popen(ngram_3_query, shell=True,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=LEXICON_ENV)
output, err = p.communicate()
if p.returncode != 0:
    print("ERROR:", p.returncode)
    print(err.decode("utf-8"))
output = output.decode("utf-8")
ignore_gram3 = int(output.split(":")[0])

del lines[ignore_gram3:]
target_file = open(output_model, "w")
lines.append("\\end\\\n")
for line in lines:
    target_file.write(line)
target_file.close()

try:
    while True:
        if os.path.exists(output_model + ".gz"):
            os.remove(output_model + ".gz")

        p = subprocess.Popen(query_command, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=LEXICON_ENV)
        _, err = p.communicate()
        if p.returncode != 0:
            print("ERROR:", p.returncode)
            print(err.decode("utf-8"))

        p = subprocess.Popen(gzip_command, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=LEXICON_ENV)
        _, err = p.communicate()
        if p.returncode != 0:
            print("ERROR:", p.returncode)
            print(err.decode("utf-8"))

        p = subprocess.Popen(query_command, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=LEXICON_ENV)
        output, err = p.communicate()
        if p.returncode != 0:
            print("ERROR:", p.returncode)
            print(err.decode("utf-8"))

        invalid_line = int(output)
        print("Invalid line:", invalid_line, "of ", len(lines), "lines.")
        del lines[invalid_line - 1]

        target_file = open(output_model, "w")
        for line in lines:
            target_file.write(line)
        target_file.close()

        p = subprocess.Popen("wc " + output_model, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=LEXICON_ENV)
        output, err = p.communicate()
        if p.returncode != 0:
            print("ERROR:", p.returncode)
            print(err.decode("utf-8"))
        print(output.decode("utf-8"))
except ValueError:
    pass

p = subprocess.Popen(compile_command, shell=True,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=LEXICON_ENV)
_, err = p.communicate()
if p.returncode != 0:
    print("ERROR:", p.returncode)
    print(err.decode("utf-8"))

p = subprocess.Popen(HCLG_graph_command, shell=True,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=LEXICON_ENV)
_, err = p.communicate()
if p.returncode != 0:
    print("ERROR:", p.returncode)
    print(err.decode("utf-8"))

p = subprocess.Popen(prep_decode_command, shell=True,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=LEXICON_ENV)
_, err = p.communicate()
if p.returncode != 0:
    print("ERROR:", p.returncode)
    print(err.decode("utf-8"))

print("SUCCESSFUL!")

# steps/online/nnet3/prepare_online_decoding.sh --mfcc-config conf/mfcc_hires.conf $dict exp/nnet3/extractor exp/chain/tdnn_7b new
