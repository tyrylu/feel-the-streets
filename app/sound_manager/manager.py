import pyfmodex as pf
from pyfmodex.flags import MODE
import os
import fnmatch
import random
from . import sndmgr
mode_2d = MODE.TWOD
mode_3d = MODE.THREED

class SoundManager(object):
    def __init__(self, sounds_dir="sounds", sound_extensions=["wav", "mp3", "ogg", "flac"], recursive_search=True, **system_init_args):
        global sndmgr
        self._sounds = {}
        self._sound_files = {}
        self._group_counts = {}
        self._exts = sound_extensions
        self._property_patterns = []
        self.fmodex_system = pf.System()
        self.fmodex_system.init(**system_init_args)
        self._recursive = recursive_search
        self._sounds_dir = sounds_dir
        self._index_dir(sounds_dir)
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
        if props.is_3d:
            mode = mode_3d
        else:
            mode = mode_2d
        sound = self.fmodex_system.create_sound(fname, mode)
        if props.min_distance is not None:
            sound.min_distance = props.min_distance
        self._sounds[name] = sound
        return sound
    
    def get_channel(self, name, set_loop=False, x=None, y=None, z=None, pan=None):
        ch = self.get(name).play(paused=True)
        if set_loop: ch.mode = 2
        if x is not None:
            ch.position = [x, y, z]
        if pan is not None: ch.pan = pan
        return ch

    def play(self, name, set_loop=False, x=None, y=None, z=None, pan=None):
        ch = self.get_channel(name, set_loop, x, y, z, pan)
        ch.paused = False
        self.fmodex_system.update() #Avoid out of channels error.
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