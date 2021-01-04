#!/usr/bin/bash

poll_trans () {
    sleep 1

    local lk_batch_id=$(jq '.batch_id' $1.json)
    local lk_corpus_id=$(jq '.corpus_id' $1.json | tr -d '"')

    local local_batch_id=$lk_batch_id
    local local_corpus_id=$lk_corpus_id

    echo "$local_batch_id $local_corpus_id"

    echo "http 0.0.0.0:8080/get_transcript batch_id==$local_batch_id corpus_id==$local_corpus_id"
    local local_callback=$(http 0.0.0.0:8080/get_transcript batch_id==$local_batch_id corpus_id==$local_corpus_id)
    echo $local_callback
    local_complete=$(echo $local_callback | jq '.complete' | tr -d '"')
    while [ $local_complete != "1" ]; do
        sleep 5
        local_callback=$(http 0.0.0.0:8080/get_transcript batch_id==$local_batch_id corpus_id==$local_corpus_id) 
        local_complete=$(echo $local_callback | jq '.complete' | tr -d '"')
    done
}

submit_audio () {
    http 0.0.0.0:8080/transcribe_file < $1 > $1.json
    echo $1.json
    # local lk_batch_id=$(jq '.batch_id' $1.json)
    # local lk_corpus_id=$(jq '.corpus_id' $1.json | tr -d '"')
    # poll_trans $lk_batch_id $lk_corpus_id &
}

audio_data=(
    /root/audio/raw_audio/17_The_Peloponnesian_War_Part_I.wav
    /root/audio/raw_audio/27_Vibration_of_Continuous_Structures_Strings_Beams_Rods_etc.wav
    /root/audio/raw_audio/30_Activation_Functions_Softmax_Activation_Detail_Explanation.wav
    /root/audio/raw_audio/Aalto_Talk_with_Linus_Torvalds.wav
)

audio_data2=(
    /root/audio/raw_audio/DODGE_HEMI_-_Everything_You_Need_To_Know__Up_To_Speed.wav
    /root/audio/raw_audio/How_Many_Holes_Does_a_Human_Have.wav
    /root/audio/raw_audio/Least_Recently_Used__Page_Replacement_Algorithm__Operating_System.wav
    /root/audio/raw_audio/Lecture_1_Introduction_to_Power_and_Politics_in_World.wav
    /root/audio/raw_audio/Matrix_vector_products__Vectors_and_spaces__Linear_Algebra__Khan_Academy.wav
    /root/audio/raw_audio/The_LG_Wing_is_Like_No_Other_Smartphone.wav
    /root/audio/raw_audio/The_W12_Engine_-_The_Science_EXPLAINED.wav
    /root/audio/raw_audio/rec05.wav
)

for i in "${audio_data[@]}";
do
    submit_audio $i
done


for i in "${audio_data2[@]}";
do
    submit_audio $i
    sleep $((RANDOM % 20))
done

