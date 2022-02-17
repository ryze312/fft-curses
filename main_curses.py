import helpers
import curses

DEVICE_INX = None # Get with PyAudio.get_device_info_by_index
PULSE_INX = None # Get with Pulse.sink_list

# Doesn't have to be the same as your audio device rate
SAMPLE_RATE = 11025
CHUNK_SIZE = 128
BARS = 128
AMPLIFY = 20

FG_COLOR = curses.COLOR_RED
BG_COLOR = curses.COLOR_BLACK

if DEVICE_INX is None or PULSE_INX is None:
    print("Please configure script according to README")

else:
    try:
        ui = helpers.UI(FG_COLOR, BG_COLOR)
        curses.wrapper(ui.init) 
        helpers.Audio(ui, DEVICE_INX, PULSE_INX, CHUNK_SIZE, SAMPLE_RATE, BARS, AMPLIFY)

    except KeyboardInterrupt:
        curses.endwin()
