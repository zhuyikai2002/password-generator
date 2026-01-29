#!/usr/bin/env python3
"""使用 AppKit 创建应用图标"""

import subprocess
import os

# 使用 Swift 脚本创建图标（更可靠）
swift_code = '''
import AppKit
import Foundation

let sizes: [(Int, String)] = [
    (16, "icon_16x16.png"),
    (32, "icon_16x16@2x.png"),
    (32, "icon_32x32.png"),
    (64, "icon_32x32@2x.png"),
    (128, "icon_128x128.png"),
    (256, "icon_128x128@2x.png"),
    (256, "icon_256x256.png"),
    (512, "icon_256x256@2x.png"),
    (512, "icon_512x512.png"),
    (1024, "icon_512x512@2x.png")
]

func createIcon(size: Int, filename: String) {
    let image = NSImage(size: NSSize(width: size, height: size))
    
    image.lockFocus()
    
    // 背景渐变
    let gradient = NSGradient(colors: [
        NSColor(red: 0.4, green: 0.5, blue: 0.92, alpha: 1.0),
        NSColor(red: 0.46, green: 0.29, blue: 0.64, alpha: 1.0)
    ])!
    
    let margin = CGFloat(size) * 0.06
    let radius = CGFloat(size) * 0.18
    let rect = NSRect(x: margin, y: margin, width: CGFloat(size) - 2*margin, height: CGFloat(size) - 2*margin)
    let path = NSBezierPath(roundedRect: rect, xRadius: radius, yRadius: radius)
    
    gradient.draw(in: path, angle: -90)
    
    // 绘制文字
    let text = "Aa1."
    let fontSize = CGFloat(size) * 0.32
    let font = NSFont.systemFont(ofSize: fontSize, weight: .bold)
    
    let attributes: [NSAttributedString.Key: Any] = [
        .font: font,
        .foregroundColor: NSColor.white
    ]
    
    let textSize = text.size(withAttributes: attributes)
    let textX = (CGFloat(size) - textSize.width) / 2
    let textY = (CGFloat(size) - textSize.height) / 2
    
    text.draw(at: NSPoint(x: textX, y: textY), withAttributes: attributes)
    
    image.unlockFocus()
    
    // 保存
    if let tiffData = image.tiffRepresentation,
       let bitmapImage = NSBitmapImageRep(data: tiffData),
       let pngData = bitmapImage.representation(using: .png, properties: [:]) {
        try? pngData.write(to: URL(fileURLWithPath: filename))
        print("Created: \\(filename)")
    }
}

// 创建 iconset 目录
try? FileManager.default.createDirectory(atPath: "AppIcon.iconset", withIntermediateDirectories: true)

for (size, filename) in sizes {
    createIcon(size: size, filename: "AppIcon.iconset/\\(filename)")
}

print("Icons created successfully!")
'''

# 写入 Swift 脚本
with open('create_icons.swift', 'w') as f:
    f.write(swift_code)

# 运行 Swift 脚本
print("Creating icons with Swift...")
result = subprocess.run(['swift', 'create_icons.swift'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr)

# 创建 icns
print("Creating icns...")
subprocess.run(['iconutil', '-c', 'icns', 'AppIcon.iconset', '-o', 'AppIcon.icns'])
print("Done! Created AppIcon.icns")
