"""Pinned original five-sprite HUD templates; immutable data, no code execution."""
import hashlib
from pathlib import Path
from inventory_rom import ROM_HASH
p=Path(__file__).resolve().parents[1];rom=(p/'local/rolo.md').read_bytes();assert hashlib.sha256(rom).hexdigest()==ROM_HASH
values=','.join(map(str,rom[0x5216:0x523e]))
(p/'src/core/status_hud_templates.hpp').write_text('#pragma once\n#include <array>\n#include <cstdint>\nnamespace rolo {inline constexpr std::array<std::uint8_t,40> status_hud_templates{'+values+'};}\n',encoding='utf-8')
