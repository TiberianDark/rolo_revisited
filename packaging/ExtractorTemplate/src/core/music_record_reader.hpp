#pragma once
#include <cstddef>
#include <cstdint>
#include <span>
#include <stdexcept>

namespace rolo {
// Data-format translation of driver 0835, 087D, 0914 and 095C-097A.
// Channel allocation, envelopes, synthesis and tick scheduling are separate.
struct MusicRecord {
    std::size_t offset{};
    std::uint8_t command{}, channel{}, value{}, delay{};
    bool end{}, stop{};
};
class MusicRecordReader {
    std::span<const std::uint8_t> bytes_;
    std::size_t cursor_{};
    std::uint8_t running_{};
    bool ended_{};
public:
    explicit MusicRecordReader(std::span<const std::uint8_t> bytes):bytes_(bytes) {
        if(bytes.empty()) throw std::invalid_argument("Empty music stream");
        if(bytes[0]<128) cursor_=1; // 0866: skip optional initial positive byte.
    }
    MusicRecord next() {
        if(ended_) throw std::logic_error("Music stream already ended");
        if(cursor_>=bytes_.size()) throw std::out_of_range("Music stream missing end");
        MusicRecord result; result.offset=cursor_;
        if(bytes_[cursor_]&128) running_=bytes_[cursor_++];
        result.command=running_; result.channel=running_&15;
        if(running_==0xfc) {
            ended_=result.end=true;
            result.stop=cursor_<bytes_.size() && bytes_[cursor_]==0x80;
            return result;
        }
        const auto kind=running_&0xf0;
        if(kind!=0x80 && kind!=0x90 && kind!=0xc0)
            throw std::invalid_argument("Unreviewed music record command");
        if(bytes_.size()-cursor_<2) throw std::out_of_range("Truncated music record");
        result.value=bytes_[cursor_++]; result.delay=bytes_[cursor_++];
        return result;
    }
};
}
