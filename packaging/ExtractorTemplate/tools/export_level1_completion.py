"""Export the pinned world-coordinate table used by A50A."""
from pathlib import Path
import hashlib
from inventory_rom import ROM_HASH
root=Path(__file__).resolve().parents[1]
rom=(root/'local/rolo.md').read_bytes()
assert hashlib.sha256(rom).hexdigest()==ROM_HASH
# Bounded 80-selector native state domain; complete external table extent remains unverified.
data=rom[0x4ad9a:0x4ad9a+160]
(root/'src/core/level1_completion_data.hpp').write_text('#pragma once\n#include <array>\n#include <cstdint>\nnamespace rolo { inline constexpr std::array<std::uint8_t,160> world_coordinate_bytes{{'+','.join(map(str,data))+'}}; }\n')
