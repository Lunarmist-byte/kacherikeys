
import time
import math
import serial
import pygame
import numpy as np

# ==========================================
# CONFIGURATION
# ==========================================

PORT = "COM7"
BAUD = 115200
SAMPLE_RATE = 44100

NOTES = [60, 62, 64, 65, 67, 69, 71, 72]

MODE_NAMES = [
    "PIANO",
    "SYNTH",
    "DRUMS"
]

SYNTH_NAMES = [
    "SINE",
    "SQUARE",
    "SAWTOOTH",
    "TRIANGLE"
]

# ==========================================
# AUDIO INITIALIZATION
# ==========================================

pygame.mixer.pre_init(
    frequency=SAMPLE_RATE,
    size=-16,
    channels=2,
    buffer=512
)

pygame.init()
pygame.mixer.set_num_channels(32)

# ==========================================
# GLOBAL STATE
# ==========================================

current_mode = 0
transpose = 0
sustain = False

active_channels = {}
sustained_notes = set()

sound_cache = {}
drum_cache = {}

# ==========================================
# FREQUENCY CALCULATION
# ==========================================

def note_frequency(note):
    return 440.0 * (2 ** ((note - 69) / 12))


# ==========================================
# CONVERT AUDIO TO PYGAME SOUND
# ==========================================

def create_sound(wave):

    peak = np.max(np.abs(wave))

    if peak > 0:
        wave = wave / peak

    audio = (wave * 12000).astype(np.int16)

    stereo = np.column_stack((audio, audio))

    return pygame.sndarray.make_sound(stereo)


# ==========================================
# PIANO MODE
# ==========================================

def make_piano(note):

    frequency = note_frequency(note)

    duration = 1.0

    t = np.arange(
        int(SAMPLE_RATE * duration)
    ) / SAMPLE_RATE

    wave = (
        np.sin(2 * np.pi * frequency * t)
        + 0.30 * np.sin(4 * np.pi * frequency * t)
        + 0.12 * np.sin(6 * np.pi * frequency * t)
        + 0.04 * np.sin(8 * np.pi * frequency * t)
    )

    return create_sound(wave)


# ==========================================
# SYNTH MODE
# ==========================================

def make_synth(note, preset):

    frequency = note_frequency(note)

    duration = 1.0

    t = np.arange(
        int(SAMPLE_RATE * duration)
    ) / SAMPLE_RATE

    phase = 2 * np.pi * frequency * t

    if preset == 0:

        wave = np.sin(phase)

    elif preset == 1:

        wave = np.sign(np.sin(phase))

    elif preset == 2:

        wave = 2 * (
            frequency * t - np.floor(
                0.5 + frequency * t
            )
        )

    else:

        wave = 2 * np.abs(
            2 * (
                frequency * t - np.floor(
                    frequency * t + 0.5
                )
            )
        ) - 1

    return create_sound(wave)


# ==========================================
# DRUM MODE
# ==========================================

def make_drum(index, transpose_value):

    factor = 2 ** (transpose_value / 12)

    durations = [
        0.8, 0.6, 0.2, 0.8,
        0.6, 0.5, 0.5, 1.2
    ]

    duration = durations[index]

    count = int(SAMPLE_RATE * duration)

    t = np.arange(count) / SAMPLE_RATE

    rng = np.random.default_rng()

    noise = rng.uniform(-1, 1, count)

    if index == 0:
        # Kick drum

        frequency = 90 * factor * np.exp(-t * 8) + 35 * factor

        phase = 2 * np.pi * np.cumsum(frequency) / SAMPLE_RATE

        wave = np.sin(phase) * np.exp(-t * 6)

    elif index == 1:
        # Snare

        wave = (
            0.7 * noise * np.exp(-t * 15)
            + 0.3 * np.sin(
                2 * np.pi * 180 * factor * t
            ) * np.exp(-t * 20)
        )

    elif index == 2:
        # Closed hi-hat

        wave = np.diff(
            np.append(noise, 0)
        ) * np.exp(-t * 60)

    elif index == 3:
        # Open hi-hat

        wave = np.diff(
            np.append(noise, 0)
        ) * np.exp(-t * 7)

    elif index == 4:
        # Low tom

        frequency = 120 * factor * np.exp(-t * 4)

        phase = 2 * np.pi * np.cumsum(frequency) / SAMPLE_RATE

        wave = np.sin(phase) * np.exp(-t * 5)

    elif index == 5:
        # High tom

        frequency = 220 * factor * np.exp(-t * 5)

        phase = 2 * np.pi * np.cumsum(frequency) / SAMPLE_RATE

        wave = np.sin(phase) * np.exp(-t * 7)

    elif index == 6:
        # Clap

        envelope = (
            np.exp(-t * 25)
            + 0.7 * np.exp(-np.maximum(t - 0.025, 0) * 30)
            + 0.5 * np.exp(-np.maximum(t - 0.05, 0) * 35)
        )

        wave = noise * envelope

    else:
        # Crash

        wave = np.diff(
            np.append(noise, 0)
        ) * np.exp(-t * 3)

    return create_sound(wave)


