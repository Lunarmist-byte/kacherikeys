# WIREKEYS

### A modular, touch-sensitive musical instrument built with ESP32

WIREKEYS is an experimental electronic musical instrument that transforms ordinary jumper wires into touch-sensitive musical keys.

Built around an ESP32 DevKit V1, the project uses capacitive touch sensing to detect interactions with exposed conductive wires. These interactions are transmitted to a computer over serial communication, where a Python-based audio engine interprets them and generates sound.

The goal is to explore the intersection of embedded systems, electronics, software, and music by building a configurable musical interface using unconventional hardware.

Rather than being limited to a conventional keyboard, WIREKEYS aims to support multiple musical interaction modes through a single hardware interface.

## Project Overview

- Microcontroller: ESP32 DevKit V1 (classic ESP32)
- Input: Capacitive touch electrodes
- Communication: USB serial
- Audio processing: Python
- Audio library: Pygame and NumPy
- Current inputs: 8 independent electrodes
- Current note range: C4 to C5

## Operating Modes

WIREKEYS is designed around a modular input-to-sound architecture. The same physical electrodes can perform different functions depending on the selected operating mode.

### 1. Piano Mode

The electrodes behave like individual piano keys.

Each electrode corresponds to a musical note. Touching an electrode triggers the corresponding note, and releasing it stops the sound.

Initial mapping:

| Electrode | Note | MIDI Number |
|---|---|---:|
| 1 | C4 | 60 |
| 2 | D4 | 62 |
| 3 | E4 | 64 |
| 4 | F4 | 65 |
| 5 | G4 | 67 |
| 6 | A4 | 69 |
| 7 | B4 | 71 |
| 8 | C5 | 72 |

Planned features:
- Configurable note mappings.
- Octave switching.
- Multiple simultaneous notes.
- Chord support.
- Sustain control.
- Different piano SoundFonts.

### 2. Synth Mode

The electrodes become triggers for a synthesizer.

Instead of producing conventional piano sounds, the audio engine generates electronic tones and synthesizer sounds.

Planned features:
- Multiple oscillator waveforms.
- Sine, square, sawtooth, and triangle waves.
- Adjustable attack, decay, sustain, and release (ADSR).
- Filter and modulation effects.
- Configurable pitch mapping.
- Different synthesizer presets.

The long-term goal is to experiment with creating an expressive touch-controlled synthesizer.

### 3. Drum Mode

The electrodes become individual percussion triggers.

Each electrode triggers a different drum sound rather than a sustained musical note.

Initial mapping:

| Electrode | Instrument |
|---|---|
| 1 | Kick |
| 2 | Snare |
| 3 | Closed hi-hat |
| 4 | Open hi-hat |
| 5 | Low tom |
| 6 | High tom |
| 7 | Clap |
| 8 | Crash |

Planned features:
- Sample-based drum sounds.
- Adjustable trigger sensitivity.
- Velocity-sensitive triggering.
- Custom sample mapping.
- Simultaneous percussion triggers.
- Basic rhythm and pattern experimentation.

## Hardware

| Component | Purpose |
|---|---|
| ESP32 DevKit V1 | Main controller |
| 8 jumper wires | Capacitive touch electrodes |
| USB cable | Power and serial communication |
| Computer | Audio generation and mode selection |

No dedicated touch-sensor modules are required for the initial prototype.

## Circuit Configuration

Each jumper wire is connected to a capacitive touch-capable GPIO pin on the classic ESP32.

| Electrode | GPIO | Touch Channel |
|---|---:|---|
| 1 | GPIO 4 | T0 |
| 2 | GPIO 13 | T4 |
| 3 | GPIO 12 | T5 |
| 4 | GPIO 14 | T6 |
| 5 | GPIO 27 | T7 |
| 6 | GPIO 33 | T8 |
| 7 | GPIO 32 | T9 |
| 8 | GPIO 15 | T3 |

The exposed metal ends of the jumper wires act as touch electrodes.

**Hardware note:** GPIO 12 and GPIO 15 are ESP32 strapping pins. If boot issues occur, disconnect the corresponding electrodes during startup and consider using alternative touch-capable pins. Never connect the electrodes directly to an external voltage supply.

## System Architecture

