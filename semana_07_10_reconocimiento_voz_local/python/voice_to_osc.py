import re
import os
import unicodedata
from difflib import get_close_matches
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import sounddevice as sd
from pocketsphinx import Decoder, get_model_path
from pythonosc.udp_client import SimpleUDPClient

OSC_HOST = "127.0.0.1"
OSC_PORT = 12000
SAMPLE_RATE = 16_000
CHANNELS = 1
CHUNK_SECONDS = 2.0
FUZZY_CUTOFF = 0.68


@dataclass(frozen=True)
class ParsedCommand:
    address: str
    value: str


COLOR_ALIASES: Dict[str, str] = {
    "rojo": "red",
    "verde": "green",
    "azul": "blue",
    "amarillo": "yellow",
    "naranja": "orange",
    "morado": "purple",
    "marron": "orange",
    "blanco": "white",
    "negro": "black",
}

SHAPE_ALIASES: Dict[str, str] = {
    "circulo": "circle",
    "cuadrado": "square",
    "triangulo": "triangle",
    "estrella": "star",
}

ACTION_ALIASES: Dict[str, str] = {
    "iniciar": "start",
    "inicia": "start",
    "comenzar": "start",
    "comienza": "start",
    "activar": "start",
    "detener": "stop",
    "deten": "stop",
    "parar": "stop",
    "pausa": "stop",
    "desactivar": "stop",
    "girar": "spin",
    "giro": "spin",
    "rotar": "spin",
    "rotarlo": "spin",
    "rapido": "faster",
    "lento": "slower",
    "reiniciar": "reset",
    "reinicia": "reset",
    "restablecer": "reset",
    "salir": "exit",
}

PHRASE_ACTIONS: Dict[str, str] = {
    "mas rapido": "faster",
    "mas rapida": "faster",
    "mas lenta": "slower",
    "mas lento": "slower",
    "salir programa": "exit",
    "detener animacion": "stop",
    "iniciar animacion": "start",
}

ENGLISH_BLOCKLIST = {
    "red", "green", "blue", "yellow", "orange", "purple", "white", "black",
    "circle", "square", "triangle", "star",
    "start", "go", "stop", "pause", "spin", "rotate", "faster", "slower", "reset", "exit", "quit",
}

SPANISH_GRAMMAR = """#JSGF V1.0;
grammar comandos;

public <comando> = (<palabra>)+;

<palabra> =
    rojo | verde | azul | amarillo | naranja | morado | marron | blanco | negro |
    circulo | cuadrado | triangulo | estrella |
    iniciar | inicia | comenzar | comienza | activar |
    detener | deten | parar | pausa | desactivar |
    girar | giro | rotar | rotarlo |
    rapido | lento | reiniciar | reinicia | restablecer |
    salir | mas | animacion | programa;
"""

SPANISH_DICT = """rojo R OW HH OW
verde V ER D EY
azul AA Z UW L
amarillo AA M AA R IY Y OW
naranja N AA R AE N HH AA
morado M OW R AA D OW
marron M AA R OW N
blanco B L AE N K OW
negro N EH G R OW
circulo S IY R K UW L OW
cuadrado K W AA D R AA D OW
triangulo T R IY AE N G UW L OW
estrella EH S T R EY Y AA
iniciar IY N IY S IY AA R
inicia IY N IY S IY AA
comenzar K OW M EH N Z AA R
comienza K OW M IY EH N S AA
activar AE K T IY V AA R
detener D EH T EH N EH R
deten D EH T EH N
parar P AA R AA R
pausa P AW S AA
desactivar D EH S AE K T IY V AA R
girar HH IY R AA R
giro HH IY R OW
rotar R OW T AA R
rotarlo R OW T AA R L OW
rapido R AE P IY D OW
lento L EH N T OW
reiniciar R EY IY N IY S IY AA R
reinicia R EY IY N IY S IY AA
restablecer R EH S T AA B L EH S EH R
salir S AA L IY R
mas M AA S
animacion AA N IY M AA S IY OW N
programa P R OW G R AA M AA
"""


def ensure_spanish_grammar_files() -> tuple[Path, Path]:
    assets_dir = Path(__file__).resolve().parent / ".sphinx_es"
    assets_dir.mkdir(exist_ok=True)

    jsgf_path = assets_dir / "comandos_es.jsgf"
    dict_path = assets_dir / "comandos_es.dict"

    jsgf_path.write_text(SPANISH_GRAMMAR, encoding="utf-8")
    dict_path.write_text(SPANISH_DICT, encoding="utf-8")

    return jsgf_path, dict_path


def build_decoder() -> Decoder:
    jsgf_path, dict_path = ensure_spanish_grammar_files()
    model_root = Path(get_model_path())
    hmm_path = model_root / "en-us" / "en-us"

    config = Decoder.default_config()
    config.set_string("-hmm", str(hmm_path))
    config.set_string("-dict", str(dict_path))
    config.set_string("-logfn", os.devnull)

    decoder = Decoder(config)
    decoder.add_jsgf_file("comandos_es", str(jsgf_path))
    decoder.activate_search("comandos_es")
    return decoder


