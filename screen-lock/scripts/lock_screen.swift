import Darwin

guard CommandLine.arguments.count == 1 ||
      (CommandLine.arguments.count == 2 && CommandLine.arguments[1] == "--check") else {
    fputs("Usage: lock_screen.swift [--check]\n", stderr)
    exit(2)
}

guard let library = dlopen("/System/Library/PrivateFrameworks/login.framework/login", RTLD_NOW),
      let symbol = dlsym(library, "SACLockScreenImmediate") else {
    fputs("Native session-lock API unavailable\n", stderr)
    exit(2)
}

if CommandLine.arguments.count == 2 {
    print("Native session-lock symbol available; no lock requested")
    exit(0)
}

let lock = unsafeBitCast(symbol, to: (@convention(c) () -> Void).self)
lock()
print("Native session-lock request sent; verification required")
