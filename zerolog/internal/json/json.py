from datetime import datetime
from typing import Any, List

import zerolog
from zerolog import constants
from zerolog.internal.util.time import convert_offset

LEFT_BRACE = 123  # {

_hex = "0123456789abcdef"
_no_escape_table: List[bool] = [False] * 256

for i in range(0x00, 0x7F):
    # 0x20 space 0x5c \ 0x22 "
    _no_escape_table[i] = i >= 0x20 and i != 0x5C and i != 0x22


class Encoder:
    # append_begin_marker inserts a map start into the dst byte array.
    @staticmethod
    def append_begin_marker(dst: bytes) -> bytes:
        dst += b"{"
        return dst

    # append_end_marker inserts a map end into the dst byte array.
    @staticmethod
    def append_end_marker(dst: bytes) -> bytes:
        dst += b"}"
        return dst

    # append_any marshals the input to a string and
    # appends the encoded string to the input byte slice.
    def append_any(self, dst: bytes, val: Any) -> bytes:
        try:
            m = zerolog.AnyMarshalFunc(val)
        except Exception as e:
            return self.append_string(dst, f"marshaling error: {e}")

        dst += f"{m}".encode()
        return dst

    # append_bool converts the input bool to a string and
    # appends the encoded string to the input byte slice.
    @staticmethod
    def append_bool(dst: bytes, val: bool) -> bytes:
        dst += f"{str(val).lower()}".encode()
        return dst

    # append_floats encodes the input bools to json and
    # appends the encoded string list to the input byte slice.
    @staticmethod
    def append_bools(dst: bytes, vals: List[bool]) -> bytes:
        if len(vals) == 0:
            dst += b"[]"
        dst += b"["
        dst += f"{str(vals[0]).lower()}".encode()
        if len(vals) > 1:
            for val in vals[1:]:
                dst += b","
                dst += f"{str(val).lower()}".encode()
        dst += b"]"
        return dst

    # append_float converts the input float to a string and
    # appends the encoded string to the input byte slice.
    @staticmethod
    def append_float(dst: bytes, val: float) -> bytes:
        dst += f"{str(val)}".encode()
        return dst

    # append_floats encodes the input floats to json and
    # appends the encoded string list to the input byte slice.
    @staticmethod
    def append_floats(dst: bytes, vals: List[float]) -> bytes:
        if len(vals) == 0:
            dst += b"[]"
        dst += b"["
        dst += f"{str(vals[0])}".encode()
        if len(vals) > 1:
            for val in vals[1:]:
                dst += b","
                dst += f"{str(val)}".encode()
        dst += b"]"
        return dst

    # append_int converts the input int to a string and
    # appends the encoded string to the input byte slice.
    @staticmethod
    def append_int(dst: bytes, val: int) -> bytes:
        dst += f"{str(val)}".encode()
        return dst

    # append_ints encodes the input ints to json and
    # appends the encoded string list to the input byte slice.
    @staticmethod
    def append_ints(dst: bytes, vals: List[int]) -> bytes:
        if len(vals) == 0:
            dst += b"[]"
        dst += b"["
        dst += f"{str(vals[0])}".encode()
        if len(vals) > 1:
            for val in vals[1:]:
                dst += b","
                dst += f"{str(val)}".encode()
        dst += b"]"
        return dst

    # append_line_break appends a line break.
    @staticmethod
    def append_line_break(dst: bytes) -> bytes:
        dst += b"\n"
        return dst

    # append_key appends a new key to the output JSON.
    def append_key(self, dst: bytes, key: str) -> bytes:
        if dst[len(dst) - 1] != LEFT_BRACE:
            dst += b","

        dst = self.append_string(dst, key)
        dst += b":"
        return dst

    @staticmethod
    def append_string(dst: bytes, s: str) -> bytes:
        dst += b'"'
        for i, _ in enumerate(s):
            # Check if the character needs encoding. Control characters, slashes,
            # and the double quote need json encoding. Bytes above the ascii
            # boundary needs utf8 encoding.
            try:
                if not _no_escape_table[ord(s[i])]:
                    # We encountered a character that needs to be encoded. Switch
                    # to complex version of the algorithm.
                    dst = append_string_complex(dst, s, i)
                    dst += b'"'
                    return dst
            except IndexError:
                dst = append_string_complex(dst, s, i)
                dst += b'"'
                return dst
        # The string has no need for encoding and therefore is directly
        # appended to the byte slice.
        dst += str.encode(s)
        dst += b'"'
        return dst

    # append_strings encodes the input strings to json and
    # appends the encoded string list to the input byte slice.
    def append_strings(self, dst: bytes, vals: List[str]) -> bytes:
        if len(vals) == 0:
            dst += b"[]"
            return dst
        dst += b"["
        dst = self.append_string(dst, vals[0])
        if len(vals) > 1:
            for val in vals[1:]:
                dst += b","
                dst = self.append_string(dst, val)
        dst += b"]"
        return dst

    # append_time formats the input time with the given format
    # and appends the encoded string to the input byte slice.
    def append_time(self, dst: bytes, t: datetime, fmt: str) -> bytes:
        match fmt:
            case constants.TimeFormatUnix:
                dst = self.append_int(dst, int(t.timestamp()))
            case constants.TimeFormatUnixMs:
                dst = self.append_int(dst, int(t.timestamp() * 1000))
            case constants.TimeFormatUnixMicro:
                dst = self.append_int(dst, int(t.timestamp() * 1000000))
            case constants.TimeFormatRFC3339:
                s = f'{t.isoformat(timespec="seconds")}'
                dst = self.append_string(dst, convert_offset(s))
            case constants.TimeFormatRFC3339Ms:
                s = f'{t.isoformat(timespec="milliseconds")}'
                dst = self.append_string(dst, convert_offset(s))
            case constants.TimeFormatRFC3339Micro:
                s = f'{t.isoformat(timespec="microseconds")}'
                dst = self.append_string(dst, convert_offset(s))
            case _:
                dst = self.append_string(dst, t.strftime(fmt))

        return dst

    # append_object_data takes in an object that is already in a byte array
    # and adds it to the dst.
    @staticmethod
    def append_object_data(dst: bytes, o: bytes) -> bytes:
        # Three conditions apply here:
        # 1. new content starts with '{' - which should be dropped   OR
        # 2. new content starts with '{' - which should be replaced with ','
        #    to separate with existing content OR
        # 3. existing content has already other fields
        if o[0] == LEFT_BRACE:
            if len(dst) > 1:
                dst += b","
            o = o[1:]
        elif len(dst) > 1:
            dst += b","
        dst += o
        return dst


