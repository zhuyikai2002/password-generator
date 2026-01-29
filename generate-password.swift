#!/usr/bin/env swift
//
// 强密码生成器 - Swift 版本
// 编译: swiftc -O -o pwgen generate-password.swift
//

import Foundation

// MARK: - 配置

let VERSION = "2.0"
let DEFAULT_LENGTH = 12
let DEFAULT_COUNT = 3
let MIN_LENGTH = 8
let MAX_LENGTH = 128

let UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
let LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
let DIGITS = "0123456789"
let SPECIAL = "!@#$%^&*_+-=[]{}|;:,.<>?"
let CONFUSING = "0O1lI|"

// MARK: - 颜色输出

struct Color {
    static let reset = "\u{001B}[0m"
    static let red = "\u{001B}[31m"
    static let green = "\u{001B}[32m"
    static let yellow = "\u{001B}[33m"
    static let blue = "\u{001B}[34m"
    static let magenta = "\u{001B}[35m"
    static let cyan = "\u{001B}[36m"
    static let bold = "\u{001B}[1m"
}

// MARK: - 密码生成

func generatePassword(
    length: Int,
    excludeConfusing: Bool = false,
    includeUppercase: Bool = true,
    includeLowercase: Bool = true,
    includeDigits: Bool = true,
    includeSpecial: Bool = true
) -> String {
    var upper = includeUppercase ? UPPERCASE : ""
    var lower = includeLowercase ? LOWERCASE : ""
    var digits = includeDigits ? DIGITS : ""
    var special = includeSpecial ? SPECIAL : ""
    
    if excludeConfusing {
        upper = upper.filter { !CONFUSING.contains($0) }
        lower = lower.filter { !CONFUSING.contains($0) }
        digits = digits.filter { !CONFUSING.contains($0) }
        special = special.filter { !CONFUSING.contains($0) }
    }
    
    let allChars = upper + lower + digits + special
    guard !allChars.isEmpty else {
        return "错误: 至少需要选择一种字符类型"
    }
    
    var required: [Character] = []
    if !upper.isEmpty { required.append(upper.randomElement()!) }
    if !lower.isEmpty { required.append(lower.randomElement()!) }
    if !digits.isEmpty { required.append(digits.randomElement()!) }
    if !special.isEmpty { required.append(special.randomElement()!) }
    
    var password = required
    let remaining = length - password.count
    if remaining > 0 {
        for _ in 0..<remaining {
            password.append(allChars.randomElement()!)
        }
    }
    
    password.shuffle()
    return String(password)
}

// MARK: - 密码强度评估

func calculateEntropy(_ password: String) -> Double {
    var charsetSize = 0
    
    let hasUpper = password.contains { UPPERCASE.contains($0) }
    let hasLower = password.contains { LOWERCASE.contains($0) }
    let hasDigit = password.contains { DIGITS.contains($0) }
    let hasSpecial = password.contains { SPECIAL.contains($0) }
    
    if hasUpper { charsetSize += 26 }
    if hasLower { charsetSize += 26 }
    if hasDigit { charsetSize += 10 }
    if hasSpecial { charsetSize += SPECIAL.count }
    
    guard charsetSize > 0 else { return 0 }
    
    return Double(password.count) * log2(Double(charsetSize))
}

struct StrengthResult {
    let level: String
    let icon: String
    let color: String
    let description: String
}

func evaluateStrength(_ entropy: Double) -> StrengthResult {
    switch entropy {
    case ..<28:
        return StrengthResult(level: "极弱", icon: "🔴", color: Color.red, description: "容易被暴力破解")
    case ..<36:
        return StrengthResult(level: "弱", icon: "🟠", color: Color.yellow, description: "可能在数小时内被破解")
    case ..<60:
        return StrengthResult(level: "中等", icon: "🟡", color: Color.yellow, description: "可抵御一般攻击")
    case ..<80:
        return StrengthResult(level: "强", icon: "🟢", color: Color.green, description: "可抵御大多数攻击")
    case ..<100:
        return StrengthResult(level: "很强", icon: "🔵", color: Color.blue, description: "非常安全")
    default:
        return StrengthResult(level: "极强", icon: "🟣", color: Color.magenta, description: "几乎不可能被破解")
    }
}

