import os
import subprocess
import shutil

query_command = "utils/prepare_lang.sh --phone-symbol-table $phones_src $dict_src \"\" $dict_tmp $dict | grep \"ERROR:\" | awk '{print $4}' | grep \\\""
src_file = "new/local/dict/lexicon.txt"
backup_file = "new/local/dict/backup_lexicon.txt"
temp_file = "/tmp/lex.tmp"

shutil.copy(src_file, backup_file)

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

p = subprocess.Popen(query_command, shell=True,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=LEXICON_ENV)
output, err = p.communicate()

tks = output.decode("utf-8").split()
tokens = []
for tk in tks:
    tk = tk.replace("'", "").replace("\"", "")
    tokens.append(tk)

shutil.copy(src_file, temp_file)

for token in tokens:
    sed_command = "sed -e '/" + token + "/d' " + temp_file
    p = subprocess.Popen(sed_command, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, env=LEXICON_ENV)
    output, err = p.communicate()
    # os.remove(temp_file)
    fd = open(temp_file, "w")
    fd.write(output.decode("utf-8"))
    fd.close()

shutil.copy(temp_file, src_file)
