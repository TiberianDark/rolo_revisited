"""Bounded semantic translation of Rolo's backwards LZ loader at $A75A.

This decodes a data format. It does not execute CPU instructions.
"""
import struct


class DecodeError(ValueError):
    pass


class ReverseBits:
    def __init__(self,data,start,end):
        self.data,self.lower,self.pointer=data,start,end
        self.state=1
        self.bits_read=0

    def bit(self):
        carry=self.state&1
        self.state >>= 1
        if self.state == 0:
            if self.pointer-4 < self.lower: raise DecodeError('Bitstream exhausted')
            self.pointer -= 4
            word=struct.unpack_from('>I',self.data,self.pointer)[0]
            carry=word&1
            self.state=(word>>1)|0x80000000
        self.bits_read += 1
        return carry

    def value(self,count):
        if not 0 <= count <= 24: raise DecodeError('Invalid bit width')
        value=0
        for _ in range(count): value=(value<<1)|self.bit()
        return value


def decode_backward_lz(data,source,max_output=0x10000):
    if source < 0 or source+12 > len(data): raise DecodeError('Truncated block header')
    encoded_size=struct.unpack_from('>I',data,source)[0]
    if encoded_size < 16 or encoded_size%4 or source+encoded_size > len(data):
        raise DecodeError('Invalid encoded block size')
    end=source+encoded_size
    trailer=struct.unpack_from('>I',data,end-4)[0]
    output_size,skip=trailer>>8,trailer&255
    if not 0 < output_size <= max_output or skip > 32: raise DecodeError('Invalid decoded size or padding')
    widths=list(data[source+4:source+8])
    if any(not 1 <= width <= 15 for width in widths): raise DecodeError('Invalid distance widths for signed 16-bit source index')
    bits=ReverseBits(data,source+8,end-4)
    if skip:
        for _ in range(skip): bits.bit()
    output=bytearray(output_size)
    cursor=output_size
    literals=matches=0
    while cursor > 0:
        if bits.bit() == 0:
            # Consecutive 2-bit groups: 3 extends the literal run.
            count=0
            while True:
                part=bits.value(2); count += part
                if count >= output_size: raise DecodeError('Literal run exceeds output')
                if part != 3: break
            count += 1
            if count > cursor: raise DecodeError('Literal run crosses output start')
            for _ in range(count):
                value=bits.value(8)
                cursor -= 1; output[cursor]=value
            literals += 1
            if cursor == 0: break
        # Branch to match handling after literal run, or directly for a 1 bit.
        selector=bits.value(2)
        if selector == 3:
            distance_count=7 if bits.bit() == 0 else widths[3]
            distance=bits.value(distance_count)
            count=selector
            while True:
                part=bits.value(3); count += part
                if count >= output_size: raise DecodeError('Match run exceeds output')
                if part != 7: break
        else:
            distance=bits.value(widths[selector])
            count=selector
        count += 2
        if count > cursor: raise DecodeError('Match run crosses output start')
        # 68000 MOVE.B (d16,A3),-(A3): source EA evaluated before predecrement.
        # Each byte refers to the prior cursor + distance, and overlap is intentional.
        for _ in range(count):
            source_index=cursor+distance
            if not cursor <= source_index < output_size: raise DecodeError('Back-reference outside decoded suffix')
            value=output[source_index]
            cursor -= 1; output[cursor]=value
        matches += 1
    return bytes(output), {'codec':'rolo-backward-lz-A75A-v1','loader':0xa75a,
                          'source_start':source,'source_end_exclusive':end,'encoded_size':encoded_size,
                          'decoded_size':output_size,'padding_bits':skip,'distance_widths':widths,
                          'bitstream_lowest_read_offset':bits.pointer,'bits_read':bits.bits_read,
                          'literal_runs':literals,'match_runs':matches}
