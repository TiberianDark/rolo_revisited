#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>

namespace rolo {
// Native semantic groups replace the original self-modifying list-append words.
// Group meanings beyond list selection remain to be established.
enum class ObjectGroup : std::uint8_t { One, Two, Three, Four, Five, Six };
using ObjectId = std::uint16_t;
struct ActiveObject { ObjectId id; ObjectGroup group; };
constexpr std::size_t max_active_objects = 48;

struct ObjectQueues {
    // Original layout: up to 48 entries followed by a zero sentinel per list.
    std::array<std::array<ObjectId, max_active_objects + 1>, 6> entries{};
    std::array<std::size_t, 6> sizes{};
};

[[nodiscard]] inline std::optional<ObjectQueues>
build_object_queues(std::span<const ActiveObject> active) {
    if (active.size() > max_active_objects) return std::nullopt;
    ObjectQueues result;
    for (const auto& object : active) {
        const auto group = static_cast<std::size_t>(object.group);
        if (group >= result.entries.size() || object.id == 0) return std::nullopt;
        result.entries[group][result.sizes[group]++] = object.id;
    }
    return result;
}

// $702C: wrap the original 16-bit arithmetic, then OR the text attributes.
[[nodiscard]] constexpr std::uint16_t font_tile_word(std::uint8_t character,
                                                     std::uint16_t attributes) {
    const auto tile = static_cast<std::uint16_t>(static_cast<unsigned>(character) + 0x7b4u - 0x20u);
    return static_cast<std::uint16_t>(tile | attributes);
}
} // namespace rolo
