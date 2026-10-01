import sys, types
sys.modules['sounddevice'] = types.ModuleType('sounddevice')
from israwave import IsraWave
from nakdimon_onnx import Nakdimon
nak = Nakdimon("nakdimon.onnx")
tts = IsraWave("israwave.onnx", "espeak-ng-data")
def speak(text, out, rate=1.0, diacritize=True):
    t = nak.compute(text) if diacritize else text
    w = tts.create(t, rate=rate)
    w.save(out)
    return t
if __name__ == "__main__":
    print(speak(sys.argv[1], sys.argv[2]))