# append_string_complex is used by append_string to take over an in
# progress JSON string encoding that encountered a character that needs
# to be encoded.
def append_string_complex(dst: bytes, s: str, i: int) -> bytes:
    start = 0
    while i < len(s):
        b = s[i]
        if b > "\x80":
            size = len(s.encode())
            i += size
            continue
        if _no_escape_table[ord(b)]:
            i += 1
            continue
        # We encountered a character that needs to be encoded.
        # Let's append the previous simple characters to the byte slice
        # and switch our operation to read and encode the remainder
        # characters byte-by-byte.
        if start < i:
            dst += s[start:i].encode()
        match b:
            case "\x22" | "\x5c":  # " and space
                dst += f"\\{b}".encode()
            case "\x08":  # \b backspace
                dst += f"\\b".encode()
            case "\x0c":  # \f form feed
                dst += f"\\f".encode()
            case "\x0a":  # \n line feed
                dst += f"\\n".encode()
            case "\x0d":  # \r carriage return
                dst += f"\\r".encode()
            case "\x09":  # \t horizontal tab
                dst += f"\\t".encode()
            case _:
                dst += b"\\u00"
                dst += _hex[int.from_bytes(b.encode()) >> 4].encode()
                dst += _hex[int.from_bytes(b.encode()) & 0xF].encode()
        i += 1
        start = i
    if start < len(s):
        dst += s[start:].encode()
    return dst
