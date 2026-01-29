#!/usr/bin/env node
/**
 * 强密码生成器 - Node.js 版本
 * 可使用 pkg 打包成可执行文件: npx pkg generate-password.js
 */

const crypto = require('crypto');
const { execSync } = require('child_process');

// ==================== 配置 ====================

const VERSION = '2.0';
const DEFAULT_LENGTH = 12;
const DEFAULT_COUNT = 3;
const MIN_LENGTH = 8;
const MAX_LENGTH = 128;

const UPPERCASE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
const LOWERCASE = 'abcdefghijklmnopqrstuvwxyz';
const DIGITS = '0123456789';
const SPECIAL = '!@#$%^&*_+-=[]{}|;:,.<>?';
const CONFUSING = '0O1lI|';

// ==================== 颜色 ====================

const Color = {
    reset: '\x1b[0m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    bold: '\x1b[1m',
};

// ==================== 密码生成 ====================

function secureRandomInt(max) {
    return crypto.randomInt(0, max);
}

function secureRandomChoice(str) {
    return str[secureRandomInt(str.length)];
}

function shuffleArray(arr) {
    const result = [...arr];
    for (let i = result.length - 1; i > 0; i--) {
        const j = secureRandomInt(i + 1);
        [result[i], result[j]] = [result[j], result[i]];
    }
    return result;
}

function generatePassword(options = {}) {
    const {
        length = DEFAULT_LENGTH,
        excludeConfusing = false,
        includeUppercase = true,
        includeLowercase = true,
        includeDigits = true,
        includeSpecial = true,
    } = options;

    let upper = includeUppercase ? UPPERCASE : '';
    let lower = includeLowercase ? LOWERCASE : '';
    let digits = includeDigits ? DIGITS : '';
    let special = includeSpecial ? SPECIAL : '';

    if (excludeConfusing) {
        const filter = (s) => s.split('').filter(c => !CONFUSING.includes(c)).join('');
        upper = filter(upper);
        lower = filter(lower);
        digits = filter(digits);
        special = filter(special);
    }

    const allChars = upper + lower + digits + special;
    if (!allChars) {
        throw new Error('至少需要选择一种字符类型');
    }

    // 确保至少包含每种类型
    const required = [];
    if (upper) required.push(secureRandomChoice(upper));
    if (lower) required.push(secureRandomChoice(lower));
    if (digits) required.push(secureRandomChoice(digits));
    if (special) required.push(secureRandomChoice(special));

    let password = [...required];
    const remaining = length - password.length;
    for (let i = 0; i < remaining; i++) {
        password.push(secureRandomChoice(allChars));
    }

    password = shuffleArray(password);
    return password.join('');
}

// ==================== 密码强度评估 ====================

function calculateEntropy(password) {
    let charsetSize = 0;
    
    const hasUpper = [...password].some(c => UPPERCASE.includes(c));
    const hasLower = [...password].some(c => LOWERCASE.includes(c));
    const hasDigit = [...password].some(c => DIGITS.includes(c));
    const hasSpecial = [...password].some(c => SPECIAL.includes(c));

    if (hasUpper) charsetSize += 26;
    if (hasLower) charsetSize += 26;
    if (hasDigit) charsetSize += 10;
    if (hasSpecial) charsetSize += SPECIAL.length;

    if (charsetSize === 0) return 0;
    return password.length * Math.log2(charsetSize);
}

function evaluateStrength(entropy) {
    if (entropy < 28) return { level: '极弱', icon: '🔴', color: Color.red, desc: '容易被暴力破解' };
    if (entropy < 36) return { level: '弱', icon: '🟠', color: Color.yellow, desc: '可能在数小时内被破解' };
    if (entropy < 60) return { level: '中等', icon: '🟡', color: Color.yellow, desc: '可抵御一般攻击' };
    if (entropy < 80) return { level: '强', icon: '🟢', color: Color.green, desc: '可抵御大多数攻击' };
    if (entropy < 100) return { level: '很强', icon: '🔵', color: Color.blue, desc: '非常安全' };
    return { level: '极强', icon: '🟣', color: Color.magenta, desc: '几乎不可能被破解' };
}

function estimateCrackTime(entropy) {
    const attemptsPerSecond = 1e12;
    const totalCombinations = Math.pow(2, entropy);
    const seconds = totalCombinations / attemptsPerSecond;
    const year = 31536000;

    if (seconds < 1) return '瞬间';
    if (seconds < 60) return `${seconds.toFixed(1)} 秒`;
    if (seconds < 3600) return `${(seconds / 60).toFixed(1)} 分钟`;
    if (seconds < 86400) return `${(seconds / 3600).toFixed(1)} 小时`;
    if (seconds < year) return `${(seconds / 86400).toFixed(1)} 天`;
    if (seconds < year * 100) return `${(seconds / year).toFixed(1)} 年`;
    if (seconds < year * 1e6) return `${(seconds / year / 1000).toFixed(1)} 千年`;
    if (seconds < year * 1e9) return `${(seconds / year / 1e6).toFixed(1)} 百万年`;
    return '宇宙年龄级别';
}

function analyzePassword(password) {
    const entropy = calculateEntropy(password);
    const strength = evaluateStrength(entropy);
    const crackTime = estimateCrackTime(entropy);
    return { password, length: password.length, entropy: entropy.toFixed(2), ...strength, crackTime };
}

// ==================== 剪贴板 ====================

function copyToClipboard(text) {
    try {
        execSync('pbcopy', { input: text, encoding: 'utf8' });
        return true;
    } catch {
        try {
            execSync('xclip -selection clipboard', { input: text, encoding: 'utf8' });
            return true;
        } catch {
            return false;
        }
    }
}

// ==================== 输出 ====================

function printBanner() {
    console.log(`
${Color.cyan}╔══════════════════════════════════════════════════════════╗
║${Color.bold}                强密码生成器 v${VERSION} (Node.js)               ${Color.reset}${Color.cyan}║
║                                                          ║
║  功能: 可配置长度 | 强度评估 | 排除混淆字符 | 跨平台打包  ║
╚══════════════════════════════════════════════════════════╝${Color.reset}
`);
}

function printPassword(index, analysis, showAnalysis = true) {
    console.log(`  [${index}] ${Color.bold}${analysis.password}${Color.reset}`);
    if (showAnalysis) {
        console.log(`      ${analysis.icon} 强度: ${analysis.color}${analysis.level}${Color.reset} | 熵值: ${analysis.entropy} bits | 破解时间: ${analysis.crackTime}`);
        console.log();
    }
}

function printHelp() {
    console.log(`
${Color.bold}用法:${Color.reset} pwgen [选项]

${Color.bold}选项:${Color.reset}
  -l, --length <N>     密码长度 (默认: ${DEFAULT_LENGTH}, 范围: ${MIN_LENGTH}-${MAX_LENGTH})
  -c, --count <N>      生成数量 (默认: ${DEFAULT_COUNT})
  -e, --exclude        排除易混淆字符 (0O1lI|)
  --no-upper           不包含大写字母
  --no-lower           不包含小写字母
  --no-digits          不包含数字
  --no-special         不包含特殊字符
  --plain              纯文本输出
  --json               JSON 格式输出
  -b, --batch          批量模式（非交互）
  -h, --help           显示帮助

${Color.bold}示例:${Color.reset}
  node generate-password.js              # 交互模式
  node generate-password.js -l 16        # 生成16位密码
  node generate-password.js -l 20 -c 5   # 生成5个20位密码
`);
}

// ==================== 参数解析 ====================

function parseArgs() {
    const args = process.argv.slice(2);
    const opts = {
        length: DEFAULT_LENGTH,
        count: DEFAULT_COUNT,
        excludeConfusing: false,
        includeUppercase: true,
        includeLowercase: true,
        includeDigits: true,
        includeSpecial: true,
        plainOutput: false,
        jsonOutput: false,
        batchMode: false,
        showHelp: false,
    };

    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        switch (arg) {
            case '-l':
            case '--length':
                opts.length = Math.max(MIN_LENGTH, Math.min(MAX_LENGTH, parseInt(args[++i]) || DEFAULT_LENGTH));
                break;
            case '-c':
            case '--count':
                opts.count = Math.max(1, Math.min(100, parseInt(args[++i]) || DEFAULT_COUNT));
                break;
            case '-e':
            case '--exclude':
                opts.excludeConfusing = true;
                break;
            case '--no-upper':
                opts.includeUppercase = false;
                break;
            case '--no-lower':
                opts.includeLowercase = false;
                break;
            case '--no-digits':
                opts.includeDigits = false;
                break;
            case '--no-special':
                opts.includeSpecial = false;
                break;
            case '--plain':
                opts.plainOutput = true;
                opts.batchMode = true;
                break;
            case '--json':
                opts.jsonOutput = true;
                opts.batchMode = true;
                break;
            case '-b':
            case '--batch':
                opts.batchMode = true;
                break;
            case '-h':
            case '--help':
                opts.showHelp = true;
                break;
        }
    }
    return opts;
}

