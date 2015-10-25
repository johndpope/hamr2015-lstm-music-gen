__author__ = 'epnichols'

from settings import *

from music21 import stream, note, scale, duration
import music21.midi as midi

import numpy as np

class MidiExporter(object):
    song = None

    def __init__(self, song_array):
        """song_array: numpy matrix of features for each frame.
        """
        self.song = song_array

        print 'Feature vector length:', FEATURE_VECTOR_LENGTH
        print 'Melody bits:', MELODY_INDICES_RANGE
        print 'Harmony bits:', HARMONY_INDICES_RANGE
        print 'Continuation bits:', CONTINUATION_FLAG_RANGE
        print 'Metric flag bits:', METRIC_FLAGS_RANGE

        #print 'song:', self.song
        print 'song.shape', self.song.shape


    def create_midi_file(self, filename):
        # s = stream.Stream()
        # n = note.Note('g#')
        # n.quarterLength = .5
        # s.repeatAppend(n, 4)
        # mf = midi.translate.streamToMidiFile(s)

        # sc = scale.PhrygianScale('g')
        # x = [s.append(note.Note(sc.pitchFromDegree(i % 11), quarterLength=.25)) for i in range(60)]


        # Melody stream.
        s = stream.Stream()

        num_frames = 0
        prev_n = -1
        new_note = None
        for frame in self.song:
            melody = frame[MELODY_INDICES_RANGE[0]:MELODY_INDICES_RANGE[1]]
            print melody
            n = None
            for i, val in enumerate(melody):
                if val == 1:
                    n = i
                    break

            # If the pitch changes, commit previous note and start new one.
            if n != prev_n:
                prev_n = n
                # commit the previous note.
                if new_note:
                    new_note.quarterLength = .25 * num_frames
                    s.append(new_note)
                # start a new note.
                if n is not None:
                    new_note = note.Note(i + 60)
                else:
                    # rest
                    new_note = note.Rest()
                num_frames = 1
            else:  # TODO: test for continuity flag
                # note is continued. Just add to the duration.
                num_frames += 1

        # Commit the final note
        new_note.quarterLength = .25 * num_frames
        s.append(new_note)

        # Harmony stream.
        s_harmony = stream.Stream()
        prev_harmony = []
        new_harmony = None
        num_frames = 0
        for frame in self.song:
            harmony = frame[HARMONY_INDICES_RANGE[0]:HARMONY_INDICES_RANGE[1]]
            print harmony

            # If the set of pitch classes changes, commit previous chord and start new one.
            if n != prev_n:
                prev_n = n
                # commit the previous note.
                if new_note:
                    new_note.quarterLength = .25 * num_frames
                    s.append(new_note)
                # start a new note.
                if n is not None:
                    new_note = note.Note(i + 60)
                else:
                    # rest
                    new_note = note.Rest()
                num_frames = 1
            else:  # TODO: test for continuity flag
                # note is continued. Just add to the duration.
                num_frames += 1

        # Commit the final note
        new_note.quarterLength = .25 * num_frames
        s.append(new_note)

        # Write midi file to disk.
        mf = midi.translate.streamToMidiFile(s)
        mf.open(filename, 'wb')
        mf.write()
        mf.close()

if __name__ == '__main__':
    # Make a random song.
    random_song = np.random.randint(0, 2, size=(16, FEATURE_VECTOR_LENGTH))

    exporter = MidiExporter(random_song)
    exporter.create_midi_file('random.midi')


