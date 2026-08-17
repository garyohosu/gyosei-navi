"""MCPサーバーに stdio で直接 JSON-RPC を話し、生の送受信を記録する。

LLM を介さず、initialize → tools/list → tools/call までを確認するための最小クライアント。
"""
import json
import os
import queue
import subprocess
import sys
import threading

REPO = r"C:\project\administrative-procedures-mcp"
CMD = ["uv", "run", "--extra", "excel", "python", "-m", "admin_procedures"]

env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")

print(f"### 起動コマンド: {' '.join(CMD)}")
print(f"### 作業ディレクトリ: {REPO}")
proc = subprocess.Popen(
    CMD, cwd=REPO,
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    env=env, text=True, encoding="utf-8", errors="replace", bufsize=1,
)
print(f"### サーバープロセス起動: pid={proc.pid}")

out_q: "queue.Queue[str]" = queue.Queue()
err_lines: list[str] = []


def _pump(stream, q):
    for line in stream:
        q.put(line)
    q.put("")


def _pump_err(stream):
    for line in stream:
        err_lines.append(line.rstrip())


threading.Thread(target=_pump, args=(proc.stdout, out_q), daemon=True).start()
threading.Thread(target=_pump_err, args=(proc.stderr,), daemon=True).start()


def send(obj):
    line = json.dumps(obj, ensure_ascii=False)
    print(f"\n>>> REQUEST\n{line}")
    proc.stdin.write(line + "\n")
    proc.stdin.flush()


def recv(timeout=90):
    try:
        line = out_q.get(timeout=timeout)
    except queue.Empty:
        print(f"!!! {timeout}秒以内に応答なし")
        return None
    if not line.strip():
        print("!!! ストリーム終了")
        return None
    print(f"<<< RESPONSE\n{line.rstrip()}")
    return json.loads(line)


try:
    # 1. initialize
    send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-11-25",
        "capabilities": {},
        "clientInfo": {"name": "gyosei-navi-evidence-probe", "version": "1.0"},
    }})
    init = recv()

    send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    # 2. tools/list
    send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    tools = recv()
    if tools and "result" in tools:
        names = [t["name"] for t in tools["result"].get("tools", [])]
        print(f"\n### 取得したツール名: {names}")

    # 3. tools/call — 引数なしで呼べる list_datasets
    send({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
          "params": {"name": "list_datasets", "arguments": {}}})
    recv()

    # 4. tools/call — 実際に集計させる
    send({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {
        "name": "summarize_records",
        "arguments": {"dataset_id": "procedures-survey-r6",
                      "group_by": ["所管府省庁"], "metrics": ["count"]},
    }})
    recv()
finally:
    proc.stdin.close()
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.terminate()
    print(f"\n### サーバー終了コード: {proc.returncode}")
    if err_lines:
        print("### サーバーの stderr:")
        for line in err_lines[:40]:
            print(f"    {line}")
