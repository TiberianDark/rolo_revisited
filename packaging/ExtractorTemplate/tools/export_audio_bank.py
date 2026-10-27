"""Extract pinned sound data and inspect sequence records, without CPU execution.

Record boundaries translated from Z80 driver 0835, 087D, 0914, 095C.
This does not synthesize audio or certify channel/envelope/timing semantics.
"""
from pathlib import Path
import hashlib
import json
from rolo_codec import decode_backward_lz
from inventory_rom import ROM_HASH


def sequence_records(data):
    at = 1 if data and data[0] < 128 else 0
    initial = at
    running = None
    records = []
    while at < len(data):
        start = at
        if data[at] & 128:
            running = data[at]
            at += 1
        if running is None:
            raise ValueError(f'No running command at {start}')
        if running == 0xfc:
            records.append(dict(offset=start, command=running, end=True,
                                stop=at < len(data) and data[at] == 0x80))
            return dict(initial_byte=data[0] if initial else None,
                        records=records, end_offset=at)
        if running & 0xf0 not in (0x80, 0x90, 0xc0):
            raise ValueError(f'Unreviewed command {running:02x} at {start}')
        if at + 2 > len(data):
            raise ValueError(f'Truncated record at {start}')
        value, delay = data[at:at+2]
        at += 2
        records.append(dict(offset=start, command=running, channel=running & 15,
                            value=value, delay_byte=delay))
    raise ValueError('Sequence has no FC end marker')


