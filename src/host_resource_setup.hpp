#pragma once
#include "host_rom.hpp"
#undef near
#undef far
#include <array>
#include <filesystem>
#include <fstream>
#include <optional>
#include <stdexcept>
#include <string>

namespace rolo {
inline std::filesystem::path saved_resource_root(const std::filesystem::path& app_root) {
    // Keep each portable installation self-contained, including first-run extraction.
    return app_root / "resources-v1";
}

inline void check_external_asset_files(const std::filesystem::path& root) {
    for (const auto* name : {"entrance-assets.rla", "player-assets.rla", "level1-player-assets.rla",
            "first-enemy-assets.rla", "level1-object-assets.rla", "world-cursor-assets.rla", "world-bunny-assets.rla", "forest-log-assets.rla"}) {
        std::error_code error;
        const auto size = std::filesystem::file_size(root / name, error);
        if (error || size <= 12) throw std::runtime_error(std::string("Missing or incomplete game resource: ") + name);
    }
}

inline std::wstring resource_setup_argument(const std::wstring& value) {
    std::wstring result = L"\"";
    unsigned slashes = 0;
    for (const auto character : value) {
        if (character == L'\\') { ++slashes; continue; }
        result.append(character == L'\"' ? slashes * 2 + 1 : slashes, L'\\');
        slashes = 0;
        result += character;
    }
    result.append(slashes * 2, L'\\');
    return result + L'\"';
}

inline bool prepare_external_resources(const std::filesystem::path& app_root, const std::filesystem::path& root) {
    const auto script = app_root / "prepare_resources.py";
    const auto python = app_root / "runtime/python/python.exe";
    if (!std::filesystem::is_regular_file(script) || !std::filesystem::is_regular_file(python))
        throw std::runtime_error("Game setup files are missing. Extract the complete Rolo download into one folder and run RoloGame.exe again.");
    std::array<wchar_t,32768> rom{};
    for (;;) {
        OPENFILENAMEW dialog{};
        dialog.lStructSize = sizeof(dialog);
        dialog.lpstrFile = rom.data();
        dialog.nMaxFile = static_cast<DWORD>(rom.size());
        dialog.lpstrTitle = L"Choose your Rolo to the Rescue ROM";
        dialog.lpstrFilter = L"Mega Drive ROM (*.bin;*.md;*.gen)\0*.bin;*.md;*.gen\0All files\0*.*\0";
        dialog.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST | OFN_NOCHANGEDIR | OFN_EXPLORER;
        if (!GetOpenFileNameW(&dialog)) {
            const auto error = CommDlgExtendedError();
            if (error) throw std::runtime_error("Windows could not open the ROM picker (error " + std::to_string(error) + ").");
            return false;
        }
        if (verified_rom(rom.data())) break;
        if (MessageBoxW(nullptr, L"That file is not the supported 512 KiB Rolo ROM revision. No resources were extracted.",
                L"Rolo ROM check", MB_RETRYCANCEL | MB_ICONWARNING) != IDRETRY) return false;
    }
    std::filesystem::create_directories(root.parent_path());
    SECURITY_ATTRIBUTES security{sizeof(SECURITY_ATTRIBUTES), nullptr, TRUE};
    const auto log = CreateFileW((root.parent_path() / "setup.log").c_str(), GENERIC_WRITE, FILE_SHARE_READ,
        &security, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (log == INVALID_HANDLE_VALUE) throw std::runtime_error("Rolo could not create its setup log.");
    const auto input = CreateFileW(L"NUL", GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE,
        &security, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (input == INVALID_HANDLE_VALUE) { CloseHandle(log); throw std::runtime_error("Rolo could not start setup input."); }
    auto command = resource_setup_argument(python.native()) + L" " + resource_setup_argument(script.native()) +
        L" --resource-root " + resource_setup_argument(root.native()) + L" --rom " + resource_setup_argument(rom.data());
    STARTUPINFOW startup{};
    startup.cb = sizeof(startup);
    startup.dwFlags = STARTF_USESTDHANDLES;
    startup.hStdInput = input;
    startup.hStdOutput = startup.hStdError = log;
    PROCESS_INFORMATION process{};
    const bool started = CreateProcessW(python.c_str(), command.data(), nullptr, nullptr, TRUE, CREATE_NO_WINDOW,
        nullptr, app_root.c_str(), &startup, &process) != FALSE;
    const auto start_error = GetLastError();
    CloseHandle(input);
    CloseHandle(log);
    if (!started) throw std::runtime_error("Windows could not start Rolo setup (error " + std::to_string(start_error) + ").");
    CloseHandle(process.hThread);
    const auto status = CreateWindowExW(WS_EX_TOPMOST, L"STATIC", L"Preparing Rolo resources",
        WS_OVERLAPPED | WS_CAPTION | WS_VISIBLE, CW_USEDEFAULT, CW_USEDEFAULT, 470, 125,
        nullptr, nullptr, GetModuleHandleW(nullptr), nullptr);
    if (status) CreateWindowW(L"STATIC", L"Extracting game data from your ROM.\nThis may take a few minutes. The game will open when ready.",
        WS_CHILD | WS_VISIBLE, 15, 15, 430, 60, status, nullptr, GetModuleHandleW(nullptr), nullptr);
    DWORD waited;
    while ((waited = WaitForSingleObject(process.hProcess, 50)) == WAIT_TIMEOUT) {
        MSG message{};
        while (PeekMessageW(&message, nullptr, 0, 0, PM_REMOVE)) { TranslateMessage(&message); DispatchMessageW(&message); }
    }
    if (status) DestroyWindow(status);
    DWORD exit_code = 1;
    const bool got_exit = GetExitCodeProcess(process.hProcess, &exit_code) != FALSE;
    CloseHandle(process.hProcess);
    if (waited != WAIT_OBJECT_0 || !got_exit) throw std::runtime_error("Rolo setup did not finish correctly.");
    if (exit_code != 0) throw std::runtime_error("Rolo could not prepare its resources. See setup.log beside the saved resource folder for details.");
    return true;
}
}