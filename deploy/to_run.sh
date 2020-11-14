#!/bin/bash
sudo PKG_CONFIG_PATH="/home/ubuntu/pkg_config_path"\
    KALDI_ROOT=/opt/kaldi\
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${KALDI_ROOT}/src/lib:${KALDI_ROOT}/tools/openfst/lib\
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${KALDI_ROOT}:${KALDI_ROOT}/tools/openfst/lib\
    LD_PRELOAD=/opt/intel/mkl/lib/intel64/libmkl_def.so:/opt/intel/mkl/lib/intel64/libmkl_avx2.so:/opt/intel/mkl/lib/intel64/libmkl_core.so:/opt/intel/mkl/lib/intel64/libmkl_intel_lp64.so:/opt/intel/mkl/lib/intel64/libmkl_intel_thread.so:/opt/intel/lib/intel64_lin/libiomp5.so\
    PYTHONPATH=${PYTHONPATH}:/home/ubuntu/dist-packages/lib/python3.6/site-packages/ \
    /home/ubuntu/deploy/kaldi_server.py > /tmp/cs0.log 2>&1 &

