import openal
from pyogg import VorbisFile
import os
import fnmatch
import random
from . import sndmgr
from .hrtf_init import oalInitHRTF
from .listener import Listener
from .source import Source

# Constants not exposed by the pyopenal bindings
AL_SOURCE_RADIUS = 0x1031

sndmgr = None

class SoundManager(object):
    def __init__(self, sounds_dir="sounds", sound_extensions=["wav", "mp3", "ogg", "flac"], recursive_search=True, init_hrtf=True, coordinates_divider=1, coordinate_decimal_places=None):
        global sndmgr
        self._sounds = {}
        self._sound_files = {}
        self._group_counts = {}
        self._exts = sound_extensions
        self._property_patterns = []
        self._sources = []
        self._coordinates_divider = coordinates_divider
        self._coordinate_decimal_places = coordinate_decimal_places
        openal.oalInit()
        if init_hrtf:
            oalInitHRTF(None)
        self._recursive = recursive_search
        self._sounds_dir = sounds_dir
        self._index_dir(sounds_dir)
        self.listener = Listener(self._coordinates_divider, self._coordinate_decimal_places)
        sndmgr = self

    def _index_dir(self, path):
        for dirpath, subdirs, files in os.walk(path):
            for subdir in subdirs:
                self._maybe_update_group_count(self._to_sound_identifier(dirpath), subdir)
            for file in files:
                name, ext = os.path.splitext(file)
                if ext[1:] in self._exts:
                    self._maybe_update_group_count(self._to_sound_identifier(dirpath), name)
                    sound_name = self._to_sound_identifier(os.path.join(dirpath, name))
                    full_path = os.path.join(dirpath, file)
                    self._sound_files[sound_name] = full_path
    
    def _maybe_update_group_count(self, group, name):
        if not name.isdigit():
            return
        if not group in self._group_counts:
            self._group_counts[group] = 0
        self._group_counts[group] += 1
    
    def _to_sound_identifier(self, path):
        path = os.path.relpath(path, self._sounds_dir)
        parts = path.split(os.sep)
        if parts[0] == self._sounds_dir:
            parts.pop(0)
        return ".".join(parts)
    
    def get(self, name):
        if name in self._sounds:
            return self._sounds[name]
        fname = self._sound_files[name]
        if os.path.splitext(fname)[1] != ".ogg":
            raise ValueError("Not an Ogg file.")
        relpath = os.path.relpath(fname, os.getcwd())
        fp = VorbisFile(relpath)
        sound = openal.Buffer(fp)
        self._sounds[name] = sound
        return sound
    
    def _create_or_find_usable_source(self, buffer):
        try:
            source = Source(buffer, False, self._coordinates_divider, self._coordinate_decimal_places)
            self._sources.append(source)
            return source
        except openal.ALError:
            for candidate_source in self._sources:
                if candidate_source.get_state() == openal.AL_STOPPED:
                    candidate_source._set_buffer(buffer)
                    return candidate_source
            raise RuntimeError("Can not create audio source.")

    def get_channel(self, name, set_loop=False, x=None, y=None, z=None, pan=None):
        buffer = self.get(name)
        ch = self._create_or_find_usable_source(buffer)
        props = self._lookup_properties(name)
        if props.min_distance is not None:
            ch.set_reference_distance(props.min_distance/self._coordinates_divider)
        ch.set_looping(set_loop)
        if x is not None:
            ch.set_position([x, y, z])
            ch.set_rolloff_factor(self._coordinates_divider)
        if pan is not None:
            ch.set_source_relative(True)
            ch.set_position([pan, 0, 0])
        return ch

    def play(self, name, set_loop=False, x=None, y=None, z=None, pan=None):
        print(f"Play {name} at x={x}, y={y}, z={z}")
        ch = self.get_channel(name, set_loop, x, y, z, pan)
        ch.play()
        return ch

    def add_property_pattern(self, pattern, props):
        self._property_patterns.append((pattern, props))
    def _lookup_properties(self, name):
        for pattern, props in self._property_patterns:
            if fnmatch.fnmatch(name, pattern):
                return props
        raise ValueError("No properties for sound %s."%name)
    def get_group_size(self, group):
        if not group in self._group_counts:
            raise ValueError("No such group: %s."%group)
        return self._group_counts[group]
    def play_random_from_group(self, group, *args, **kwargs):
        count = self.get_group_size(group)
        choice = random.randint(1, count)
        sound = "%s.%02d"%(group, choice)
        return self.play(sound, *args, **kwargs)

    def __del__(self):
        openal.oalQuit()