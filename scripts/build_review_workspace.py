"""Editable worked starter and deterministic offline HTML assembly; no business authoring."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ('layout.html', 'style.css', 'runtime.js', 'review.json', 'requirement.md')
GUIDE = '''# 可运行评审起点 / Runnable review starter

这是设备维修教学样例，不是你的项目，也不是空白项目已通过验收。先读 requirement.md 并替换业务，不继承样例权限、状态、验收或来源。

编辑顺序：
1. requirement.md：先确定当前模块的任务、入口、字段规则、动作结果、拒绝/恢复和可判验收。内容必须来自本项目授权来源。
2. layout.html + runtime.js：产品与业务模拟；先跑通一个完整主链及失败恢复，再扩展其他模块。保留实际存量功能，不为适配样例删页面。
3. layout.html 的 aside：按当前动作写就近业务说明、前端反馈、后端守卫与写入、测试的具体输入和结果。review.json 是同一说明的机器映射；不是另一份业务真相。
4. review.json：替换上下文、评审点、语义覆盖、来源/验收引用；保留通用合同。示例是 R1；R0 仅需就近阅读时按 references/review-workspace.md 裁剪辅助功能。
5. style.css：根据本项目的布局约定调整，不改造成第二套产品。

用 build 命令拼回单 HTML，自动绑定 requirement.md 的 UTF-8 文本 SHA256（CRLF/CR 归一化 LF）。不要手算 hash、整段重写大 HTML 或逆向检查器。分块编辑不影响最终单文件交付。
构建会清空旧验证状态与冷读证据；不会代填授权、不把编译成功写成 PASS。若机器交接已 ready，先更新其绑定再单独验证，不用本草稿构建器覆盖其签署。
修改后运行联合门禁，再做浏览器检查。原型是本地模拟，真实权限/并发与客户签署仍需各自验证。

English: This is an editable worked example, not a blank project or an accepted specification. Replace its business facts and sources. Build assembles local fragments, binds the actual normalized requirement hash, and invalidates verification claims. It neither authorizes policies nor proves behavior.
'''


def text_hash(text: str) -> str:
    return hashlib.sha256(text.replace('\r\n', '\n').replace('\r', '\n').encode('utf-8')).hexdigest()


def init_project(target: Path) -> dict:
    target = target.resolve()
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise ValueError('目标必须是不存在或为空的目录；不会覆盖现有成果 / destination must be empty')
    sample = ROOT / 'examples/medium-review-handoff'
    raw = (sample / 'review-prototype.html').read_text(encoding='utf-8')
    manifest = re.search(r'<script type="application/json" id="review-workspace-manifest">(.*?)</script>', raw, re.S)
    css = re.search(r'<style>(.*?)</style>', raw, re.S)
    code = re.search(r'<script>(.*?)</script>', raw, re.S)
    if not all((manifest, css, code)):
        raise ValueError('官方示例结构已变化，无法安全拆分 / example shape changed')
    layout = raw
    for match, token in sorted(((manifest, '@@ADS_MANIFEST@@'), (css, '@@ADS_STYLE@@'), (code, '@@ADS_RUNTIME@@')), key=lambda item: item[0].start(), reverse=True):
        layout = layout[:match.start(1)] + token + layout[match.end(1):]
    target.mkdir(parents=True, exist_ok=True)
    values = {'layout.html': layout, 'style.css': css[1], 'runtime.js': code[1],
              'review.json': json.dumps(json.loads(manifest[1]), ensure_ascii=False, indent=2) + '\n',
              'requirement.md': (sample / 'requirement.md').read_text(encoding='utf-8'), 'EDITING.md': GUIDE}
    for name, text in values.items():
        (target / name).write_text(text, encoding='utf-8', newline='\n')
    return {'status': 'example_initialized_not_project_accepted', 'directory': str(target), 'files': list(values)}


def build_project(directory: Path, output: Path | None = None) -> dict:
    directory = directory.resolve()
    output = (output or directory / 'prototype.html').resolve()
    inputs = {name: directory / name for name in FILES}
    if output in {path.resolve() for path in inputs.values()}:
        raise ValueError('输出不能覆盖输入片段 / output cannot replace an input')
    missing = [name for name, path in inputs.items() if not path.is_file()]
    if missing:
        raise ValueError('缺少输入片段 / missing fragments: ' + ', '.join(missing))
    contents = {name: path.read_text(encoding='utf-8') for name, path in inputs.items()}
    document = json.loads(contents['review.json'])
    if not isinstance(document, dict) or not isinstance(document.get('baseline'), dict):
        raise ValueError('review.json 必须包含 baseline 对象 / baseline object required')
    if document.get('machine_handoff', {}).get('status') == 'ready':
        raise ValueError('ready 交接需显式复核绑定；本工具只构建未签署草稿 / signed handoff requires rebinding review')
    # Newly assembled projections do not inherit old runtime or reader evidence.
    for point in document.get('review_points', []):
        point['verification_status'] = 'not_run'
        point['evidence_refs'] = []
    if isinstance(document.get('cold_read_contract'), dict):
        document['cold_read_contract'].update(status='pending', evidence_refs=[])
    document['baseline']['hash'] = text_hash(contents['requirement.md'])
    document['baseline']['requirement_ref'] = 'requirement.md'
    if output.parent != directory:
        raise ValueError('单文件输出放在输入目录以保持 PRD 引用有效 / output must stay beside requirement.md')
    if re.search(r'</script\b', contents['runtime.js'], re.I) or re.search(r'</style\b', contents['style.css'], re.I):
        raise ValueError('JS/CSS 包含会提前关闭内嵌资源的结束标签；请转义 / unsafe inline closing tag')
    values = {'@@ADS_MANIFEST@@': json.dumps(document, ensure_ascii=False).replace('<', '\\u003c'),
              '@@ADS_STYLE@@': contents['style.css'], '@@ADS_RUNTIME@@': contents['runtime.js']}
    layout = contents['layout.html']
    for token in values:
        if layout.count(token) != 1:
            raise ValueError('layout.html 须且仅须包含一个 ' + token)
    # One replacement pass prevents business content containing a token from being interpreted again.
    rendered = re.sub('|'.join(map(re.escape, values)), lambda match: values[match[0]], layout)
    output.write_text(rendered, encoding='utf-8', newline='\n')
    return {'status': 'built_not_validated', 'output': str(output), 'baseline_text_sha256': document['baseline']['hash'],
            'output_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'not_proven': ['business completeness', 'browser behavior', 'human review', 'production implementation']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    init = subs.add_parser('init'); init.add_argument('--output', type=Path, required=True)
    build = subs.add_parser('build'); build.add_argument('--project', type=Path, required=True); build.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = init_project(args.output) if args.command == 'init' else build_project(args.project, args.output)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print('BLOCKED REVIEW-BUILD: ' + str(exc)); return 2
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0


if __name__ == '__main__':
    raise SystemExit(main())
