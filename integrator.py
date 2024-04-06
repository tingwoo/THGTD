import os
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip, AudioFileClip
import numpy as np

class Integrator:
    def __init__(self, id, video_json, audio_json, video_src_path, audio_src_path):
        self.result_path = 'result/' + id

        self.track_length = max(max(video_json, key=lambda x: x['end'])['end'], max(audio_json, key=lambda x: x['end'])['end'])

        self.video_tracks = self.json_to_dict(video_json)
        self.audio_tracks = self.json_to_dict(audio_json)

        self.video_src_path = video_src_path
        self.audio_src_path = audio_src_path

    def json_to_dict(self, data):
        dict = {}

        for segment in data:
            spk = segment['spk']
            if spk in dict:
                dict[spk][segment['start']:segment['end']] = np.ones(segment['end'] - segment['start'], dtype = int)
            else:
                dict[spk] = np.zeros(self.track_length, dtype = int)
                dict[spk][segment['start']:segment['end']] = np.ones(segment['end'] - segment['start'], dtype = int)

        if len(dict) == 1:
            dict['default speaker'] = np.zeros(self.track_length)
                
        return dict

    def find_good_segments(self, starting_point, length, i_thr, a_thr):
        # use audio or video?
        start = starting_point

        if start+length < length:
            return None, None

        names = []
        for spk in self.audio_tracks:
            names.append(spk)
        
        track0_sum = np.sum(self.audio_tracks[names[0]][start:start+length])
        track1_sum = np.sum(self.audio_tracks[names[1]][start:start+length])

        max_tmp = np.maximum(self.audio_tracks[names[0]][start:start+length], self.audio_tracks[names[1]][start:start+length])
        both_sum = np.sum(np.where(max_tmp == 1, 1, 0))

        interact_score = abs(track0_sum - track1_sum) / length
        active_score = both_sum / length

        while start + length < self.track_length:
            if interact_score <= i_thr and active_score >= a_thr:
                print(f"\nFound interval: {start} to {start + length - 1}")
                print(f"Interactivity : {1 - interact_score}")
                print(f"Activity      : {active_score}")
                return start, start + length

            track0_sum -= self.audio_tracks[names[0]][start]
            track1_sum -= self.audio_tracks[names[1]][start]
            track0_sum += self.audio_tracks[names[0]][start+length]
            track1_sum += self.audio_tracks[names[1]][start+length]
            interact_score = abs(track0_sum - track1_sum) / length

            both_sum -= max(self.audio_tracks[names[0]][start], self.audio_tracks[names[1]][start])
            both_sum += max(self.audio_tracks[names[0]][start+length], self.audio_tracks[names[1]][start+length])
            active_score = both_sum / length

            start += 1

        return None, None

    def cut_video(self, intervals, source_path, target_face):
        video = VideoFileClip(source_path)

        for interval in intervals:
            print(f"Interval {interval[0]} - {interval[1]}")
            folder_name = f"{target_face}_{interval[0]}_{interval[1]}"
            if not os.path.exists(os.path.join(self.result_path, folder_name)):
                os.makedirs(os.path.join(self.result_path, folder_name))
            clip = video.subclip(interval[0]/1000, interval[1]/1000)
            clip = clip.set_audio(None)
            clip.write_videofile(os.path.join(self.result_path, folder_name, 'video.mp4'), verbose=False, logger=None)

    def cut_audio(self, intervals, source_path, target_face, suffix):
        audio = AudioFileClip(source_path)

        for interval in intervals:
            print(f"Interval {interval[0]} - {interval[1]}")
            folder_name = f"{target_face}_{interval[0]}_{interval[1]}"
            if not os.path.exists(os.path.join(self.result_path, folder_name)):
                os.makedirs(os.path.join(self.result_path, folder_name))
            clip = audio.subclip(interval[0]/1000, interval[1]/1000)
            clip.write_audiofile(os.path.join(self.result_path, folder_name, f'audio_{suffix}.wav'), verbose=False, logger=None)

    def compare_two_tracks(self, track1, track2):
        cmp = np.where(track1 == track2, 1, 0)
        return np.sum(cmp) / cmp.size

    def match_video_to_audio(self, target_face):
        best_match_score = 0
        best_match = ''
        for spk in self.audio_tracks:
            tmp_score = self.compare_two_tracks(self.video_tracks[target_face], self.audio_tracks[spk])
            print("Compared to " + spk + ": " + str(round(tmp_score, 3)) + " match")
            if tmp_score > best_match_score:
                best_match_score = tmp_score
                best_match = spk

        for spk in self.audio_tracks:
            if spk != best_match:
                return best_match, spk
        return

    def generate_data(self, target_face, at_most, length, i_threshold=0.1, a_threshold=0.7, visualize=False):
        # create directory for clips generated from this video
        if not os.path.exists(self.result_path):
            os.makedirs(self.result_path)

        print('\n-- Match Video to Audio --')
        print(f"What is the best match for video speaker \"{target_face}\"?")
        matched_speaker, other_speaker = self.match_video_to_audio(target_face)
        print('Matched Speaker: ' + matched_speaker)
        
        print('\n-- Select Clips That Are Both Interactive and Active --')
        current_point = 0
        clips_count = 0
        intervals = []
        for _ in range(at_most):
            start, end = self.find_good_segments(current_point, length, i_threshold, a_threshold)
            if start is None:
                break
            clips_count += 1
            intervals.append([start, end])
            current_point = end

        print("\n-- Cut Video and Audio into Clips --") 
        # clip_path = os.path.join(self.result_path, f"{start}_{end-1}")
        print("\n- Cuttting video") 
        self.cut_video(intervals, os.path.join(self.video_src_path, target_face+'.avi'), target_face)
        print("\n- Cuttting audio (matched speaker)") 
        self.cut_audio(intervals, os.path.join(self.audio_src_path, matched_speaker+'.wav'), target_face, 'matched')
        print("\n- Cuttting audio (the other speaker)") 
        self.cut_audio(intervals, os.path.join(self.audio_src_path, other_speaker+'.wav'), target_face, 'other')

        print(f"\nGenerated {clips_count} clips.")

        if visualize:
            fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(16, 8))

            axes[0].plot(self.video_tracks[target_face], 'r')
            axes[0].set_title('Target Face')
            axes[0].set_xlim(0, self.track_length)

            axes[1].plot(self.audio_tracks[matched_speaker])
            axes[1].set_title(f'Matched Speaker: {matched_speaker}')
            axes[1].set_xlim(0, self.track_length)

            axes[2].plot(self.audio_tracks[other_speaker])
            axes[2].set_title(f'The Other Speaker: {other_speaker}')
            axes[2].set_xlim(0, self.track_length)

            for i, interval in enumerate(intervals):
                if interval[0] is not None:
                    axes[0].barh(0.5, interval[1] - interval[0], left=interval[0], height=1.2, color='yellow')
                    axes[1].barh(0.5, interval[1] - interval[0], left=interval[0], height=1.2, color='yellow')
                    axes[2].barh(0.5, interval[1] - interval[0], left=interval[0], height=1.2, color='yellow')

            plt.subplots_adjust(hspace=0.5)
            # plt.show()
            plt.savefig(os.path.join(self.result_path, 'plot.png'))

    