// ==================== 主程序 ====================

function generatePasswords(opts) {
    const results = [];
    for (let i = 0; i < opts.count; i++) {
        const pwd = generatePassword(opts);
        results.push(analyzePassword(pwd));
    }
    return results;
}

function batchMode(opts) {
    const passwords = generatePasswords(opts);

    if (opts.jsonOutput) {
        const output = {
            generated_at: new Date().toISOString(),
            count: passwords.length,
            passwords: passwords.map((p, i) => ({
                index: i + 1,
                password: p.password,
                length: p.length,
                entropy: p.entropy,
                strength: p.level,
            })),
        };
        console.log(JSON.stringify(output, null, 2));
        return;
    }

    if (opts.plainOutput) {
        passwords.forEach(p => console.log(p.password));
        return;
    }

    printBanner();
    console.log('-'.repeat(58));
    console.log('生成的密码：\n');
    passwords.forEach((p, i) => printPassword(i + 1, p));
    console.log('-'.repeat(58));
}

async function interactiveMode(opts) {
    const readline = require('readline');
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
    });

    const question = (prompt) => new Promise(resolve => rl.question(prompt, resolve));

    printBanner();
    console.log(`当前配置: 长度=${opts.length}, 数量=${opts.count}, 排除混淆字符=${opts.excludeConfusing ? '是' : '否'}`);
    console.log();

    let passwords = [];

    const regenerate = () => {
        passwords = generatePasswords(opts);
        console.log('-'.repeat(58));
        console.log('生成的密码：\n');
        passwords.forEach((p, i) => printPassword(i + 1, p));
        console.log('-'.repeat(58));
    };

    regenerate();

    while (true) {
        console.log(`\n命令: [1-${opts.count}] 选择 | [r] 重新生成 | [l] 改长度 | [q] 退出`);
        const input = (await question('请输入: ')).trim().toLowerCase();

        const num = parseInt(input);
        if (!isNaN(num) && num >= 1 && num <= opts.count) {
            const selected = passwords[num - 1];
            console.log('\n' + '='.repeat(58));
            console.log(`你选择的密码: ${Color.bold}${selected.password}${Color.reset}`);
            console.log('='.repeat(58));

            if (copyToClipboard(selected.password)) {
                console.log('✓ 密码已复制到剪贴板');
            }

            const cont = (await question('\n继续生成? [y/n]: ')).toLowerCase();
            if (cont !== 'y') break;
            regenerate();
        } else if (input === 'r') {
            console.log('\n重新生成...\n');
            regenerate();
        } else if (input === 'l') {
            const newLen = parseInt(await question(`请输入新的密码长度 (${MIN_LENGTH}-${MAX_LENGTH}): `));
            if (newLen >= MIN_LENGTH && newLen <= MAX_LENGTH) {
                opts.length = newLen;
                console.log(`\n密码长度已更新为: ${newLen}\n`);
                regenerate();
            } else {
                console.log('无效的长度');
            }
        } else if (input === 'q') {
            console.log('退出');
            break;
        } else {
            console.log('无效输入');
        }
    }

    rl.close();
}

// ==================== 入口 ====================

const opts = parseArgs();

if (opts.showHelp) {
    printHelp();
} else if (opts.batchMode) {
    batchMode(opts);
} else {
    interactiveMode(opts);
}
