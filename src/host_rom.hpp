#pragma once
#define NOMINMAX
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <commdlg.h>
#include <bcrypt.h>
#undef near
#undef far
#include <SDL3/SDL.h>
#include <filesystem>
#include <fstream>
#include <vector>
#include <array>
namespace rolo {
inline constexpr char pinned_rom_sha256[]="9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9";
inline bool verified_rom(const std::filesystem::path&path){
 std::error_code error;if(std::filesystem::file_size(path,error)!=524288||error)return false;
 std::ifstream in(path,std::ios::binary);std::vector<unsigned char>data(524288);if(!in.read(reinterpret_cast<char*>(data.data()),data.size()))return false;
 BCRYPT_ALG_HANDLE algorithm{};if(BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,nullptr,0)<0)return false;
 std::array<unsigned char,32> digest{};const auto status=BCryptHash(algorithm,nullptr,0,data.data(),ULONG(data.size()),digest.data(),ULONG(digest.size()));BCryptCloseAlgorithmProvider(algorithm,0);
 if(status<0)return false;std::string hash;constexpr char digits[]="0123456789abcdef";for(auto b:digest){hash+=digits[b>>4];hash+=digits[b&15];}
 return hash==pinned_rom_sha256;
}
inline bool ensure_verified_rom(){
 char* pref=SDL_GetPrefPath("NativeRolo","RoloToTheRescue");if(!pref)return false;
 const std::filesystem::path directory=std::filesystem::u8path(pref);SDL_free(pref);
 const auto cached=directory/"verified-rom.bin";if(verified_rom(cached))return true;
 for(;;){
  std::array<wchar_t,32768> path{};OPENFILENAMEW dialog{};dialog.lStructSize=sizeof(dialog);dialog.lpstrFile=path.data();dialog.nMaxFile=DWORD(path.size());
  dialog.lpstrTitle=L"Rolo to the Rescue - select your original ROM";
  dialog.lpstrFilter=L"Mega Drive ROM (*.bin;*.md;*.gen)\0*.bin;*.md;*.gen\0All files\0*.*\0";
  dialog.Flags=OFN_FILEMUSTEXIST|OFN_PATHMUSTEXIST|OFN_NOCHANGEDIR|OFN_EXPLORER;
  if(!GetOpenFileNameW(&dialog))return false;
  if(!verified_rom(path.data())){
   if(MessageBoxW(nullptr,L"This ROM does not match the supported Rolo revision. Please select the same original 512 KB ROM used for this port.\n\nNo ROM has been imported.",L"ROM revision does not match",MB_RETRYCANCEL|MB_ICONWARNING)!=IDRETRY)return false;
   continue;
  }
  std::filesystem::create_directories(directory);
  const auto temporary=directory/"verified-rom.tmp";std::filesystem::copy_file(path.data(),temporary,std::filesystem::copy_options::overwrite_existing);
  if(!verified_rom(temporary)){std::filesystem::remove(temporary);return false;}
  if(!MoveFileExW(temporary.c_str(),cached.c_str(),MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH))return false;
  return true;
 }
}
}