func estimateCrackTime(_ entropy: Double) -> String {
    let attemptsPerSecond: Double = 1e12
    let totalCombinations = pow(2, entropy)
    let seconds = totalCombinations / attemptsPerSecond
    
    let year: Double = 31536000
    
    switch seconds {
    case ..<1: return "瞬间"
    case ..<60: return String(format: "%.1f 秒", seconds)
    case ..<3600: return String(format: "%.1f 分钟", seconds / 60)
    case ..<86400: return String(format: "%.1f 小时", seconds / 3600)
    case ..<year: return String(format: "%.1f 天", seconds / 86400)
    case ..<(year * 100): return String(format: "%.1f 年", seconds / year)
    case ..<(year * 1e6): return String(format: "%.1f 千年", seconds / year / 1000)
    case ..<(year * 1e9): return String(format: "%.1f 百万年", seconds / year / 1e6)
    default: return "宇宙年龄级别"
    }
}

// MARK: - 剪贴板

func copyToClipboard(_ text: String) -> Bool {
    let task = Process()
    task.executableURL = URL(fileURLWithPath: "/usr/bin/pbcopy")
    
    let pipe = Pipe()
    task.standardInput = pipe
    
    do {
        try task.run()
        pipe.fileHandleForWriting.write(text.data(using: .utf8)!)
        pipe.fileHandleForWriting.closeFile()
        task.waitUntilExit()
        return task.terminationStatus == 0
    } catch {
        return false
    }
}

// MARK: - 输出

func printBanner() {
    print("""
    
    \(Color.cyan)╔══════════════════════════════════════════════════════════╗
    ║\(Color.bold)                 强密码生成器 v\(VERSION) (Swift)               \(Color.reset)\(Color.cyan)║
    ║                                                          ║
    ║  功能: 可配置长度 | 强度评估 | 排除混淆字符 | 原生编译    ║
    ╚══════════════════════════════════════════════════════════╝\(Color.reset)
    """)
}

func printPassword(_ index: Int, _ password: String, showAnalysis: Bool = true) {
    print("  [\(index)] \(Color.bold)\(password)\(Color.reset)")
    
    if showAnalysis {
        let entropy = calculateEntropy(password)
        let strength = evaluateStrength(entropy)
        let crackTime = estimateCrackTime(entropy)
        
        print("      \(strength.icon) 强度: \(strength.color)\(strength.level)\(Color.reset) | 熵值: \(String(format: "%.2f", entropy)) bits | 破解时间: \(crackTime)")
        print()
    }
}

func printHelp() {
    print("""
    
    \(Color.bold)用法:\(Color.reset) pwgen [选项]
    
    \(Color.bold)选项:\(Color.reset)
      -l, --length <N>     密码长度 (默认: \(DEFAULT_LENGTH), 范围: \(MIN_LENGTH)-\(MAX_LENGTH))
      -c, --count <N>      生成数量 (默认: \(DEFAULT_COUNT))
      -e, --exclude        排除易混淆字符 (0O1lI|)
      --no-upper           不包含大写字母
      --no-lower           不包含小写字母
      --no-digits          不包含数字
      --no-special         不包含特殊字符
      --plain              纯文本输出
      --json               JSON 格式输出
      -b, --batch          批量模式（非交互）
      -h, --help           显示帮助
    
    \(Color.bold)示例:\(Color.reset)
      pwgen                    # 交互模式
      pwgen -l 16              # 生成16位密码
      pwgen -l 20 -c 5 -b      # 批量生成5个20位密码
      pwgen -l 16 -e           # 排除混淆字符
      pwgen --plain            # 纯文本输出
    
    """)
}

// MARK: - 参数解析

struct Options {
    var length: Int = DEFAULT_LENGTH
    var count: Int = DEFAULT_COUNT
    var excludeConfusing: Bool = false
    var includeUppercase: Bool = true
    var includeLowercase: Bool = true
    var includeDigits: Bool = true
    var includeSpecial: Bool = true
    var plainOutput: Bool = false
    var jsonOutput: Bool = false
    var batchMode: Bool = false
    var showHelp: Bool = false
}

func parseArguments() -> Options {
    var opts = Options()
    var args = Array(CommandLine.arguments.dropFirst())
    
    var i = 0
    while i < args.count {
        let arg = args[i]
        
        switch arg {
        case "-l", "--length":
            i += 1
            if i < args.count, let val = Int(args[i]) {
                opts.length = max(MIN_LENGTH, min(MAX_LENGTH, val))
            }
        case "-c", "--count":
            i += 1
            if i < args.count, let val = Int(args[i]) {
                opts.count = max(1, min(100, val))
            }
        case "-e", "--exclude":
            opts.excludeConfusing = true
        case "--no-upper":
            opts.includeUppercase = false
        case "--no-lower":
            opts.includeLowercase = false
        case "--no-digits":
            opts.includeDigits = false
        case "--no-special":
            opts.includeSpecial = false
        case "--plain":
            opts.plainOutput = true
            opts.batchMode = true
        case "--json":
            opts.jsonOutput = true
            opts.batchMode = true
        case "-b", "--batch":
            opts.batchMode = true
        case "-h", "--help":
            opts.showHelp = true
        default:
            break
        }
        i += 1
    }
    
    return opts
}

