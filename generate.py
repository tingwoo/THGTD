from integrator import Integrator
from pydub import AudioSegment
import os

def translate_video_json(data):
    new_data = []
    for i, spk in enumerate(data['time']):
        for segment in spk:
            new_data.append({ 'spk': f'0000{i}', 'start': int(segment[0]*1000), 'end': int(segment[1]*1000) })
    return new_data

def split_audio_channels(src_path, res_dir_path):
    # Split stereo into mono
    stereo_audio = AudioSegment.from_file(src_path)

    left_channel = stereo_audio.split_to_mono()[0]
    right_channel = stereo_audio.split_to_mono()[1]

    os.makedirs(res_dir_path, exist_ok=True)

    left_channel.export(os.path.join(res_dir_path, "SPEAKER_00.wav"), format="wav")
    right_channel.export(os.path.join(res_dir_path, "SPEAKER_01.wav"), format="wav")


talknet_input = {
    "videoname": "0000",
    "speakers": 2,
    "time": [
        [
            [
                3.08,
                8.92
            ],
            [
                17.16,
                17.56
            ],
            [
                18.0,
                26.48
            ],
            [
                36.08,
                40.0
            ],
            [
                45.76,
                50.08
            ]
        ],
        [
            [
                0.96,
                2.04
            ],
            [
                2.6,
                2.8
            ],
            [
                9.2,
                16.88
            ],
            [
                27.0,
                36.04
            ],
            [
                40.96,
                45.56
            ]
        ]
    ]
}

seperate_input = [
    {
        "spk": "SPEAKER_00",
        "start": 31,
        "end": 2933
    },
    {
        "spk": "SPEAKER_01",
        "start": 3153,
        "end": 8755
    },
    {
        "spk": "SPEAKER_00",
        "start": 9110,
        "end": 16822
    },
    {
        "spk": "SPEAKER_01",
        "start": 17159,
        "end": 26322
    },
    {
        "spk": "SPEAKER_00",
        "start": 26710,
        "end": 36683
    },
    {
        "spk": "SPEAKER_01",
        "start": 36683,
        "end": 39856
    },
    {
        "spk": "SPEAKER_00",
        "start": 40801,
        "end": 46977
    },
    {
        "spk": "SPEAKER_01",
        "start": 46977,
        "end": 49964
    },
    {
        "spk": "SPEAKER_00",
        "start": 48901,
        "end": 48968
    }
]

# Translate Talknet output
talknet_input = translate_video_json(talknet_input)

# split stereo into mono
split_audio_channels(src_path="source/0000_audio_stereo.wav", res_dir_path="source/0000_audio")

# Match, select segments and cut
# only TWO speakers are allowed (for now)

# INPUTS
# id:             Output folder name
# video_json:     [{'spk': 'spkA', 'start': 15, 'end': 1270}, {'spk': 'spkB', 'start': 1240, 'end': 3535}, ...]
# audio_json:     [{'spk': 'spk1', 'start': 10, 'end': 1200}, {'spk': 'spk2', 'start': 1250, 'end': 3600}, ...]
# video_src_path: Folder containing cropped video files from a certain video (00000.avi and 00001.avi)
# audio_src_path: Folder containing seperated audio files from a certain audio (e.g. 'SPEAKER_00.mp3', 'SPEAKER_01.mp3')

integrator = Integrator(
    id='0000',
    video_json=talknet_input, 
    audio_json=seperate_input, 
    video_src_path='source/0000_video', 
    audio_src_path='source/0000_audio'
)

# INPUTS
# target_face:    video speaker you want to match.
# at_most:        number of output clips
# length:         output clip length
# i_threshold:    "Interactivity" threshold. Integrator will only choose segments where abs(speaker1_length - speaker2_length) / length < threshold
# a_threshold:    "Activity" threshold.      Integrator will only choose segments where talking_length / length > threshold
# visualize:      To display plot or not

integrator.generate_data(
    target_face='00000', 
    at_most=10, 
    length=8000, 
    i_threshold=0.1, 
    a_threshold=0.7, 
    visualize=True
)

integrator.generate_data(
    target_face='00001', 
    at_most=10, 
    length=8000, 
    i_threshold=0.1, 
    a_threshold=0.7, 
    visualize=True
)