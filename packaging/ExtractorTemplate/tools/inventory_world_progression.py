"""Extract ROM jigsaw cell/edge data and scoped selector contexts, offline."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from inventory_rom import ROM_HASH, inventory

def edge_glyph(edge_code, own_complete, neighbour_complete, edge_offset, tables):
    """Typed transcription of only the A608 glyph choice, not a CPU interpreter."""
    if edge_code not in range(4) or edge_offset not in (0,2,4,6):
        raise ValueError('Outside checked edge domain')
    index=edge_offset//2
    if not own_complete:
        return tables[0xa65e if edge_code==2 and neighbour_complete else 0xa656][index]
    if edge_code==2 and not neighbour_complete:
        return tables[0xa666][index]
    return 0


def catalogue(rom, project):
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('Unexpected ROM revision')
    inv,_=inventory(rom,project/'docs')
    records=[];cells=[];mask_cursor=0x13e59
    # Three descriptors are bounded by the inspected zero-long terminator.
    for address in (0x4baaa,0x4bab2,0x4baba):
        source,width,coordinate_word=struct.unpack_from('>IHH',rom,address)
        ids=rom[source:source+width*4]
        if len(ids)!=width*4:raise ValueError('Truncated jigsaw cells')
        rows=[]
        for row in range(4):
            line=[]
            for column in range(width):
                index=row*width+column;mask=rom[mask_cursor];level=ids[index]
                previous_width,previous_coordinate=struct.unpack_from('>HH',rom,address-4)
                next_coordinate=struct.unpack_from('>H',rom,address+14)[0]
                delta_words={0:1,2:0xffff,
                    4:(width+coordinate_word-next_coordinate)&0xffff if row==3 else width,
                    6:-(previous_width+previous_coordinate-coordinate_word)&0xffff if row==0 else (-width)&0xffff}
                neighbours=[]
                for edge_offset,word in delta_words.items():
                    delta=word if word<0x8000 else word-0x10000
                    neighbour_address=source+index+delta
                    if not 0<=neighbour_address<len(rom):raise ValueError('Jigsaw neighbour address outside ROM')
                    neighbours.append(dict(edge_offset=edge_offset,delta_word=word,address=neighbour_address,
                        selector=rom[neighbour_address],completion_flag_read_possible=((mask>>edge_offset)&3)==2))
                item=dict(descriptor=address,row=row,column=column,level_selector=level,
                    source_address=source+index,edge_mask_address=mask_cursor,edge_mask=mask,
                    edge_codes={str(offset):(mask>>offset)&3 for offset in (0,2,4,6)},neighbours=neighbours)
                if level:
                    pointer=0x4ad9a+level*2;x,y=rom[pointer:pointer+2]
                    item['world_coordinate_record']=dict(address=pointer,raw=rom[pointer:pointer+2].hex(),
                        x_word=((x<<4)-8)&0xffff,y_word=((y<<4)-8)&0xffff,
                        first_byte_ff_suppresses_coordinate_update=x==255)
                cells.append(item);line.append(level);mask_cursor+=1
            rows.append(line)
        records.append(dict(address=address,source=source,width=width,coordinate_word=coordinate_word,
            rows=rows,raw_ids=ids.hex(),ids_sha256=hashlib.sha256(ids).hexdigest()))
    if rom[0x4bac2:0x4bac6]!=bytes(4):raise ValueError('Jigsaw terminator differs')
    selectors=sorted({cell['level_selector'] for cell in cells if cell['level_selector']})
    contexts=json.loads((project/'docs/stage9/indexed-inline-targets.json').read_text(encoding='utf-8'))
    context=next(c for c in contexts if c['dispatch']=='A66E')
    calls=[c['address'] for c in inv['calls'] if c['target']==0xa608]
    if set(calls)!={int(p['call'],16) for p in context['producer_contexts']}:
        raise ValueError('Additional observed jigsaw edge callers need assessment')
    tables={address:list(struct.unpack_from('>4H',rom,address)) for address in (0xa656,0xa65e,0xa666)}
    decisions=[dict(edge_code=code,own_complete=own,neighbour_complete=neighbour,edge_offset=offset,
                    glyph=edge_glyph(code,own,neighbour,offset,tables))
               for code in range(4) for own in (False,True) for neighbour in (False,True) for offset in (0,2,4,6)]
    return dict(rom_sha256=ROM_HASH,records=records,cells=cells,
        glyph_tables=[dict(address=address,words=list(struct.unpack_from('>4H',rom,address)),raw=rom[address:address+8].hex())
                      for address in (0xa656,0xa65e,0xa666)],
        glyph_decisions=decisions,
        indexed_continuation=context,known_edge_helper_calls=calls,
        completion_helper_calls=[c for c in inv['calls'] if c['target']==0xa50a],
        counts=dict(cells=len(cells),nonzero_cells=sum(bool(c['level_selector']) for c in cells),
            zero_cells=sum(not c['level_selector'] for c in cells),distinct_nonzero_selectors=len(selectors),
            descriptors=len(records),neighbour_byte_reads=sum(len(c['neighbours']) for c in cells),
            conditional_neighbour_completion_reads=sum(n['completion_flag_read_possible'] for c in cells for n in c['neighbours']),
            glyph_decision_cases=len(decisions)),
        conditional_neighbour_selector_domain=sorted({n['selector'] for c in cells for n in c['neighbours'] if n['completion_flag_read_possible']}),
        nonzero_selector_domain=selectors,
        scope='70 nonzero jigsaw cell selectors in80 cells, not proof of70 distinct playable levels or completion routing. Coordinate rows are only the70 referenced entries. Static data/expression extraction; no original CPU or gameplay execution.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('rom')
    parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1]);args=parser.parse_args()
    result=catalogue(Path(args.rom).read_bytes(),args.project)
    (args.project/'docs/stage9/world-jigsaw-data.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result['counts']))


if __name__=='__main__':main()