// MARK: - 主程序

func generatePasswords(_ opts: Options) -> [(String, Double)] {
    var results: [(String, Double)] = []
    
    for _ in 0..<opts.count {
        let pwd = generatePassword(
            length: opts.length,
            excludeConfusing: opts.excludeConfusing,
            includeUppercase: opts.includeUppercase,
            includeLowercase: opts.includeLowercase,
            includeDigits: opts.includeDigits,
            includeSpecial: opts.includeSpecial
        )
        let entropy = calculateEntropy(pwd)
        results.append((pwd, entropy))
    }
    
    return results
}

func batchMode(_ opts: Options) {
    let passwords = generatePasswords(opts)
    
    if opts.jsonOutput {
        let formatter = ISO8601DateFormatter()
        let timestamp = formatter.string(from: Date())
        
        print("{")
        print("  \"generated_at\": \"\(timestamp)\",")
        print("  \"count\": \(passwords.count),")
        print("  \"passwords\": [")
        
        for (i, (pwd, entropy)) in passwords.enumerated() {
            let strength = evaluateStrength(entropy)
            let comma = i < passwords.count - 1 ? "," : ""
            print("""
                {
                  "index": \(i + 1),
                  "password": "\(pwd)",
                  "length": \(pwd.count),
                  "entropy": \(String(format: "%.2f", entropy)),
                  "strength": "\(strength.level)"
                }\(comma)
            """)
        }
        
        print("  ]")
        print("}")
        return
    }
    
    if opts.plainOutput {
        for (pwd, _) in passwords {
            print(pwd)
        }
        return
    }
    
    // 默认格式
    printBanner()
    print(String(repeating: "-", count: 58))
    print("生成的密码：\n")
    
    for (i, (pwd, _)) in passwords.enumerated() {
        printPassword(i + 1, pwd)
    }
    
    print(String(repeating: "-", count: 58))
}

func interactiveMode(_ opts: Options) {
    var currentOpts = opts
    
    printBanner()
    print("当前配置: 长度=\(currentOpts.length), 数量=\(currentOpts.count), 排除混淆字符=\(currentOpts.excludeConfusing ? "是" : "否")")
    print()
    
    var passwords: [(String, Double)] = []
    
    func regenerate() {
        passwords = generatePasswords(currentOpts)
        print(String(repeating: "-", count: 58))
        print("生成的密码：\n")
        for (i, (pwd, _)) in passwords.enumerated() {
            printPassword(i + 1, pwd)
        }
        print(String(repeating: "-", count: 58))
    }
    
    regenerate()
    
    while true {
        print("\n命令: [1-\(currentOpts.count)] 选择 | [r] 重新生成 | [l] 改长度 | [q] 退出")
        print("请输入: ", terminator: "")
        
        guard let input = readLine()?.trimmingCharacters(in: .whitespaces).lowercased() else {
            break
        }
        
        if let num = Int(input), num >= 1 && num <= currentOpts.count {
            let (pwd, _) = passwords[num - 1]
            print("\n" + String(repeating: "=", count: 58))
            print("你选择的密码: \(Color.bold)\(pwd)\(Color.reset)")
            print(String(repeating: "=", count: 58))
            
            if copyToClipboard(pwd) {
                print("✓ 密码已复制到剪贴板")
            }
            
            print("\n继续生成? [y/n]: ", terminator: "")
            if readLine()?.lowercased() != "y" {
                break
            }
            regenerate()
            
        } else if input == "r" {
            print("\n重新生成...\n")
            regenerate()
            
        } else if input == "l" {
            print("请输入新的密码长度 (\(MIN_LENGTH)-\(MAX_LENGTH)): ", terminator: "")
            if let lenStr = readLine(), let newLen = Int(lenStr), newLen >= MIN_LENGTH && newLen <= MAX_LENGTH {
                currentOpts.length = newLen
                print("\n密码长度已更新为: \(newLen)\n")
                regenerate()
            } else {
                print("无效的长度")
            }
            
        } else if input == "q" {
            print("退出")
            break
            
        } else {
            print("无效输入")
        }
    }
}

// MARK: - 入口

let opts = parseArguments()

if opts.showHelp {
    printHelp()
} else if opts.batchMode {
    batchMode(opts)
} else {
    interactiveMode(opts)
}
