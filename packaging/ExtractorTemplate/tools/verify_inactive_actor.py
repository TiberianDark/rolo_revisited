"""Complete static equivalence proof for the leaf routine A84C. No ROM execution."""
import hashlib,json,re
from pathlib import Path
from m68k_static import Decoder
PIN='9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9'
def verify(project):
    rom=(project/'local/rolo.md').read_bytes()
    assert hashlib.sha256(rom).hexdigest()==PIN
    assert rom[0xa84c:0xa84e]==bytes.fromhex('4e75')
    instruction=Decoder(rom,0xa84c).decode()
    assert instruction['mnemonic']=='RTS' and instruction['size']==2
    native_path=project/'src/core/actor_defeat.hpp';native=native_path.read_text()
    assert re.search(r'inactive_actor_callback\s*=\s*0xa84c\s*;',native)
    match=re.search(r'inline void inactive_actor_update\(ActorState&\)\s*\{([^{}]*)\}',native)
    assert match and not match[1].strip(),'Native function is no longer empty'
    host_path=project/'src/core/level1_enemy_slice.hpp';host=host_path.read_text()
    assert re.search(r'if\(callback==0xa84c\)return;',host),'Native dispatch is no longer a direct return'
    return dict(address=0xa84c,hex='00A84C',status='verified green: complete inactive-actor callback',verification_status='verified',rom_sha256=PIN,
        range=['00A84C','00A84E'],original_bytes='4e75',instruction_count=1,
        contract='Return to caller without reading/writing actor state, globals, artwork, sound or gameplay state. Windows function return replaces the original call/return mechanism.',
        proof='The whole original routine is one RTS. Native helper has an empty body; the live shared-world callback dispatch directly returns for this identity. No dependencies, input-dependent branches or additional instructions exist within the routine.',
        scope='Complete local routine semantics for every actor/input state; does not certify callers, scheduling, animation or CPU/device timing.',
        native_sources=['src/core/actor_defeat.hpp','src/core/level1_enemy_slice.hpp'],source_sha256={str(p.relative_to(project)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in (native_path,host_path)})
if __name__=='__main__':
    project=Path(__file__).resolve().parents[1];result=verify(project)
    (project/'docs/stage9/inactive-actor-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('hex','status','original_bytes','instruction_count')}))
