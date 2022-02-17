import asyncio

import numpy as np
from pulsectl_asyncio import PulseAsync
from pyaudio import PyAudio, paUInt8, paContinue
from scipy.fft import rfft
from ui import UI


class Audio(object):

    def __init__(self, ui: UI, device_index: int, pulse_index: int, chunk: int, rate: int, bars: int, sensitivity: int):
        assert chunk % bars == 0
        self.pyaudio = PyAudio()
        self.ui = ui
        self.chunk = chunk * 2
        self.rate = rate
        self.sensitivity = sensitivity
        self.chunk_to_bars = chunk // bars
        self.device = None
        self.stream = None
        self.volume = None
        self.start(device_index, pulse_index)

    def start(self, device, pulse):
        self.stream = self.pyaudio.open(format=paUInt8,
                                        channels=1,
                                        rate=self.rate,
                                        frames_per_buffer=self.chunk,
                                        input=True,
                                        input_device_index=pulse,
                                        stream_callback=self.audio_callback,
                                        start=False)
        asyncio.run(self.start_pulse(device))

    async def start_pulse(self, device):
        async with PulseAsync("FFT Curses") as pulse:
            self.device = (await pulse.sink_list())[device].index

            await self.update_volume(pulse)
            self.stream.start_stream()

            await self.listen(pulse)

    def do_fft(self, data):
        levels = np.abs(rfft(data))[1:] / self.chunk  # Stripping y(0)
        levels = levels.reshape(-1, self.chunk_to_bars).mean(1)  # Averaging values for bars
        levels = levels.clip(0, 255)

        return levels

    def audio_callback(self, in_data, frame_count, time_info, status):
        audio_data = np.frombuffer(in_data, np.uint8) / self.volume * self.sensitivity
        self.ui.update_levels(self.do_fft(audio_data))

        return in_data, paContinue

    async def listen(self, pulse):
        async for event in pulse.subscribe_events('sink'):
            # Pulseaudio does not provide a info regarding what event happend
            # So just update volume every time something related to our device happens
            # Not efficient but that's all we have   
            if event.index == self.device:
                await self.update_volume(pulse)

    async def update_volume(self, pulse):
        # Cube the volume, pulsectl for some reason does not do this
        # See pa_sw_volume_to_linear function at
        # https://fossies.org/linux/pulseaudio/src/pulse/volume.c
        self.volume = (await pulse.sink_info(self.device)).volume.value_flat ** 3