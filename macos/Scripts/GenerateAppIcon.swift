#!/usr/bin/env swift
import AppKit

func pngData(size: Int) -> Data {
    let s = NSSize(width: size, height: size)
    let image = NSImage(size: s, flipped: false) { rect in
        NSColor(calibratedRed: 0.22, green: 0.48, blue: 0.96, alpha: 1).setFill()
        rect.fill()
        let m = CGFloat(size) * 0.2
        NSColor.white.withAlphaComponent(0.92).setFill()
        NSBezierPath(roundedRect: NSInsetRect(rect, m, m * 1.12), xRadius: m * 0.35, yRadius: m * 0.35).fill()
        return true
    }
    guard let tiff = image.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff),
          let png = rep.representation(using: .png, properties: [:])
    else {
        fatalError("Could not build PNG")
    }
    return png
}

let repoRoot = URL(fileURLWithPath: CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : FileManager.default.currentDirectoryPath, isDirectory: true)
let dir = repoRoot.appendingPathComponent("SmartPaste/Assets.xcassets/AppIcon.appiconset", isDirectory: true)
try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
try pngData(size: 512).write(to: dir.appendingPathComponent("AppIcon-512.png"))
try pngData(size: 1024).write(to: dir.appendingPathComponent("AppIcon-512@2x.png"))
print("OK:", dir.path)
