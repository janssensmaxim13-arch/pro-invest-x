# ProInvestiX Enterprise Desktop

Cross-platform desktop applicatie gebouwd met Tauri + Next.js.

## Vereisten

- Node.js 18+
- Rust 1.70+
- Platform-specifieke dependencies (zie Tauri docs)

## Development

```bash
# Install dependencies
npm install

# Run in development mode
npm run tauri:dev
```

## Building

```bash
# Build voor huidig platform
npm run tauri:build

# Build voor specifiek platform
npm run tauri:build:windows
npm run tauri:build:mac
npm run tauri:build:linux
```

## Features

- 🖥️ Native desktop experience
- 🔔 System tray met quick actions
- 📢 Native notifications
- 🔄 Auto-updates
- 💾 Offline support
- ⌨️ Keyboard shortcuts

## Platform Support

| Platform | Status |
|----------|--------|
| Windows 10/11 | ✅ |
| macOS 10.15+ | ✅ |
| Linux (Ubuntu 20.04+) | ✅ |
