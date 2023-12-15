import zerolog.internal.json as json
from .encoder import Encoder

enc: Encoder = json.Encoder()


def decode_if_binary_to_string(inp: bytes) -> str:
    return inp.decode("utf-8")