# ==========================================
# SOUND CACHE
# ==========================================

def get_sound(note):

    actual_note = note + transpose

    key = (current_mode, actual_note)

    if key in sound_cache:
        return sound_cache[key]

    if current_mode == 0:

        sound = make_piano(actual_note)

    else:

        preset = 0

        if current_mode == 1:
            sound = make_synth(actual_note, preset)

        else:
            return None

    sound_cache[key] = sound

    return sound


def get_drum(index):

    key = (index, transpose)

    if key not in drum_cache:

        drum_cache[key] = make_drum(
            index,
            transpose
        )

    return drum_cache[key]


# ==========================================
# NOTE MANAGEMENT
# ==========================================

def stop_all_notes():

    for channel in active_channels.values():
        channel.fadeout(60)

    active_channels.clear()
    sustained_notes.clear()


def note_on(note, velocity):

    if current_mode == 2:

        index = NOTES.index(note)

        sound = get_drum(index)

        channel = pygame.mixer.find_channel(True)

        channel.set_volume(
            max(0.05, min(1.0, velocity / 127))
        )

        channel.play(sound)

        print("DRUM:", index + 1)

        return

    if note in active_channels:
        return

    sound = get_sound(note)

    if sound is None:
        return

    channel = pygame.mixer.find_channel(True)

    channel.set_volume(
        max(0.05, min(1.0, velocity / 127))
    )

    channel.play(sound, loops=-1)

    active_channels[note] = channel

    print(
        "NOTE ON:",
        note + transpose,
        "MODE:",
        MODE_NAMES[current_mode]
    )


def note_off(note):

    if current_mode == 2:
        return

    if note not in active_channels:
        return

    if sustain:

        sustained_notes.add(note)

    else:

        active_channels[note].fadeout(100)

        del active_channels[note]


# ==========================================
# MODE CONTROL
# ==========================================

def change_mode(new_mode):

    global current_mode

    new_mode = new_mode % 3

    if new_mode == current_mode:
        return

    stop_all_notes()

    current_mode = new_mode

    print("\n------------------------")
    print("MODE:", MODE_NAMES[current_mode])
    print("------------------------\n")


# ==========================================
# SERIAL EVENT HANDLER
# ==========================================

def process_message(line):

    global transpose, sustain

    parts = line.split()

    if not parts:
        return

    command = parts[0]

    if command == "ON" and len(parts) == 3:

        note = int(parts[1])
        velocity = int(parts[2])

        if note in NOTES:
            note_on(note, velocity)

    elif command == "OFF" and len(parts) == 2:

        note = int(parts[1])

        if note in NOTES:
            note_off(note)

    elif command == "MODE" and len(parts) == 2:

        change_mode(int(parts[1]))

    elif command == "TRANSPOSE" and len(parts) == 2:

        transpose = int(parts[1])

        print(
            "TRANSPOSE:",
            transpose,
            "semitones"
        )

    elif command == "SUSTAIN" and len(parts) == 2:

        new_state = bool(int(parts[1]))

        if sustain and not new_state:

            for note in list(sustained_notes):

                if note in active_channels:

                    active_channels[note].fadeout(100)

                    del active_channels[note]

            sustained_notes.clear()

        sustain = new_state

        print(
            "SUSTAIN:",
            "ON" if sustain else "OFF"
        )


# ==========================================
# MAIN APPLICATION
# ==========================================

def main():

    print("==========================")
    print("       WIREKEYS v1.1")
    print("==========================")

    print("Connecting to ESP32:", PORT)

    esp = None

    try:

        esp = serial.Serial(
            PORT,
            BAUD,
            timeout=0.05
        )

        time.sleep(2)

        esp.reset_input_buffer()

        print("\nWIREKEYS CONNECTED")
        print("Touch the electrodes to play.")
        print("Joystick controls instrument modes and pitch.")
        print("Press joystick to toggle sustain.\n")

        while True:

            line = esp.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if line:
                process_message(line)

    except KeyboardInterrupt:

        print("\nWIREKEYS STOPPED")

    except serial.SerialException as error:

        print("\nSERIAL ERROR:", error)

        print(
            "Check COM port and close Arduino Serial Monitor."
        )

    except Exception as error:

        print("\nERROR:", error)

    finally:

        stop_all_notes()

        if esp and esp.is_open:
            esp.close()

        pygame.quit()


if __name__ == "__main__":
    main()
