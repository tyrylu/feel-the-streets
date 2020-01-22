import openal
import os
import fnmatch
import random
from . import sndmgr

sndmgr = None

class SoundManager(object):
    def __init__(self, sounds_dir="sounds", sound_extensions=["wav", "mp3", "ogg", "flac"], recursive_search=True, **system_init_args):
        global sndmgr
        self._sounds = {}
        self._sound_files = {}
        self._group_counts = {}
        self._exts = sound_extensions
        self._property_patterns = []
        openal.oalInit()
        self._recursive = recursive_search
        self._sounds_dir = sounds_dir
        self._index_dir(sounds_dir)
        self.listener = openal.Listener()
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
        props = self._lookup_properties(name)
        fname = self._sound_files[name]
        sound = openal.oalOpen(fname)
        if props.min_distance is not None:
            sound.set_reference_distance(props.min_distance)
        self._sounds[name] = sound
        return sound
    
    def get_channel(self, name, set_loop=False, x=None, y=None, z=None, pan=None):
        ch = self.get(name)
        ch.set_looping(set_loop)
        if x is not None:
            ch.set_position([x, y, z])
        if pan is not None:
            ch.set_source_relative(True)
            ch.set_position([pan, 0, 0])
        return ch

    def play(self, name, set_loop=False, x=None, y=None, z=None, pan=None):
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