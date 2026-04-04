INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>紫微斗数分析报告生成器</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f4f4f9;
            color: #333;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }
        .container {
            width: 100%;
            max-width: 800px;
            background: #fff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #2c3e50;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], input[type="date"], select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .checkbox-group {
            display: flex;
            align-items: center;
        }
        input[type="checkbox"] {
            margin-right: 10px;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            background-color: #3498db;
            color: white;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        #downloadBtn {
            background-color: #2ecc71;
            display: none;
        }
        #downloadBtn:hover {
            background-color: #27ae60;
        }
        .preview-area {
            margin-top: 30px;
            border: 1px solid #eee;
            background: #fafafa;
            padding: 15px;
            border-radius: 4px;
            max-height: 500px;
            overflow-y: auto;
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            margin: 0;
            font-family: "Courier New", Courier, monospace;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>紫微斗数分析报告</h1>
    <form id="reportForm">
        <div class="form-group">
            <label for="date_str">出生日期 (YYYY-MM-DD)</label>
            <input type="date" id="date_str" name="date_str" required>
        </div>
        
        <div class="form-group">
            <label for="time_index">出生时辰</label>
            <select id="time_index" name="time_index">
                <option value="0">子时 (23:00 - 01:00)</option>
                <option value="1">丑时 (01:00 - 03:00)</option>
                <option value="2">寅时 (03:00 - 05:00)</option>
                <option value="3">卯时 (05:00 - 07:00)</option>
                <option value="4">辰时 (07:00 - 09:00)</option>
                <option value="5">巳时 (09:00 - 11:00)</option>
                <option value="6">午时 (11:00 - 13:00)</option>
                <option value="7">未时 (13:00 - 15:00)</option>
                <option value="8">申时 (15:00 - 17:00)</option>
                <option value="9">酉时 (17:00 - 19:00)</option>
                <option value="10">戌时 (19:00 - 21:00)</option>
                <option value="11">亥时 (21:00 - 23:00)</option>
                <option value="12">晚子时 (23:00 - 24:00)</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="gender">性别</label>
            <select id="gender" name="gender">
                <option value="男">男</option>
                <option value="女">女</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="date_type">历法</label>
            <select id="date_type" name="date_type">
                <option value="solar">公历 (阳历)</option>
                <option value="lunar">农历 (阴历)</option>
            </select>
        </div>
        
        <div class="form-group checkbox-group" id="leap_group" style="display: none;">
            <input type="checkbox" id="is_leap_month" name="is_leap_month">
            <label for="is_leap_month" style="margin: 0;">是否为闰月</label>
        </div>
        
        <div class="form-group">
            <label for="language">报告语言 (Language)</label>
            <select id="language" name="language">
                <option value="zh-CN">简体中文 (Simplified Chinese)</option>
                <option value="zh-TW">繁体中文 (Traditional Chinese)</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="target_date">目标分析日期（可选，默认今天）</label>
            <input type="date" id="target_date" name="target_date">
        </div>
        
        <div class="button-group">
            <button type="submit" id="generateBtn">生成分析报告</button>
            <button type="button" id="downloadBtn" onclick="downloadMd()">💾 下载 Markdown 文件</button>
        </div>
    </form>

    <div class="preview-area" id="previewArea" style="display: none;">
        <h3>📄 报告预览</h3>
        <pre><code id="preview"></code></pre>
    </div>
</div>

<script>
    let markdownContent = "";

    // 判断是否显示“闰月”勾选框
    document.getElementById("date_type").addEventListener("change", function(e) {
        if (e.target.value === "lunar") {
            document.getElementById("leap_group").style.display = "flex";
        } else {
            document.getElementById("leap_group").style.display = "none";
            document.getElementById("is_leap_month").checked = false;
        }
    });

    document.getElementById("reportForm").addEventListener("submit", async function(e) {
        e.preventDefault();
        
        const btn = document.getElementById("generateBtn");
        btn.innerText = "生成中...";
        btn.disabled = true;
        
        const formData = new FormData(e.target);
        
        // 转换请求数据
        const reqBody = {
            date_str: formData.get("date_str"),
            time_index: parseInt(formData.get("time_index")),
            gender: formData.get("gender"),
            date_type: formData.get("date_type"),
            is_leap_month: formData.get("is_leap_month") === "on",
            target_date: formData.get("target_date") || "",
            language: formData.get("language")
        };
        
        try {
            const res = await fetch("/api/report/generate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(reqBody)
            });
            
            if (res.ok) {
                markdownContent = await res.text();
                document.getElementById("preview").innerText = markdownContent;
                document.getElementById("previewArea").style.display = "block";
                document.getElementById("downloadBtn").style.display = "block";
            } else {
                const err = await res.json();
                alert("生成失败: " + (err.detail || "未知错误"));
            }
        } catch (error) {
            alert("网络错误: " + error.message);
        } finally {
            btn.innerText = "生成分析报告";
            btn.disabled = false;
        }
    });

    function downloadMd() {
        if (!markdownContent) return;
        const blob = new Blob([markdownContent], {type: "text/markdown"});
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        const dateStr = document.getElementById("date_str").value;
        const lang = document.getElementById("language").value;
        if (lang === "zh-TW") {
            a.download = `紫微鬥數報告_${dateStr}.md`;
        } else {
            a.download = `紫微斗数报告_${dateStr}.md`;
        }
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
</script>
</body>
</html>
"""
