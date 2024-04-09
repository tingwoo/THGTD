#!/bin/bash

# Define the index array
index=(90 148 42 40 36 4 3 159 24 70 134 100 103 55 112 86 116 13 111 94 146 58 140 30 48 99 98 26 107 9 106 145 74 150 20 14 92 53 156 135 44 22 10 72 108 130 60 80 21 131 66 104 19 136 141 105 77 27 120 102 138 15 7 51 152 157 17 78 43 18 85 75 147 76 114 127 122 89 91 2 143 113 52 151 84 129 34 50 83 6 41 144 142 25 101 87 117 38 71 67 47 68 158 125 93 11 49 0 123 69 63 137 32 33 132 96 110 121 46 35 28 149 59 56 73 81 82 153 45 37 61 118 109 155 39 154 126 29 5 64 133 54 57 16 12 65 31 128 124 79 119 23 97 1 139 95 115 62 8 88)

# Define the start and end of the loop
a=1
b=3

# Loop from a to b
for ((i=a; i<=b; i++))
do
    idx=${index[$((i-1))]}
    python generate.py --talknet_folder_root /Users/ericsunkuan/Desktop/NTUEE/112-2/ML/meeting_data_collect/TalkNet-ASD-main/demo/$i --audio_folder_root /Users/ericsunkuan/Desktop/NTUEE/112-2/ML/meeting_data_collect/seperate_results/output/separated/preprocessed/$(printf "%04d" $idx) --id $i --spk_datajson_path /Users/ericsunkuan/Desktop/NTUEE/112-2/ML/meeting_data_collect/seperate_results/output/spk_data.json --spk_id $idx
done