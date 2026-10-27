"""Evidence-scoped transporter completion gates; never promote fixtures to fidelity."""
import hashlib,json
from pathlib import Path

def catalogue(project):
    paths=['src/core/level1_transport_world.hpp','src/core/transporter_continuation.hpp','src/core/player_trigger_continuation.hpp','src/main.cpp','docs/stage9/level1-transport-contract.json','docs/stage9/word-transfer-queue-contract.json']
    sources={p:(project/p).read_text(encoding='utf-8') for p in paths}
    main=sources['src/main.cpp'];host=sources['src/core/level1_transport_world.hpp']
    gates=[
        ('Activation and marker lifecycle','connected_partial','Class8 allocation, literal0x17 consumption, retained trigger and resumed925C scanner are connected.','Close allocation failure/re-entry and complete upstream caller domains.'),
        ('Destination and actor handoff','connected_partial','First matching11xx marker, saved destination, live controlled actor and original reset order are implemented.','Close all reachable parameter, actor identity and malformed/missing destination caller paths.'),
        ('Palette black wait and restore','connected_partial','Eight eligible black phases, live artwork palette and nonblocking fade-in are connected.','Original interrupt eligibility across menu/pause and independent input-reference timing remain open.'),
        ('Companion repositioning','connected_partial','Rolo-onlyAC34 direct callback/history placement is translated and bound.','Full companion identities/history lifecycle and original-reference comparison remain open.'),
        ('Sprite publication consumption','implementation_gap','Host prepares and copies sprite views, but main has no published_sprites reference.','Replace placeholder staging with original live group/chunk/culling/capacity semantics and consume publication in renderer.'),
        ('Scroll publication consumption','implementation_gap','Host stores horizontal/vertical transport publication; main has no transport_host scroll buffer consumer.','Connect ordered scroll publication to renderer, preserving original foreground/background coordinate domains.'),
        ('Graphics transfer lifecycle','implementation_gap','Original queue format and reset/flush contracts are mapped; host copies vectors instead of modeled semantic transfer completion.','Bind original queue producer ordering, source ownership and native publication completion.'),
        ('Transport sound','implementation_gap','transport_sound stores world.sound only.','Implement sound1D through the native audio pipeline with original timing.'),
        ('Independent original comparison','reference_gap','Existing SDL fixture explicitly says full_original_reference_verified=false.','Compare original input/frame cases and failure paths without executing ROM instructions in this project.'),
    ]
    if 'published_sprites' in main: raise ValueError('Renderer changed: reassess publication gap')
    if 'world.sound=command' not in host: raise ValueError('Sound binding changed: reassess gap')
    return dict(scope='Completion audit of entire Level1 transporter; connected helpers are not full feature completion.',fully_faithful=False,green=False,
        source_sha256={p:hashlib.sha256((project/p).read_bytes()).hexdigest() for p in paths},
        gates=[dict(name=n,status=s,evidence=e,pending=p) for n,s,e,p in gates],
        remaining=['All nine feature gates must be supported at their full scope before green.','Tests for local helpers do not establish renderer consumption or independent original fidelity.'])

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]
    (p/'docs/stage9/transporter-readiness-contract.json').write_text(json.dumps(catalogue(p),indent=2)+'\n')
    print('Transporter: nine scoped completion gates; full-feature green=false')
