#pragma once
#include "core/palette_entry_contracts.hpp"
#include <cstdint>
#include <limits>
namespace rolo {
// Host callback ownership, not a CPU register file or instruction interpreter.
enum class NativeEventKind:std::uint8_t{foreground,frame,trap_return};
struct NativeEventContext{const void*owner{};std::uint32_t depth{};NativeEventKind kind=NativeEventKind::foreground;};
// A structured native scope supplies the restore-and-return role of $1074 RTE.
// It restores host ownership on normal return and C++ unwinding; payload state is separate.
class NativeEventScope {
 NativeEventContext&live;const NativeEventContext saved;
public:
 NativeEventScope(NativeEventContext&context,NativeEventKind kind):live(context),saved(context){if(context.depth==std::numeric_limits<std::uint32_t>::max())throw std::out_of_range("Native event nesting extent");live.kind=kind;++live.depth;}
 NativeEventScope(const NativeEventScope&)=delete;NativeEventScope&operator=(const NativeEventScope&)=delete;
 ~NativeEventScope()noexcept{live=saved;}
};
// $149E saves caller state, TRAP0 returns through1074, then falls through14A4.
// Windows uses a synchronous C++ callback and its ABI instead of a CPU exception stack.
inline void run_native_palette_event(NativeEventContext&context,PaletteInterruptState&s,NativePaletteEffects&p,PaletteInterruptServices&v){
 NativeEventScope frame(context,NativeEventKind::frame);
 {NativeEventScope trap(context,NativeEventKind::trap_return);}
 update_palette_interrupt_tail(s,p,v);
}
}
