from datetime import datetime
from typing import Any, List

import zerolog
from zerolog import constants

LEFT_BRACE = 123  # {


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
        for i in s:
            dst += str.encode(i)

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
                dst = self.append_string(dst, f'{t.isoformat(timespec="seconds")}Z')
            case constants.TimeFormatRFC3339Ms:
                dst = self.append_string(
                    dst, f'{t.isoformat(timespec="milliseconds")}Z'
                )
            case constants.TimeFormatRFC3339Micro:
                dst = self.append_string(
                    dst, f'{t.isoformat(timespec="microseconds")}Z'
                )
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
