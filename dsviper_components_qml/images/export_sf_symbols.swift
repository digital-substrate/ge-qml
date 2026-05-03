#!/usr/bin/env swift
//
// export_sf_symbols.swift — Export SF Symbols as @1x + @2x PNGs
//
// Usage:  swift export_sf_symbols.swift
//
// Generates for each icon:
//   {name}-dark.png      — @1x dark (22×22 or 16×16)
//   {name}-dark@2x.png   — @2x dark (44×44 or 32×32) — used on Retina
//   {name}.png           — @1x light
//   {name}@2x.png        — @2x light
//
// QML references "{name}-dark.png" — Qt auto-selects @2x on Retina.
//

import AppKit

struct IconSpec {
    let sfName: String
    let baseName: String
    let logicalSize: Int  // @1x size (22 or 16)
    let weight: NSFont.Weight
}

let toolbarIcons: [IconSpec] = [
    IconSpec(sfName: "arrow.up.circle",                          baseName: "arrow.up.circle",                          logicalSize: 22, weight: .regular),
    IconSpec(sfName: "arrow.triangle.merge",                     baseName: "arrow.triangle.merge",                     logicalSize: 22, weight: .regular),
    IconSpec(sfName: "icloud.and.arrow.down",                    baseName: "icloud.and.arrow.down",                    logicalSize: 22, weight: .regular),
    IconSpec(sfName: "icloud.and.arrow.up",                      baseName: "icloud.and.arrow.up",                      logicalSize: 22, weight: .regular),
    IconSpec(sfName: "link.icloud",                              baseName: "link.icloud",                              logicalSize: 22, weight: .regular),
    IconSpec(sfName: "person.icloud",                            baseName: "person.icloud",                            logicalSize: 22, weight: .regular),
    IconSpec(sfName: "person.icloud.fill",                       baseName: "person.icloud.fill",                       logicalSize: 22, weight: .regular),
    IconSpec(sfName: "arrow.triangle.2.circlepath.icloud",       baseName: "arrow.triangle.2.circlepath.icloud",       logicalSize: 22, weight: .regular),
    IconSpec(sfName: "arrow.triangle.2.circlepath.icloud.fill",  baseName: "arrow.triangle.2.circlepath.icloud.fill",  logicalSize: 22, weight: .regular),
    IconSpec(sfName: "arrowshape.right.circle",                  baseName: "arrowshape.right.circle",                  logicalSize: 22, weight: .regular),
    IconSpec(sfName: "dice",                                     baseName: "dice",                                     logicalSize: 22, weight: .regular),
    IconSpec(sfName: "creditcard.and.123",                       baseName: "creditcard.and.123",                       logicalSize: 22, weight: .regular),
]

let smallIcons: [IconSpec] = [
    IconSpec(sfName: "eye",                                      baseName: "eye",                                      logicalSize: 16, weight: .regular),
    IconSpec(sfName: "eye.slash",                                baseName: "eye.slash",                                logicalSize: 16, weight: .regular),
    IconSpec(sfName: "doc.on.doc",                               baseName: "doc.on.doc",                               logicalSize: 22, weight: .regular),
    IconSpec(sfName: "plus.circle",                              baseName: "plus.circle",                              logicalSize: 22, weight: .regular),
    IconSpec(sfName: "plus.circle.dashed",                       baseName: "plus.circle.dashed",                       logicalSize: 22, weight: .regular),
    IconSpec(sfName: "key.viewfinder",                           baseName: "key.viewfinder",                           logicalSize: 22, weight: .regular),
    IconSpec(sfName: "arrow.right.circle.fill",                  baseName: "arrow.right.circle.fill",                  logicalSize: 22, weight: .regular),
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
    // Find exact pointSize so symbol fits in pixelSize without scaling
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
let allIcons = toolbarIcons + smallIcons
var exported = 0
var failed = 0

for theme in themes {
    let label = theme.suffix == "-dark" ? "Dark" : "Light"
    print("\n── \(label) ──")

    for icon in allIcons {
        guard let sfImage = NSImage(systemSymbolName: icon.sfName, accessibilityDescription: nil) else {
            print("  ✗ SF Symbol not found: \(icon.sfName)")
            failed += 2
            continue
        }

        // @1x — logical size
        let px1x = icon.logicalSize
        if let data = renderIcon(sfImage, pixelSize: px1x, tint: theme.tint, weight: icon.weight) {
            let name = "\(icon.baseName)\(theme.suffix).png"
            try! data.write(to: outputDir.appendingPathComponent(name))
            print("  ✓ \(name) (\(px1x)×\(px1x) @1x)")
            exported += 1
        } else { failed += 1 }

        // @2x — double pixel size
        let px2x = icon.logicalSize * 2
        if let data = renderIcon(sfImage, pixelSize: px2x, tint: theme.tint, weight: icon.weight) {
            let name = "\(icon.baseName)\(theme.suffix)@2x.png"
            try! data.write(to: outputDir.appendingPathComponent(name))
            print("  ✓ \(name) (\(px2x)×\(px2x) @2x)")
            exported += 1
        } else { failed += 1 }
    }
}

print("\nDone: \(exported) exported, \(failed) failed")
