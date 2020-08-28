import openal
from openal import *
from openal import _err
from openal.al_lib import lib


# Constants needed to do the initialization.
ALC_NUM_HRTF_SPECIFIERS_SOFT = 0x1994
ALC_HRTF_SPECIFIER_SOFT = 0x1995
ALC_HRTF_SOFT = 0x1992
# And a function as well...
alcGetStringiSOFT = lib.alcGetStringiSOFT
alcGetStringiSOFT.argtypes = [ctypes.c_void_p, ctypes.c_int]
alcGetStringiSOFT.restype = ctypes.c_char_p
alcResetDeviceSOFT = lib.alcResetDeviceSOFT
alcResetDeviceSOFT.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
alcResetDeviceSOFT.restype = ctypes.c_char
def oalInitHRTF(requested_hrtf=None):
    
    global _stereo_angles_ext_supported, _hrtf_enabled
    if not alc.alcIsExtensionPresent(openal._oaldevice, b"ALC_SOFT_HRTF"):
        _err("HRTF extension not present")
        
    if al.alIsExtensionPresent(b"AL_EXT_STEREO_ANGLES"):
        _stereo_angles_ext_supported = True
    else:
        _stereo_angles_ext_supported = False
        
    # Enumerate available HRTFs, and reset the device using one
    num_hrtf = ctypes.c_int(0)
    alc.alcGetIntegerv(openal._oaldevice, ALC_NUM_HRTF_SPECIFIERS_SOFT, 1, num_hrtf)
    
    if num_hrtf.value == 0:
        _err("No HRTFs found")
    else:
        attr = (ctypes.c_int * 5)()
        
        index = -1
        for n in range(num_hrtf.value):
            hrtfname = alcGetStringiSOFT(openal._oaldevice, ALC_HRTF_SPECIFIER_SOFT, n).decode("utf-8")    
            if requested_hrtf == hrtfname:
                if requested_hrtf == hrtfname:
                    index = n
        
        attr[0] = ALC_HRTF_SOFT
        attr[1] = ALC_TRUE
        
        if index == -1:
            if requested_hrtf:
                _err('HRTF "{}" not found'.format(requested_name))
        else:
            attr[2] = ALC_HRTF_ID_SOFT
            attr[3] = index
            
        attr[4] = 0
            
        if not alcResetDeviceSOFT(openal._oaldevice, attr):        
            _err("Failed to reset device: {}".format(alc.alcGetError(_oaldevice, alcGetError(_oaldevice))))       
            
        # Check if HRTF is enabled
        hrtf_state = ctypes.c_int(0)
        alc.alcGetIntegerv(openal._oaldevice, ALC_HRTF_SOFT, 1, hrtf_state)
        if not hrtf_state:
            _err("Something went wrong, HRTF is still not enabled (check console for errors)")
            _hrtf_enabled = False
        else:
            _hrtf_enabled = True                 
        