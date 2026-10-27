"""Independently compare bitstream traversal and verify generated stage-2 assets.

Requires the same user-supplied ROM; uses only the Python standard library.
"""
import argparse
import hashlib
import json
import io
import struct
import unittest
from pathlib import Path
from romtool import read_rom
from rolo_extract import font_evidence
from rolo_codec import decode_backward_lz,DecodeError


def reference_decode(data,source):
    # Alternate formulation: directly address packed bits, grow a reverse suffix.
    # No sentinel shifts or fixed destination buffer; still derived from the same
    # inspected loader, so this is not independent original-hardware verification.
    encoded=struct.unpack_from('>I',data,source)[0]; end=source+encoded
    footer=struct.unpack_from('>I',data,end-4)[0]
    size,bit_number=footer>>8,footer&255
    widths=data[source+4:source+8]
    def take(width):
        nonlocal bit_number
        result=0
        for _ in range(width):
            pointer=end-8-(bit_number//32)*4
            if pointer<source+8: raise DecodeError('Reference bitstream exhausted')
            packed=struct.unpack_from('>I',data,pointer)[0]
            result=(result<<1)|((packed>>(bit_number%32))&1)
            bit_number+=1
        return result
    suffix=[]
    while len(suffix)<size:
        if take(1)==0:
            count=1
            while True:
                chunk=take(2); count+=chunk
                if chunk!=3: break
            if len(suffix)+count>size: raise DecodeError('Reference literal overrun')
            suffix.extend(take(8) for _ in range(count))
            if len(suffix)==size: break
        selector=take(2); count=selector+2
        if selector==3:
            distance=take(widths[3] if take(1) else 7)
            while True:
                chunk=take(3); count+=chunk
                if chunk!=7: break
        else: distance=take(widths[selector])
        if len(suffix)+count>size or distance>=len(suffix): raise DecodeError('Reference match invalid')
        for _ in range(count): suffix.append(suffix[-1-distance])
    return bytes(reversed(suffix))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom'); parser.add_argument('--assets',required=True); parser.add_argument('--out',required=True)
    args=parser.parse_args()
    suite=unittest.TestLoader().discover(str(Path(__file__).resolve().parent),pattern='test_*.py')
    test_output=io.StringIO()
    test_result=unittest.TextTestRunner(stream=test_output,verbosity=0).run(suite)
    if not test_result.wasSuccessful(): parser.exit(1,test_output.getvalue())
    data=read_rom(args.rom); font_evidence(data)
    assets=Path(args.assets); manifest=json.loads((assets/'stage2.manifest.json').read_text())
    bank_results=[]
    for bank in manifest['banks']:
        name=bank['asset_id'].split('research.',1)[1]
        decoded,evidence=decode_backward_lz(data,bank['source_start'])
        alternate=reference_decode(data,bank['source_start'])
        if decoded!=alternate or decoded!=(assets/(name+'.tiles')).read_bytes(): raise ValueError('Decoded bank differs')
        if hashlib.sha256(decoded).hexdigest()!=bank['sha256']: raise ValueError('Bank hash differs')
        if evidence['bitstream_lowest_read_offset']!=bank['source_start']+8: raise ValueError('Unread complete payload words')
        bank_results.append({'asset':name,'decoded_size':len(decoded),'tile_count':len(decoded)//32,
                             'sha256':bank['sha256'],'alternate_bit_reader_matches':True})
    for layer in manifest['layers']:
        name=layer['asset_id'].split('research.',1)[1]
        if (assets/(name+'.tilemap')).read_bytes()!=data[layer['source']:layer['source']+layer['size']]:
            raise ValueError('Raw tilemap differs')
    groups=json.loads((assets/'initial-object-groups.json').read_text())
    if len(groups['definitions'])!=7 or groups['observed_group_words']!=[0x36c8,0x38c8,0x3ac8]:
        raise ValueError('Initial-state templates differ')
    report={'status':'passed','python_unit_tests_passed':test_result.testsRun,'banks':bank_results,
            'raw_tilemaps_match_rom':True,'initial_templates_classified':7,
            'decoder_reference_scope':'different bit traversal and output algorithm; both derived from the same ROM loader',
            'hardware_comparison_performed':False,'native_cpp_compiled':False,'cpp_tests_executed':False,
            'sdl_preview_executed':False,'gameplay_ported':False}
    output=Path(args.out); output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__': main()