def main():
    project = Path(__file__).resolve().parents[1]
    rom = (project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest() != ROM_HASH:
        raise ValueError('Pinned ROM hash mismatch')
    out = project/'assets/extracted/audio'
    out.mkdir(parents=True, exist_ok=True)
    # Reproduce byte placement only: opaque driver upload followed by 32 patches.
    # Patch pointers refer ten bytes before each appended record; register-indexed
    # reads start at +12. Preserve that overlap rather than inventing a layout.
    driver = rom[0x7e7a0:0x7e7a0+0x1120] + rom[0x7c37e:0x7c37e+0x480]
    header = ['#pragma once', '#include <array>', '#include <cstdint>',
              'namespace rolo::audio_data {']
    def array(name, data):
        header.append(f'inline constexpr std::array<std::uint8_t,{len(data)}> {name}{{{{')
        header.extend(','.join(map(str, data[i:i+32]))+',' for i in range(0,len(data),32))
        header.append('}};')
    patches=[]
    for program in range(32):
        base=int.from_bytes(driver[0x392+2*program:0x394+2*program], 'little')
        if base+46>len(driver):
            raise ValueError('Instrument outside initialized sound data')
        patches.extend(driver[base:base+46])
    array('patches', patches)
    end=driver.index(0,0xbac)
    array('registers',driver[0xbac:end])
    array('frequency_low',driver[0x3f2:0x446])
    array('frequency_high',driver[0x446:0x49a])
    header.append('}')
    (project/'src/core/audio_bank_data.hpp').write_text('\n'.join(header)+'\n')
    def pointer(at):
        value = int.from_bytes(rom[at:at+4], 'big')
        if value >= len(rom):
            raise ValueError(f'Pointer outside ROM: {value:x}')
        return value
    music = []
    sequences=[]
    for sound_id in range(33):
        source = pointer(0x78a92 + 4*sound_id)
        data, _ = decode_backward_lz(rom, source)
        sequences.append(data)
        filename = f'music-{sound_id:02d}.seq'
        (out/filename).write_bytes(data)
        entry = dict(id=sound_id, source=source, file=filename, bytes=len(data),
                     sha256=hashlib.sha256(data).hexdigest())
        try:
            trace = sequence_records(data)
            trace_name = f'music-{sound_id:02d}-records.json'
            (out/trace_name).write_text(json.dumps(trace, indent=2)+'\n')
            entry.update(records=len(trace['records']), trace=trace_name,
                         structure='decoded')
        except ValueError as error:
            entry.update(structure='needs-review', reason=str(error))
        music.append(entry)
    blob=bytearray();offsets=[]
    for data in sequences:
        offsets.append(len(blob));blob.extend(data)
    offsets.append(len(blob))
    lines=['#pragma once','#include <array>','#include <cstdint>','namespace rolo::music_bank {']
    def music_array(name, data, typ='std::uint8_t'):
        lines.append(f'inline constexpr std::array<{typ},{len(data)}> {name}{{{{')
        lines.extend(','.join(map(str,data[i:i+32]))+',' for i in range(0,len(data),32))
        lines.append('}};')
    music_array('bytes',blob);music_array('offsets',offsets,'std::uint32_t')
    music_array('level_pairs',rom[0x4ae3a:0x4ae3a+160])
    music_array('cycle',rom[0x5db8:0x5dc8])
    music_array('delays',[int.from_bytes(rom[a:a+2],'big') for a in range(0x5dac,0x5db8,2)],'std::uint16_t')
    lines.append('}')
    (project/'src/core/music_sequence_data.hpp').write_text('\n'.join(lines)+'\n')
    assignments=dict(source='ROM 005D08..005DAA and 005CE6..005D06',
        cycle=list(rom[0x5db8:0x5dc8]),
        scenes={'title':dict(music=2,loop=True,evidence='initialize_entrance_scene / 165E'),
                'jigsaw_map':dict(music=16,loop=True,evidence='initialize_world_front_end / 1A6E'),
                'game_over':dict(music=21,loop=False,evidence='initialize_game_over_scene / 15AA'),
                'level_complete':dict(music=23,loop=False,evidence='level1_progress.hpp completion handoff'),
                'attract':dict(music=[9,10],loop=True,evidence='initialize_attract_scene; credits sign branch')} ,
        levels=[])
    for selector in range(80):
        cue,tune=rom[0x4ae3a+selector*2:0x4ae3c+selector*2]
        assignments['levels'].append(dict(selector=selector,entry_cue=None if cue==255 else cue,
            cue_delay_frames=None if cue==255 else int.from_bytes(rom[0x5dac+(cue-27)*2:0x5dae+(cue-27)*2],'big'),
            tune='rotating_playlist' if tune==255 else tune,
            rule='Entry cue/delay only when cue differs from previous cue; otherwise delayed tune on next update. IDs 8/14 become 9 on original visited/reward branch.'))
    (out/'music-assignments.json').write_text(json.dumps(assignments,indent=2)+'\n')
    effects = []
    effect_bytes=bytearray()
    for sound_id in range(91):
        source = pointer(0x78926 + 4*sound_id)
        payload = rom[source:source+23]
        if len(payload) != 23:
            raise ValueError('Truncated effect descriptor')
        effects.append(dict(id=sound_id, source=source, payload_hex=payload.hex()))
        effect_bytes.extend(payload)
    lines=['#pragma once','#include <array>','#include <cstdint>','namespace rolo::effect_bank {',
           f'inline constexpr std::array<std::uint8_t,{len(effect_bytes)}> descriptors{{{{']
    lines.extend(','.join(map(str,effect_bytes[i:i+32]))+',' for i in range(0,len(effect_bytes),32))
    lines+=['}};','}']
    (project/'src/core/sound_effect_data.hpp').write_text('\n'.join(lines)+'\n')
    report = dict(rom_sha256=ROM_HASH, music=music, effects=effects,
                  instruments=32, instrument_record_stride=36,
                  instrument_window_bytes=46,
                  level_sound_pairs=[dict(selector=i, music=rom[0x4ae3a+2*i],
                                         effect=rom[0x4ae3b+2*i]) for i in range(80)],
                  status='Data extraction and record boundaries only; audible playback pending.',
                  driver_review={'initialize':'0835', 'commands':'087D-08F2',
                                 'delay':'0914', 'running_command':'095C-097A'})
    (out/'bank.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f"33 music IDs, 91 effect descriptors, 80 level pairs; "
          f"{sum(m['structure']=='decoded' for m in music)}/33 record streams decoded.")


if __name__ == '__main__':
    main()
