from integrator import Integrator
from pydub import AudioSegment
import os,argparse
import json

def translate_video_json(data):
    new_data = []
    for i, spk in enumerate(data['time']):
        for segment in spk:
            new_data.append({ 'spk': f'0000{i}', 'start': int(segment[0]*1000), 'end': int(segment[1]*1000) })
    return new_data

def split_audio_channels(src_path, res_dir_path, speaker_names):
    # Split stereo into mono
    stereo_audio = AudioSegment.from_file(src_path)

    left_channel = stereo_audio.split_to_mono()[0]
    right_channel = stereo_audio.split_to_mono()[1]

    os.makedirs(res_dir_path, exist_ok=True)

    left_channel.export(os.path.join(res_dir_path, speaker_names[0] + ".wav"), format="wav")
    right_channel.export(os.path.join(res_dir_path, speaker_names[1] + ".wav"), format="wav")

def get_two_speakers(data):
    unique_speakers = []

    for entry in data:
        speaker = entry["spk"]
        if speaker not in unique_speakers:
            unique_speakers.append(speaker)

    if len(unique_speakers) == 2:
        return unique_speakers
    else:
        return []


parser = argparse.ArgumentParser(description = "TalkNet Demo or Columnbia ASD Evaluation")

parser.add_argument('--talknet_folder_root',             type=str, default="001",   help='Demo video name')
parser.add_argument('--audio_folder_root',           type=str, default="demo",  help='Path for inputs, tmps and outputs')
parser.add_argument('--id',           type=int, default=0,  help='Path for inputs, tmps and outputs')
parser.add_argument('--spk_datajson_path',           type=str, default=0)
parser.add_argument('--spk_id',           type=int, default=0)
args = parser.parse_args()

print("video id : ",args.id,", audio id : ",args.spk_id)

talknet_json_path = os.path.join(args.talknet_folder_root,"pywork/data.json")

with open(talknet_json_path, 'r') as f:
    talknet_input = json.load(f)
print(talknet_input)

with open(args.spk_datajson_path, 'r') as f:
    spk_data = json.load(f)

spk_id_padded = "{:04}".format(args.spk_id)
print(spk_id_padded)
print(" ")
for d in (spk_data['wav_files']):
    base_name = os.path.basename(d['file_name'])
    name, ext = os.path.splitext(base_name)
    if(name == spk_id_padded):
        seperate_input = d['data']
        print(seperate_input)
        break

# Make sure seperate output only has 2 speakers
speaker_list = get_two_speakers(seperate_input) 
if not speaker_list:
    print("Not 2 speakers.")
    exit()

# Translate Talknet output
talknet_input = translate_video_json(talknet_input)

# split stereo into mono
audio_path = os.path.join("source", f"{args.id}_audio" )
wav_path = os.path.join(args.audio_folder_root,"0000.wav" )

os.makedirs(audio_path, exist_ok = True)
split_audio_channels(src_path=wav_path, res_dir_path=f"source/{args.id}_audio", speaker_names=speaker_list)

# Match, select segments and cut
# only TWO speakers are allowed (for now)

# INPUTS
# id:             Output folder name
# video_json:     [{'spk': 'spkA', 'start': 15, 'end': 1270}, {'spk': 'spkB', 'start': 1240, 'end': 3535}, ...]
# audio_json:     [{'spk': 'spk1', 'start': 10, 'end': 1200}, {'spk': 'spk2', 'start': 1250, 'end': 3600}, ...]
# video_src_path: Folder containing cropped video files from a certain video (00000.avi and 00001.avi)
# audio_src_path: Folder containing seperated audio files from a certain audio (e.g. 'SPEAKER_00.mp3', 'SPEAKER_01.mp3')

integrator = Integrator(
    id=f"{args.id}",
    video_json=talknet_input, 
    audio_json=seperate_input, 
    # video_src_path=f'source/{args.id}_video', 
    video_src_path= os.path.join(args.talknet_folder_root,"pycrop"),
    audio_src_path=f'source/{args.id}_audio'
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