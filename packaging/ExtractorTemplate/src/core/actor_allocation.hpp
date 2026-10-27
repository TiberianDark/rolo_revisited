#pragma once
#include "core/actor_initialization.hpp"
#include <array>
#include <span>
#include <stdexcept>

namespace rolo {
struct AllocationDiagnostics {
    virtual ~AllocationDiagnostics()=default;
    virtual void allocation_diagnostic(std::uint32_t palette_context)=0; // Native replacement for5998 remains a world service.
};
struct GraphicsSpan {std::uint32_t start{},remaining{};int next{-1};};
struct GraphicsAllocation {std::uint32_t start{};bool found{},negative{};};
// $34C2..$34F0: BMI tests wrapped subtraction's N flag, not signed BGE.
inline GraphicsAllocation allocate_graphics_span(std::span<GraphicsSpan> spans,int head,
        std::uint32_t request,AllocationDiagnostics& diagnostics) {
    for(auto index=head;index!=-1;) {
        if(index<0||static_cast<std::size_t>(index)>=spans.size())throw std::out_of_range("Native graphics-span link");
        auto& span=spans[index];const auto remaining=span.remaining-request;
        if(signed_long(remaining)<0){index=span.next;continue;}
        span.remaining=remaining;const auto start=span.start;span.start+=request;
        return {start,true,(request&0x8000u)!=0}; // TST.W request supplies returned N.
    }
    diagnostics.allocation_diagnostic(0); // D1=0 at the terminal null link.
    return {0xffffffffu,false,true};
}
struct ActorPool {
    static constexpr std::uint32_t first_key=0xffff998cu,stride=130;
    std::array<ActorState,48> actors{};
    std::array<std::uint32_t,49> free_keys{};
    std::size_t cursor{};
    static constexpr std::uint32_t key(std::size_t index) {return first_key+static_cast<std::uint32_t>(index)*stride;}
    ActorState& resolve(std::uint32_t identity) {
        const auto delta=identity-first_key;
        if(identity<first_key||delta%stride||delta/stride>=actors.size())throw std::out_of_range("Native actor identity");
        return actors[delta/stride];
    }
    // $27F0: reinitialize free keys; only byte0 of each record is written.
    void initialize_free_stack() {
        cursor=0;
        for(std::size_t i=0;i<actors.size();++i){actors[i].byte(0,255);free_keys[i]=key(i);}
        free_keys.back()=0;
    }
};
struct ActorChainDefinition {
    ActorInitialDefinition initial;
    std::uint32_t linked{};
    std::uint16_t resource_units{};
};
struct ActorAllocationServices:ActorInitializationServices,AllocationDiagnostics {
    virtual const ActorChainDefinition& allocation_definition(std::uint32_t)=0;
    virtual GraphicsAllocation allocation_graphics(std::uint16_t)=0;
};
struct ActorAllocationRequest {
    std::uint32_t definition{},x{},y{},marker{},resource_context{};
    std::uint8_t facing{};
};
struct ActorAllocationResult {
    std::uint32_t returned_key{},head{},tail{},resource_context{},marker_context{};
    bool success{};
};
// $28B0..$29EE. Identities retain the source record keys to preserve word74
// and head/previous/next relationships; they are native data handles, not CPU memory.
inline ActorAllocationResult allocate_actor_chain(ActorPool& pool,ActorAllocationRequest request,
        ActorAllocationServices& services) {
    auto cursor=pool.cursor;
    if(cursor>=pool.free_keys.size())throw std::out_of_range("Native actor free-stack cursor");
    const auto first=pool.free_keys[cursor];std::uint32_t head=0,previous=0;
    auto context=request.resource_context;
    auto failure=[&] {
        pool.cursor=cursor-1;services.allocation_diagnostic(context);
        return ActorAllocationResult{0,head,previous,context,request.marker,false};
    };
    for(std::size_t steps=0;steps<=pool.actors.size();++steps) {
        if(cursor>=pool.free_keys.size())throw std::out_of_range("Native actor free-stack end");
        const auto identity=pool.free_keys[cursor++];
        if(!identity)return failure();
        const auto& definition=services.allocation_definition(request.definition);
        if(definition.initial.key!=request.definition)throw std::logic_error("Native definition identity mismatch");
        if(definition.resource_units) {
            const auto allocation=services.allocation_graphics(definition.resource_units);
            context=allocation.start;
            if(allocation.negative)return failure();
            if(!allocation.found)throw std::logic_error("Resource failure omitted native negative flag");
        }
        auto& actor=pool.resolve(identity);
        initialize_actor(actor,definition.initial,request.x,request.y,request.facing,
            static_cast<std::uint16_t>(context),request.marker,head,previous,services);
        request.marker=0; // Only the first member consumes the source marker.
        const auto type=definition.initial.type;
        const auto shifted=static_cast<std::uint16_t>((type>>2)|((type&0x8000)?0xc000:0));
        context=(context&0xffff0000u)|shifted; // MOVE.W/ASR.W retains upper D1.
        if(previous)pool.resolve(previous).longword(84,identity);
        head=first;previous=identity;
        request.definition=definition.linked;
        if(!request.definition){pool.cursor=cursor;return {head,head,previous,context,request.marker,true};}
    }
    throw std::logic_error("Native definition chain escaped pool capacity");
}
}
