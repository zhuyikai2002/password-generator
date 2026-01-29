#!/usr/bin/env swift
//
// Password Generator - macOS Native App
// 使用 WebKit 显示 GUI 界面的原生窗口应用
// 编译: swiftc -framework Cocoa -framework WebKit -o PasswordGenerator PasswordGenerator.swift
//

import Cocoa
import WebKit

// HTML 内容（内嵌）
let htmlContent = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>强密码生成器</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 32px;
            max-width: 460px;
            width: 100%;
        }
        .header { text-align: center; margin-bottom: 24px; }
        .logo {
            width: 64px; height: 64px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 14px;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 12px;
            font-size: 22px; font-weight: bold; color: white;
        }
        h1 { color: #333; font-size: 20px; margin-bottom: 4px; }
        .subtitle { color: #666; font-size: 13px; }
        .settings { margin-bottom: 20px; }
        .setting-group { margin-bottom: 16px; }
        .setting-label {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 6px; color: #333; font-weight: 500; font-size: 13px;
        }
        .setting-value {
            background: #667eea; color: white;
            padding: 2px 10px; border-radius: 10px; font-size: 12px;
        }
        .slider-container { display: flex; align-items: center; gap: 8px; }
        .slider-container input[type="number"] {
            width: 60px; padding: 5px 8px;
            border: 1.5px solid #e0e0e0; border-radius: 6px;
            font-size: 12px; text-align: center;
        }
        .slider-container input[type="number"]:focus { outline: none; border-color: #667eea; }
        input[type="range"] {
            flex: 1; height: 6px; border-radius: 3px;
            background: #e0e0e0; outline: none; -webkit-appearance: none;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none; width: 18px; height: 18px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            cursor: pointer; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        .checkboxes { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .checkbox-item { display: flex; align-items: center; gap: 6px; cursor: pointer; }
        .checkbox-item input { width: 15px; height: 15px; accent-color: #667eea; }
        .checkbox-item span { font-size: 12px; color: #555; }
        .password-display {
            background: #f8f9fa; border: 1.5px solid #e0e0e0;
            border-radius: 10px; padding: 16px; margin-bottom: 12px;
            text-align: center; transition: border-color 0.3s;
        }
        .password-display:hover { border-color: #667eea; }
        .password-text {
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 15px; font-weight: 600; color: #333;
            word-break: break-all; line-height: 1.4; min-height: 22px;
        }
        .strength-bar { margin-top: 12px; }
        .strength-meter {
            height: 5px; background: #e0e0e0;
            border-radius: 3px; overflow: hidden; margin-bottom: 6px;
        }
        .strength-fill { height: 100%; border-radius: 3px; transition: width 0.3s, background 0.3s; }
        .strength-info { display: flex; justify-content: space-between; font-size: 11px; color: #666; }
        .strength-level { font-weight: 600; }
        .buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        button {
            padding: 12px 16px; border: none; border-radius: 8px;
            font-size: 13px; font-weight: 600; cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:active { transform: scale(0.98); }
        .btn-generate {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        .btn-generate:hover { box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5); }
        .btn-copy { background: #f0f0f0; color: #333; }
        .btn-copy:hover { background: #e5e5e5; }
        .btn-copy.copied { background: #4CAF50; color: white; }
        .history { margin-top: 20px; border-top: 1px solid #eee; padding-top: 16px; }
        .history-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .history-title { font-size: 12px; color: #666; font-weight: 500; }
        .history-clear { font-size: 11px; color: #667eea; cursor: pointer; }
        .history-list { max-height: 120px; overflow-y: auto; }
        .history-item {
            display: flex; justify-content: space-between; align-items: center;
            padding: 8px 10px; background: #f8f9fa; border-radius: 6px;
            margin-bottom: 4px; font-family: 'SF Mono', monospace; font-size: 11px;
        }
        .history-copy {
            background: rgba(102, 126, 234, 0.1); border: none;
            cursor: pointer; padding: 3px 8px; font-size: 10px; color: #667eea; border-radius: 4px;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="logo">Aa1.</div>
        <h1>强密码生成器</h1>
        <p class="subtitle">v2.0 macOS 原生版</p>
    </div>
    <div class="settings">
        <div class="setting-group">
            <div class="setting-label">
                <span>密码长度</span>
                <span class="setting-value" id="lengthValue">16</span>
            </div>
            <div class="slider-container">
                <input type="range" id="lengthSlider" min="8" max="128" value="16">
                <input type="number" id="lengthInput" min="8" max="128" value="16">
            </div>
        </div>
        <div class="setting-group">
            <div class="setting-label"><span>字符类型</span></div>
            <div class="checkboxes">
                <label class="checkbox-item"><input type="checkbox" id="uppercase" checked><span>大写字母</span></label>
                <label class="checkbox-item"><input type="checkbox" id="lowercase" checked><span>小写字母</span></label>
                <label class="checkbox-item"><input type="checkbox" id="numbers" checked><span>数字</span></label>
                <label class="checkbox-item"><input type="checkbox" id="symbols" checked><span>特殊字符</span></label>
                <label class="checkbox-item"><input type="checkbox" id="excludeConfusing"><span>排除混淆</span></label>
            </div>
        </div>
    </div>
    <div class="password-display">
        <div class="password-text" id="passwordText">点击生成按钮</div>
        <div class="strength-bar">
            <div class="strength-meter"><div class="strength-fill" id="strengthFill"></div></div>
            <div class="strength-info">
                <span class="strength-level" id="strengthLevel">-</span>
                <span id="entropyInfo">-</span>
            </div>
        </div>
    </div>
    <div class="buttons">
        <button class="btn-generate" id="generateBtn">🔄 生成密码</button>
        <button class="btn-copy" id="copyBtn">📋 复制</button>
    </div>
    <div class="history" id="historySection" style="display:none">
        <div class="history-header">
            <span class="history-title">📜 历史记录</span>
            <span class="history-clear" id="clearHistory">清空</span>
        </div>
        <div class="history-list" id="historyList"></div>
    </div>
</div>
<script>
const CHARS={uppercase:'ABCDEFGHIJKLMNOPQRSTUVWXYZ',lowercase:'abcdefghijklmnopqrstuvwxyz',numbers:'0123456789',symbols:'!@#$%^&*_+-'};
const CONFUSING='0O1lI|';
let history=[];
const $=id=>document.getElementById(id);
function updateLength(v){v=Math.max(8,Math.min(128,parseInt(v)||8));$('lengthSlider').value=v;$('lengthInput').value=v;$('lengthValue').textContent=v;}
$('lengthSlider').addEventListener('input',()=>updateLength($('lengthSlider').value));
$('lengthInput').addEventListener('change',()=>updateLength($('lengthInput').value));
function secureRandom(max){const arr=new Uint32Array(1);crypto.getRandomValues(arr);return arr[0]%max;}
function genPwd(){
    const len=parseInt($('lengthSlider').value),useU=$('uppercase').checked,useL=$('lowercase').checked,useN=$('numbers').checked,useS=$('symbols').checked,excC=$('excludeConfusing').checked;
    let charset='',req=[];
    if(useU){let c=CHARS.uppercase;if(excC)c=c.split('').filter(x=>!CONFUSING.includes(x)).join('');charset+=c;if(c)req.push(c[secureRandom(c.length)]);}
    if(useL){let c=CHARS.lowercase;if(excC)c=c.split('').filter(x=>!CONFUSING.includes(x)).join('');charset+=c;if(c)req.push(c[secureRandom(c.length)]);}
    if(useN){let c=CHARS.numbers;if(excC)c=c.split('').filter(x=>!CONFUSING.includes(x)).join('');charset+=c;if(c)req.push(c[secureRandom(c.length)]);}
    if(useS){charset+=CHARS.symbols;req.push(CHARS.symbols[secureRandom(CHARS.symbols.length)]);}
    if(!charset){alert('请至少选择一种字符类型');return null;}
    let pwd=[...req];for(let i=pwd.length;i<len;i++)pwd.push(charset[secureRandom(charset.length)]);
    for(let i=pwd.length-1;i>0;i--){const j=secureRandom(i+1);[pwd[i],pwd[j]]=[pwd[j],pwd[i]];}
    return pwd.join('');
}
function calcEnt(p){let s=0;if(/[A-Z]/.test(p))s+=26;if(/[a-z]/.test(p))s+=26;if(/[0-9]/.test(p))s+=10;if(/[^A-Za-z0-9]/.test(p))s+=32;return p.length*Math.log2(s||1);}
function evalStr(e){if(e<28)return{level:'极弱',color:'#f44336',pct:15};if(e<36)return{level:'弱',color:'#ff9800',pct:30};if(e<60)return{level:'中等',color:'#ffeb3b',pct:50};if(e<80)return{level:'强',color:'#8bc34a',pct:70};if(e<100)return{level:'很强',color:'#4caf50',pct:85};return{level:'极强',color:'#2196f3',pct:100};}
function crackT(e){const s=Math.pow(2,e)/1e12;if(s<1)return'瞬间';if(s<60)return Math.round(s)+'秒';if(s<3600)return Math.round(s/60)+'分钟';if(s<86400)return Math.round(s/3600)+'小时';if(s<31536000)return Math.round(s/86400)+'天';if(s<31536000*1000)return Math.round(s/31536000)+'年';return'宇宙年龄';}
function updateDisp(p){$('passwordText').textContent=p;const e=calcEnt(p),st=evalStr(e);$('strengthFill').style.width=st.pct+'%';$('strengthFill').style.background=st.color;$('strengthLevel').textContent=st.level;$('strengthLevel').style.color=st.color;$('entropyInfo').textContent='熵值:'+e.toFixed(1)+'bits | 破解:'+crackT(e);}
function addHist(p){history.unshift(p);if(history.length>10)history.pop();renderHist();}
function renderHist(){if(history.length===0){$('historySection').style.display='none';return;}$('historySection').style.display='block';$('historyList').innerHTML=history.map(pwd=>'<div class="history-item"><span>'+pwd+'</span><button class="history-copy" onclick="copyText(\\''+pwd+'\\')">复制</button></div>').join('');}
function copyText(t){navigator.clipboard.writeText(t).then(()=>{$('copyBtn').textContent='✓ 已复制';$('copyBtn').classList.add('copied');setTimeout(()=>{$('copyBtn').textContent='📋 复制';$('copyBtn').classList.remove('copied');},1500);});}
$('generateBtn').addEventListener('click',()=>{const p=genPwd();if(p){updateDisp(p);addHist(p);}});
$('copyBtn').addEventListener('click',()=>{const p=$('passwordText').textContent;if(p&&p!=='点击生成按钮')copyText(p);});
$('clearHistory').addEventListener('click',()=>{history=[];renderHist();});
const initPwd=genPwd();if(initPwd)updateDisp(initPwd);
</script>
</body>
</html>
"""

class AppDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow!
    var webView: WKWebView!
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        // 创建窗口
        let windowRect = NSRect(x: 0, y: 0, width: 500, height: 680)
        window = NSWindow(
            contentRect: windowRect,
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        
        window.title = "强密码生成器"
        window.center()
        window.minSize = NSSize(width: 400, height: 500)
        
        // 创建 WebView
        let config = WKWebViewConfiguration()
        webView = WKWebView(frame: window.contentView!.bounds, configuration: config)
        webView.autoresizingMask = [.width, .height]
        
        // 加载 HTML
        webView.loadHTMLString(htmlContent, baseURL: nil)
        
        window.contentView?.addSubview(webView)
        window.makeKeyAndOrderFront(nil)
        
        // 设置应用激活
        NSApp.activate(ignoringOtherApps: true)
    }
    
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return true
    }
}

// 启动应用
let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
