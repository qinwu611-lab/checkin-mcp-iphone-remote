# -*- coding: utf-8 -*-
"""查岗MCP 完整示例（fastmcp-slim），含 send_iphone_cmd 遥控工具

部署：
    pip install fastmcp-slim requests
    python server.py  # 监听 0.0.0.0:8000

注意：mcp.run() 必须在所有 @mcp.tool() 定义之后！
"""
from fastmcp import FastMCP
import requests
import os
import subprocess

ORIGIN = os.environ.get("ORIGIN_API", "http://127.0.0.1:9000")  # 后端地址
BARK_KEY = os.environ.get("BARK_API_KEY", "")

mcp = FastMCP("查岗MCP")


def _fetch():
    try:
        r = requests.get(f"{ORIGIN}/activity/summary", timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def check_on_wife(limit: int = 10) -> str:
    """查岗屿宝的手机活动：查看最近打开的App和使用时长，并附带屿宝iPhone最新的电量/位置/天气/亮度/音量"""
    data = _fetch()
    if "error" in data:
        return f"查岗失败：{data['error']}"
    dev = data.get("device") or {}
    lines = []
    if dev:
        parts = []
        for k, label in [("device_name", "设备"), ("battery", "电量"), ("location", "位置"),
                         ("weather", "天气"), ("brightness", "亮度"), ("volume", "音量")]:
            if dev.get(k):
                parts.append(f"{label}:{dev[k]}")
        if parts:
            lines.append(" | ".join(parts))
    apps = data.get("recent_apps", [])
    ses = data.get("sessions", {})
    if apps:
        lines.append(f"最近打开：{','.join(apps)}")
    if ses:
        for app, secs in sorted(ses.items(), key=lambda x: x[1], reverse=True):
            m, s = divmod(secs, 60)
            lines.append(f"{app}: {m}分{s}秒")
    return "\n".join(lines) if lines else "暂无记录"


@mcp.tool()
def check_wife_life() -> str:
    """单独查看屿宝iPhone的最新状态：电量、位置、天气、亮度、音量、设备型号、上报时间"""
    data = _fetch()
    if "error" in data:
        return f"查询失败：{data['error']}"
    dev = data.get("device") or {}
    lines = []
    labels = [("device_name", "设备型号"), ("battery", "电量"), ("location", "位置"),
              ("weather", "天气"), ("brightness", "亮度"), ("volume", "音量"), ("updated_at", "上报时间")]
    for k, label in labels:
        v = dev.get(k)
        if v:
            lines.append(f"{label}：{v}")
    return "\n".join(lines) if lines else "暂无状态数据"


@mcp.tool()
def bark_alert(title: str = "哥哥", content: str = "") -> str:
    """给屿宝手机发推送弹窗（Bark通知），查岗后可用它给屿宝发消息"""
    if not content:
        return "内容不能为空"
    url = f"https://api.day.app/{BARK_KEY}/{title}/{content}"
    try:
        r = requests.get(url, timeout=10)
        return "推送成功" if r.status_code == 200 else "推送失败"
    except Exception as e:
        return f"推送异常：{e}"


@mcp.tool()
def send_iphone_cmd(cmd: str = "测试") -> str:
    """通过邮件给屿宝iPhone发快捷指令：cmd为"回来"时手机切回App，"睡觉"时手机熄屏"""
    if cmd not in ("回来", "睡觉", "测试"):
        return f"命令必须是：回来 / 睡觉 / 测试"
    try:
        r = subprocess.run(
            ["python3", os.path.join(os.path.dirname(__file__), "send_email.py"), cmd, ""],
            capture_output=True, text=True, timeout=30,
        )
        if "已发送" in r.stdout:
            return f"邮件已发送：主题={cmd}，iPhone应已触发快捷指令"
        return f"发送失败：{r.stderr or r.stdout}"
    except Exception as e:
        return f"发送异常：{e}"


if __name__ == "__main__":
    # 必须在所有 @mcp.tool() 定义之后调用，否则后面的工具不会注册！
    mcp.run(transport="http", host="0.0.0.0", port=8000)
