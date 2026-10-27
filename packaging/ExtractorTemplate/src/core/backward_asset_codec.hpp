#pragma once
#include <array>
#include <cstdint>
#include <span>
#include <vector>
#include <stdexcept>
namespace rolo {
struct AssetDecodeError:std::runtime_error{using std::runtime_error::runtime_error;};
class BackwardAssetBits {
 std::span<const std::uint8_t> data;std::size_t lower_,pointer_;std::uint32_t state_=1;std::uint64_t consumed_=0;
public:
 BackwardAssetBits(std::span<const std::uint8_t> bytes,std::size_t lower,std::size_t end):data(bytes),lower_(lower),pointer_(end){if(lower>end||end>bytes.size())throw AssetDecodeError("Bitstream extent");}
 bool bit(){bool carry=state_&1;state_>>=1;if(!state_){if(pointer_-lower_<4)throw AssetDecodeError("Bitstream exhausted");pointer_-=4;std::uint32_t word=0;for(unsigned i=0;i<4;++i)word=(word<<8)|data[pointer_+i];state_=(word>>1)|(std::uint32_t(carry)<<31);carry=word&1;}++consumed_;return carry;}
 std::uint32_t value(std::uint32_t count){if(count>65536)throw AssetDecodeError("Bit width extent");std::uint32_t result=0;for(std::uint32_t i=0;i<count;++i)result=(result<<1)|std::uint32_t(bit());return result;}
 std::uint32_t dbf_value(std::uint16_t counter){return value(std::uint32_t(counter)+1);}
 std::uint32_t width_value(std::uint16_t width){return value(width?width:65536);}
 std::size_t pointer()const{return pointer_;}std::uint64_t consumed()const{return consumed_;}
};
struct BackwardAssetResult {std::vector<std::uint8_t> bytes;std::size_t encoded_size{},lowest_read{};std::uint64_t bits_read{};std::uint32_t literal_runs{},match_runs{};};
// $A75A/$A768: typed data decompressor, never a CPU instruction interpreter.
inline BackwardAssetResult decode_backward_asset(std::span<const std::uint8_t> data,std::size_t source,std::size_t max_output=65536){
 auto word=[&](std::size_t at){if(at>data.size()||data.size()-at<4)throw AssetDecodeError("Truncated asset header");std::uint32_t result=0;for(unsigned i=0;i<4;++i)result=(result<<8)|data[at+i];return result;};
 if(source>data.size()||data.size()-source<12)throw AssetDecodeError("Truncated asset header");const auto size=word(source);
 if(size<16||size%4||size>data.size()-source)throw AssetDecodeError("Invalid encoded asset size");const auto end=source+size;const auto trailer=word(end-4);const auto output_size=trailer>>8,skip=trailer&255;
 if(!output_size||output_size>max_output||output_size>65536||skip>32)throw AssetDecodeError("Invalid asset output extent");
 std::array<std::uint8_t,4> widths;for(unsigned i=0;i<4;++i){widths[i]=data[source+4+i];if(!widths[i]||widths[i]>15)throw AssetDecodeError("Invalid distance width");}
 BackwardAssetBits bits(data,source+8,end-4);for(unsigned i=0;i<skip;++i)bits.bit();BackwardAssetResult result;result.bytes.resize(output_size);result.encoded_size=size;std::size_t cursor=output_size;
 while(cursor){
  if(!bits.bit()){
   std::size_t count=0;for(;;){const auto part=bits.value(2);count+=part;if(count>=output_size)throw AssetDecodeError("Literal run exceeds output");if(part!=3)break;}++count;if(count>cursor)throw AssetDecodeError("Literal run crosses output start");
   for(std::size_t i=0;i<count;++i){auto value=bits.value(8);result.bytes[--cursor]=static_cast<std::uint8_t>(value);}++result.literal_runs;if(!cursor)break;
  }
  const auto selector=bits.value(2);std::size_t count=selector;std::uint32_t distance;
  if(selector==3){const auto width=bits.bit()?widths[3]:7;distance=bits.width_value(width);for(;;){const auto part=bits.value(3);count+=part;if(count>=output_size)throw AssetDecodeError("Match run exceeds output");if(part!=7)break;}}
  else distance=bits.width_value(widths[selector]);
  count+=2;if(count>cursor)throw AssetDecodeError("Match run crosses output start");
  for(std::size_t i=0;i<count;++i){const auto from=cursor+distance;if(from>=output_size)throw AssetDecodeError("Backreference outside decoded suffix");const auto value=result.bytes[from];result.bytes[--cursor]=value;}++result.match_runs;
 }
 result.lowest_read=bits.pointer();result.bits_read=bits.consumed();return result;
}
}
