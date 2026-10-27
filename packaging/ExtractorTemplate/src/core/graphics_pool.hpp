#pragma once
#include "core/actor_allocation.hpp"
namespace rolo {
struct GraphicsPool {
    // $3478:25 twelve-byte nodes plus a sentinel; original free-stack order.
    std::array<GraphicsSpan,26> nodes{};
    std::array<int,25> free_nodes{};
    std::size_t cursor{};
    GraphicsSpan& node(int index) {
        if(index<0||static_cast<std::size_t>(index)>=nodes.size())throw std::out_of_range("Native graphics-pool node");
        return nodes[index];
    }
    void release(std::uint32_t start,std::uint32_t size) {
        int previous=0,next=node(0).next;
        while(next!=-1&&signed_long(start)>=signed_long(node(next).start)) {
            previous=next;next=node(next).next;
        }
        auto free_cursor=cursor;
        int resident=previous;
        if(start==node(previous).start+node(previous).remaining)node(previous).remaining+=size;
        else {
            if(free_cursor>=free_nodes.size())throw std::out_of_range("Native graphics free-node exhaustion; source-domain audit pending");
            resident=free_nodes.at(free_cursor++);
            node(previous).next=resident;
            node(resident)={start,size,next};
        }
        // $3536 uses the released span's start+size, including wrapped addition.
        if(next!=-1&&start+size==node(next).start) {
            node(resident).remaining+=node(next).remaining;
            node(resident).next=node(next).next;
            if(!free_cursor)throw std::out_of_range("Native graphics free-node underflow");
            free_nodes.at(--free_cursor)=next;
        }
        cursor=free_cursor;
    }
    void initialize(std::uint16_t reserved_patterns) {
        nodes[0]={0xffffffffu,0,-1};cursor=0;
        for(std::size_t i=0;i<free_nodes.size();++i)free_nodes[i]=static_cast<int>(i+1);
        const auto reserved=static_cast<std::uint16_t>(reserved_patterns<<5);
        release(reserved,0xa800u-reserved);
    }
    GraphicsAllocation allocate(std::uint32_t size,AllocationDiagnostics& diagnostics) {
        return allocate_graphics_span(nodes,nodes[0].next,size,diagnostics);
    }
};
}
