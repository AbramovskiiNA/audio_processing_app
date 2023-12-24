import argparse
import json
import logging
import wave

import pyrubberband as pyrb
import soundfile as sf
from pydub import AudioSegment
from pythonjsonlogger import jsonlogger
from vosk import KaldiRecognizer, Model, SetLogLevel

logger = logging.getLogger()

logHandler = logging.FileHandler(filename='log.txt', mode='w', encoding='utf-8')
logHandler.setFormatter(jsonlogger.JsonFormatter('%(asctime)%(levelname)%(message)'))
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)


def main():
    args = parse_arguments()

    if args.mode == 'modification':
        modify_audio(args.infile,
                     args.outfile,
                     args.volume,
                     args.speed)
    elif args.mode == 'recognition':
        recognize_text(args.infile,
                       args.outfile,
                       args.language)


def modify_audio(infile, outfile, volume: float = 1, speed: float = 1):
    audio = AudioSegment.from_wav(infile)
    audio = audio + volume
    audio.export(outfile, 'wav')

    data, samplerate = sf.read(outfile)
    stretched = pyrb.time_stretch(data, samplerate, speed)
    # shifted = pyrb.pitch_shift(data, samplerate, speed)
    sf.write(outfile, stretched, samplerate, format='wav')


def recognize_text(infile, outfile, language: str):
    SetLogLevel(-1)

    if language == 'en':
        model = Model(lang="en-us")
    else:
        model = Model(lang="ru")
    logging.info('Model ready')

    wf = wave.open(infile, 'rb')
    logging.info(f'Audio file {infile} open')

    rec = KaldiRecognizer(model, wf.getframerate())
    rec.AcceptWaveform(wf.readframes(wf.getnframes()))
    logging.info('Recognition finished')
    result = rec.FinalResult()

    text = json.loads(result)['text']
    with open(outfile, 'w', encoding='utf-8') as w:
        w.write(text)
        logging.info(f'Text file {outfile} saved')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', type=str, choices=['modification', 'recognition'],
                        default='modification',
                        help='app mode')
    parser.add_argument('infile',
                        help='input audio file path')
    parser.add_argument('outfile',
                        help='output audio file path')
    parser.add_argument('-v', '--volume', type=float,
                        help='volume increase factor in dB')
    parser.add_argument('-s', '--speed', type=float,
                        help='speed increase factor')
    parser.add_argument('-l', '--language', type=str, choices=['en', 'ru'], default='en',
                        help='language for recognition')
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main()
