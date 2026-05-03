#!/usr/bin/env swift
//
// export_sf_symbols.swift — Export SF Symbols for graph_editor (@1x + @2x)
//
// Usage:  swift export_sf_symbols.swift
//

import AppKit

struct IconSpec {
    let sfName: String
    let baseName: String
    let logicalSize: Int
    let weight: NSFont.Weight
}

let icons: [IconSpec] = [
    IconSpec(sfName: "number.circle",                            baseName: "number.circle",                            logicalSize: 22, weight: .regular),
    IconSpec(sfName: "line.diagonal",                            baseName: "line.diagonal",                            logicalSize: 22, weight: .regular),
    IconSpec(sfName: "point.3.connected.trianglepath.dotted",    baseName: "point.3.connected.trianglepath.dotted",    logicalSize: 22, weight: .regular),
    IconSpec(sfName: "tag",                                      baseName: "tag",                                      logicalSize: 22, weight: .regular),
    IconSpec(sfName: "message",                                  baseName: "message",                                  logicalSize: 22, weight: .regular),
]

struct ThemeVariant {
    let suffix: String
    let tint: NSColor
}

let themes: [ThemeVariant] = [
    ThemeVariant(suffix: "-dark", tint: .white),
    ThemeVariant(suffix: "",      tint: .black),
]

func renderIcon(_ sfImage: NSImage, pixelSize: Int, tint: NSColor, weight: NSFont.Weight) -> Data? {
    let targetPx = CGFloat(pixelSize)
    let probeConfig = NSImage.SymbolConfiguration(pointSize: targetPx, weight: weight)
    let probeImage = sfImage.withSymbolConfiguration(probeConfig) ?? sfImage
    let probeMax = max(probeImage.size.width, probeImage.size.height)
    let exactPointSize = targetPx * (targetPx / probeMax)

    let config = NSImage.SymbolConfiguration(pointSize: exactPointSize, weight: weight)
    let configured = sfImage.withSymbolConfiguration(config) ?? sfImage

    let bitmapRep = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: pixelSize, pixelsHigh: pixelSize,
        bitsPerSample: 8, samplesPerPixel: 4,
        hasAlpha: true, isPlanar: false,
        colorSpaceName: .deviceRGB,
        bytesPerRow: 0, bitsPerPixel: 0
    )!
    bitmapRep.size = NSSize(width: pixelSize, height: pixelSize)

    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: bitmapRep)

    let symbolSize = configured.size
    let x = (targetPx - symbolSize.width) / 2
    let y = (targetPx - symbolSize.height) / 2
    configured.draw(
        in: NSRect(x: x, y: y, width: symbolSize.width, height: symbolSize.height),
        from: .zero, operation: .sourceOver, fraction: 1.0)

    tint.set()
    NSRect(origin: .zero, size: NSSize(width: pixelSize, height: pixelSize)).fill(using: .sourceIn)

    NSGraphicsContext.restoreGraphicsState()

    return bitmapRep.representation(using: .png, properties: [:])
}

let scriptURL = URL(fileURLWithPath: CommandLine.arguments[0])
let outputDir = scriptURL.deletingLastPathComponent()
var exported = 0
var failed = 0

for theme in themes {
    let label = theme.suffix == "-dark" ? "Dark" : "Light"
    print("\n── \(label) ──")
    for icon in icons {
        guard let sfImage = NSImage(systemSymbolName: icon.sfName, accessibilityDescription: nil) else {
            print("  ✗ SF Symbol not found: \(icon.sfName)")
            failed += 2; continue
        }
        for (suffix, scale) in [("", 1), ("@2x", 2)] {
            let px = icon.logicalSize * scale
            if let data = renderIcon(sfImage, pixelSize: px, tint: theme.tint, weight: icon.weight) {
                let name = "\(icon.baseName)\(theme.suffix)\(suffix).png"
                try! data.write(to: outputDir.appendingPathComponent(name))
                print("  ✓ \(name) (\(px)×\(px) @\(scale)x)")
                exported += 1
            } else { failed += 1 }
        }
    }
}

print("\nDone: \(exported) exported, \(failed) failed")
