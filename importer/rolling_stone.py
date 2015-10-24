"""Importer for the Rolling Stone 500 Dataset.
   http://theory.esm.rochester.edu/rock_corpus/

"""
import numpy as np
import os
import glob
from base import ImporterBase


class ImporterRollingStone(ImporterBase):
    """Base Class for the dataset import.
    """
    def __init__(self, path='../data/rock_corpus_v2-1/rs200_melody_nlt'):
        self.path = path
        self.output = []
        self.pr_n_pitches = 120
        self.pr_bar_division = 16

        path_songs = os.path.join(self.path, '*.nlt')

        for cur_path_song in glob.glob(path_songs):
            cur_song_events = []

            # prevent from trying to read empty files
            if os.stat(cur_path_song).st_size == 0:
                continue

            with open(cur_path_song) as cur_song:
                for cur_event in cur_song:
                    # ignore Error lines
                    if 'Error' in cur_event:
                        continue

                    # every event consists of
                    # Onset, Position in bar, Pitch, Scale Degree
                    cur_event_list = [float(x) for x in cur_event.rstrip().split("\t")]
                    cur_song_events.append(cur_event_list)

            self.import_piano_roll(np.asarray(cur_song_events))

    def import_piano_roll(self, note_events):
        # get the number of total bars
        n_bars = int(note_events[-1][1])+1

        # reserve memory
        piano_roll = np.zeros([self.pr_n_pitches, self.pr_bar_division*n_bars])

        # pitch_range_start = np.min(note_events[:, 2])
        # pitch_range_end = np.max(note_events[:, 2])
        # print(pitch_range_start, pitch_range_end, pitch_range_end-pitch_range_start)

        # set the note length as the derivative of the onsets
        # (suggested in the documentation)
        note_events = np.c_[note_events[:-1], np.diff(note_events[:, 0])]

        # loop over bars
        bar_grid = np.linspace(0, 1, self.pr_bar_division)

        for cur_bar in range(int(note_events[0][1]), int(note_events[-1][1])):
            # get the notes which belong to the bar
            cur_notes = note_events[note_events[:, 1] - cur_bar < 1, :]

            # what are the nearest notes
            offset = int(cur_notes[0][0])

            for cur_note in cur_notes:
                note_idx_start = np.argmin(cur_note[1]-bar_grid)
                duration = int(1.0 / cur_note[4])
                note_idx_end = note_idx_start + duration
                cur_pitch = cur_note[2]

                # add to piano-roll
                cur_bar_idx_start = cur_bar*self.pr_bar_division
                cur_bar_idx_end = (cur_bar+1)*self.pr_bar_division
                piano_roll[cur_pitch, cur_bar_idx_start+note_idx_start:cur_bar_idx_start+note_idx_end] = 1

        import matplotlib.pyplot as plt
        plt.imshow(piano_roll, cmap=plt.get_cmap('gray_r'))
        plt.show()

        # append to output list
        self.output.append(piano_roll)

    def add_beat_flags(self):
        pass

if __name__ == '__main__':
    data_rs = ImporterRollingStone()