def best_match(token: str, vocabulary: List[str]) -> str:
    if token in vocabulary:
        return token

    candidates = get_close_matches(token, vocabulary, n=1, cutoff=FUZZY_CUTOFF)
    return candidates[0] if candidates else ""


def canonical_tokens(text: str) -> List[str]:
    vocab = list(COLOR_ALIASES) + list(SHAPE_ALIASES) + list(ACTION_ALIASES)
    canonical: List[str] = []
    normalized = normalize_text(text)

    for phrase, action in PHRASE_ACTIONS.items():
        if phrase in normalized:
            canonical.append(action)

    for token in normalized.split():
        if token in ENGLISH_BLOCKLIST:
            continue

        matched = best_match(token, vocab)
        if matched:
            canonical.append(matched)

    return canonical


def normalize_text(text: str) -> str:
    lowered = text.lower().strip()
    lowered = unicodedata.normalize("NFKD", lowered)
    lowered = "".join(char for char in lowered if not unicodedata.combining(char))
    lowered = re.sub(r"[^a-z0-9\s]", "", lowered)
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered


def parse_commands(text: str) -> List[ParsedCommand]:
    words = canonical_tokens(text)
    commands: List[ParsedCommand] = []
    canonical_action_tokens = {"start", "stop", "spin", "faster", "slower", "reset", "exit"}
    actions = [ACTION_ALIASES[word] if word in ACTION_ALIASES else word for word in words if word in ACTION_ALIASES or word in canonical_action_tokens]

    for word in words:
        if word in COLOR_ALIASES:
            commands.append(ParsedCommand("/color", COLOR_ALIASES[word]))
            break

    for word in words:
        if word in SHAPE_ALIASES:
            commands.append(ParsedCommand("/shape", SHAPE_ALIASES[word]))
            break

    if "start" in actions:
        commands.append(ParsedCommand("/anim", "start"))
    elif "stop" in actions:
        commands.append(ParsedCommand("/anim", "stop"))

    if "spin" in actions:
        commands.append(ParsedCommand("/spin", "toggle"))

    if "faster" in actions:
        commands.append(ParsedCommand("/speed", "up"))
    elif "slower" in actions:
        commands.append(ParsedCommand("/speed", "down"))

    if "reset" in actions:
        commands.append(ParsedCommand("/reset", "now"))

    return commands


def capture_audio_chunk() -> tuple[bytes, float]:
    frames = int(SAMPLE_RATE * CHUNK_SECONDS)
    recording = sd.rec(frames, samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="int16")
    sd.wait()

    audio = np.asarray(recording).reshape(-1).astype(np.float32)
    rms = float(np.sqrt(np.mean(np.square(audio)))) if audio.size else 0.0

    # Automatic gain normalization helps pocketsphinx with low microphone input.
    target_rms = 2200.0
    if rms > 1.0:
        gain = min(target_rms / rms, 6.0)
        audio = np.clip(audio * gain, -32768, 32767)

    pcm = audio.astype(np.int16).tobytes()

    # Pocketsphinx expects mono little-endian 16-bit PCM bytes.
    return pcm, rms


def recognize_with_pocketsphinx(decoder: Decoder, pcm_audio: bytes) -> str:
    decoder.start_utt()
    decoder.process_raw(pcm_audio, False, True)
    decoder.end_utt()

    hypothesis = decoder.hyp()
    if hypothesis is None:
        return ""

    return hypothesis.hypstr


def listen_loop(client: SimpleUDPClient) -> None:
    decoder = build_decoder()

    while True:
        user_input = input("\nHablar (Enter) | Salir (q): ").strip().lower()
        if user_input in {"q", "salir"}:
            break

        try:
            audio, rms = capture_audio_chunk()
        except Exception as exc:  # sounddevice can raise PortAudioError on device issues
            print(f"Audio capture error: {exc}")
            continue

        try:
            text = recognize_with_pocketsphinx(decoder, audio)
        except Exception as exc:
            print(f"Sphinx error: {exc}")
            continue

        normalized = normalize_text(text)
        if rms < 250.0:
            print("Audio muy bajo.")
            continue

        if not normalized:
            print("No entendido.")
            continue

        print(f"Escuchado: {normalized}")

        if "exit" in [ACTION_ALIASES[word] if word in ACTION_ALIASES else word for word in canonical_tokens(normalized)]:
            break

        commands = parse_commands(normalized)
        if not commands:
            print("Sin comando valido.")
            continue

        sent_commands = []
        for command in commands:
            client.send_message(command.address, command.value)
            sent_commands.append(f"{command.address} {command.value}")

        client.send_message("/text", normalized)
        print("Enviado: " + " | ".join(sent_commands))


def main() -> None:
    client = SimpleUDPClient(OSC_HOST, OSC_PORT)
    print(f"OSC -> {OSC_HOST}:{OSC_PORT}")
    listen_loop(client)


if __name__ == "__main__":
    main()