The project is divided into two major components.

### ESP32 Firmware

The ESP32 handles:
- Capacitive touch measurement.
- Baseline calibration.
- Touch detection.
- Key press and release detection.
- Touch intensity estimation.
- Serial event transmission.

The firmware sends events in a simple format:

```text
ON 60 85
OFF 60
```

The event contains:
- Event type.
- Electrode's assigned MIDI note number.
- Estimated touch intensity.

The firmware does not need to know whether the computer is running Piano, Synth, or Drum mode.

### Python Audio Engine

The Python application handles:
- Serial communication.
- Operating mode selection.
- Input-to-sound mapping.
- Audio generation.
- Sound playback.
- Simultaneous audio events.

The selected mode determines how incoming electrode events are interpreted.

For example, the same electrode can trigger C4 in Piano Mode, a synthesizer tone in Synth Mode, or a kick drum in Drum Mode.

## Software Requirements

- Arduino IDE
- ESP32 board support package
- Python 3.11 or compatible
- PySerial
- Pygame
- NumPy

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Lunarmist-byte/WIREKEYS.git
cd WIREKEYS
```

### 2. Upload the firmware

1. Open the firmware sketch in Arduino IDE.
2. Select ESP32 DevKit V1.
3. Select the correct serial port.
4. Set upload speed to 115200 if required.
5. Upload the firmware.

Keep all electrodes untouched during startup calibration.

### 3. Create the Python environment

Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\activate
```

### 4. Install dependencies

```bash
python -m pip install pyserial pygame numpy
```

## 4.5 Download the Audio Pack
Link:https://musical-artifacts.com/artifacts/1229
Put it in a folder called 'audio', the file should end with .sf2

### 5. Configure the serial port

Update the port in the Python configuration:

```python
PORT = "COM7"
BAUD = 115200
```

Replace `COM7` with the serial port assigned to your ESP32.

Close Arduino Serial Monitor before launching the Python application.

### 6. Run the application

```bash
python wirekey.py
```

## Project Structure

```text
WIREKEYS/
│
├── firmware/
│   └── wirekeys.ino
│
├── software/
│   ├── wirekey.py
│   ├── audio_engine.py
│   ├── modes/
│   │   ├── piano.py
│   │   ├── synth.py
│   │   └── drums.py
│   └── samples/
│       └── drums/
│
├── requirements.txt
├── README.md
└── LICENSE
```

This is the planned modular structure. The current prototype may still have its firmware and Python application in separate standalone files.

## Development Roadmap

### Version 1.0 — Initial Prototype
- [x] ESP32 capacitive touch detection.
- [x] Eight touch electrodes.
- [x] Serial communication.
- [x] Basic software-generated audio.
- [x] Note-on and note-off events.

### Version 1.1 — Modular Audio Engine
- [x] Separate input processing from sound generation.
- [x] Implement Piano Mode.
- [x] Implement Synth Mode.
- [x] Implement Drum Mode.
- [x] Add runtime mode selection.
- [x] Support configurable electrode mappings.

### Version 1.2 — Improved Audio
- [x] Integrate FluidSynth and SoundFonts.
- [x] Add realistic piano and instrument sounds.
- [x] Add sample-based percussion.
- [x] Implement synthesizer oscillators.
- [x] Add ADSR envelopes and effects.


## Current Limitations

- Touch detection is affected by electrode geometry and environmental noise.
- Touch intensity is an approximation based on capacitive readings, not a direct measurement of pressure.
- The initial audio engine uses generated waveforms rather than realistic instrument samples.
- The current firmware uses startup calibration.
- The initial prototype has a fixed eight-electrode configuration.

## Contributing

WIREKEYS is an experimental open-source hardware and software project.

Ideas, improvements, experiments, and contributions are welcome. The project is particularly interested in unconventional musical interfaces, embedded systems, capacitive sensing, and real-time audio processing.

### Images and Demo
https://github.com/user-attachments/assets/84c43484-03e1-42b8-8ab7-dde49cdc5dc5
<img width="1280" height="960" alt="WhatsApp Image 2026-10-31 at 8 30 46 PM" src="https://github.com/user-attachments/assets/263ee2b3-7547-4163-ae27-ce4072c44650" />


## License

MIT License.

---
