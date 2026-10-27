#pragma once
#include <cstdint>
#include <fstream>
#include <optional>
#include <string>
#include <vector>

namespace rolo {
struct PreviewPixels {
    std::uint32_t kind{}, source{}, palette{}, width{}, height{};
    std::vector<std::uint8_t> rgba;
};
// Bounded asset data reader, independent of SDL and ROM execution.
inline std::optional<std::vector<PreviewPixels>> load_preview_assets(const std::string& path) {
    std::ifstream file(path,std::ios::binary);
    char magic[8]{};
    if (!file.read(magic,8) || std::string(magic,8)!=std::string("RLOAS01\0",8)) return std::nullopt;
    auto word=[&]() -> std::optional<std::uint32_t> {
        unsigned char bytes[4];if (!file.read(reinterpret_cast<char*>(bytes),4)) return std::nullopt;
        return static_cast<std::uint32_t>(bytes[0])|(static_cast<std::uint32_t>(bytes[1])<<8)|
               (static_cast<std::uint32_t>(bytes[2])<<16)|(static_cast<std::uint32_t>(bytes[3])<<24);
    };
    const auto count=word();if (!count || *count<3 || *count>2048) return std::nullopt;
    std::vector<PreviewPixels> records;std::uint64_t total=0;
    for (std::uint32_t i=0;i<*count;++i) {
        const auto kind=word(),source=word(),palette=word(),width=word(),height=word(),size=word();
        if (!kind||!source||!palette||!width||!height||!size || *kind>3 || *palette>3 ||
            *width==0 || *height==0 || *width>320 || *height>224 ||
            static_cast<std::uint64_t>(*width)*(*height)*4!=*size) return std::nullopt;
        total+=*size;if (total>8*1024*1024) return std::nullopt;
        for (const auto& existing:records)
            if (existing.kind==*kind && existing.source==*source && existing.palette==*palette &&
                existing.width==*width && existing.height==*height) return std::nullopt;
        PreviewPixels record{*kind,*source,*palette,*width,*height,std::vector<std::uint8_t>(*size)};
        if (!file.read(reinterpret_cast<char*>(record.rgba.data()),static_cast<std::streamsize>(*size))) return std::nullopt;
        records.push_back(std::move(record));
    }
    if (file.peek()!=std::char_traits<char>::eof()) return std::nullopt;
    return records;
}
} // namespace rolo

