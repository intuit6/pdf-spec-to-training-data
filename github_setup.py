#!/usr/bin/env python3
"""
GitHub 仓库创建和推送脚本

用法：
  python github_setup.py --token YOUR_GITHUB_TOKEN --owner intuit6 --repo pdf-spec-to-training-data

或使用交互模式：
  python github_setup.py --interactive

步骤：
1. 在 GitHub 上创建新仓库（或使用已有仓库）
2. 配置仓库设置（保护分支、Actions权限等）
3. 推送本地代码
4. 创建初始 release（可选）
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ 需要安装 requests 库: pip install requests")
    sys.exit(1)


def run_git(cmd, check=True):
    """运行 git 命令"""
    print(f"$ git {cmd}")
    result = subprocess.run(
        f"git {cmd}",
        shell=True,
        capture_output=True,
        text=True
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr and check:
        print("错误:", result.stderr)
    return result.returncode == 0


def create_github_repo(token, owner, repo, description="", private=False):
    """在 GitHub 上创建仓库"""
    url = f"https://api.github.com/repos/{owner}/{repo}"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "name": repo,
        "description": description or "将 PDF 规范文档转换为训练数据集",
        "private": private,
        "auto_init": False,
        "gitignore_template": "Python",
        "license_template": "mit"
    }

    response = requests.post("https://api.github.com/orgs/{}/repos".format(owner) if owner else "https://api.github.com/user/repos", json=data)
    if response.status_code == 201:
        repo_info = response.json()
        print(f"✓ 仓库创建成功: {repo_info['html_url']}")
        return repo_info['ssh_url'] if 'ssh_url' in repo_info else repo_info['clone_url']
    elif response.status_code == 422:
        print(f"⚠️  仓库可能已存在: {owner}/{repo}")
        return f"https://github.com/{owner}/{repo}.git"
    else:
        print(f"❌ 创建失败: {response.status_code}")
        print(response.text)
        return None


def setup_repo_settings(owner, repo, token):
    """配置仓库设置（分支保护、Actions权限等）"""
    print("\n配置仓库设置...")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    base_url = f"https://api.github.com/repos/{owner}/{repo}"

    # 1. 启用 Issues
    requests.patch(
        f"{base_url}",
        headers=headers,
        json={"has_issues": True}
    )

    # 2. 启用 Wiki
    requests.patch(
        f"{base_url}",
        headers=headers,
        json={"has_wiki": True}
    )

    print("✓ 仓库设置完成（Issues、Wiki 已启用）")


def push_to_github(remote_url, branch="main"):
    """推送代码到 GitHub"""
    print("\n推送代码到 GitHub...")

    steps = [
        ("init", f"init"),
        ("add remote", f"remote add origin {remote_url}"),
        ("add all", "add ."),
        ("commit", 'commit -m "Initial commit: PDF to training data converter"'),
        ("branch", f"branch -M {branch}"),
        ("push", f"push -u origin {branch}"),
    ]

    for name, cmd in steps:
        if not run_git(cmd):
            print(f"❌ 步骤失败: {name}")
            return False

    print(f"✓ 代码已推送到: {remote_url}")
    return True


def create_release(token, owner, repo, version="v1.0.0"):
    """创建 GitHub Release"""
    print("\n创建 Release...")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 获取最新 commit
    response = requests.get(f"https://api.github.com/repos/{owner}/{repo}/commits")
    if response.status_code != 200:
        print("⚠️  无法获取 commits，跳过 release 创建")
        return False

    latest_commit = response.json()[0]['sha']

    # 创建 release
    data = {
        "tag_name": version,
        "target_commitish": latest_commit,
        "name": f"Release {version}",
        "body": f"""## 更新内容

### 🎉 初始版本 v1.0.0

- PDF 文本和表格提取
- 多种输出格式（JSONL、CSV、TXT、Parquet）
- 智能分块策略
- 配置文件和命令行工具
- 完整文档和示例

详见 [CHANGELOG.md](https://github.com/{owner}/{repo}/blob/{version}/CHANGELOG.md) 和 [文档](https://github.com/{owner}/{repo}/blob/{version}/README.md)。

### 📦 安装
```bash
pip install git+https://github.com/{owner}/{repo}.git
```

### 🚀 快速开始
```bash
python scripts/generate_dataset.py --config config/config.yaml
```

**Full Changelog**: https://github.com/{owner}/{repo}/compare/v0.1.0...{version}""",
        "draft": False,
        "prerelease": False
    }

    response = requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/releases",
        headers=headers,
        json=data
    )

    if response.status_code == 201:
        release = response.json()
        print(f"✓ Release 创建成功: {release['html_url']}")
        return True
    else:
        print(f"⚠️  Release 创建失败: {response.status_code}")
        print(response.text)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="GitHub 仓库创建和推送工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互模式（会提示输入）
  python github_setup.py --interactive

  # 命令行模式
  python github_setup.py \\
    --token YOUR_GITHUB_TOKEN \\
    --owner intuit6 \\
    --repo pdf-spec-to-training-data \\
    --private false

  # 创建私有仓库
  python github_setup.py \\
    --token YOUR_GITHUB_TOKEN \\
    --owner intuit6 \\
    --repo my-private-pdf-tool \\
    --private true
        """
    )

    parser.add_argument("--token", help="GitHub Personal Access Token")
    parser.add_argument("--owner", help="GitHub 用户名或组织名")
    parser.add_argument("--repo", default="pdf-spec-to-training-data", help="仓库名")
    parser.add_argument("--private", action="store_true", help="私有仓库")
    parser.add_argument("--interactive", action="store_true", help="交互模式")
    parser.add_argument("--create-release", action="store_true", help="创建初始 release")
    parser.add_argument("--version", default="v1.0.0", help="Release 版本号")

    args = parser.parse_args()

    # 交互模式
    if args.interactive:
        print("=== GitHub 仓库创建向导 ===\n")

        token = input("GitHub Personal Access Token (需要 repo 权限): ").strip()
        if not token:
            print("❌ 必须提供 token")
            return 1

        owner = input("GitHub 用户名/组织名: ").strip()
        if not owner:
            print("❌ 必须提供 owner")
            return 1

        repo = input(f"仓库名 [{args.repo}]: ").strip() or args.repo
        private = input("私有仓库? (y/N): ").strip().lower() == 'y'
        create_release_opt = input("创建初始 release? (y/N): ").strip().lower() == 'y'

        args.token = token
        args.owner = owner
        args.repo = repo
        args.private = private
        args.create_release = create_release_opt

    # 验证参数
    if not args.token:
        print("❌ 必须提供 --token 或使用 --interactive")
        parser.print_help()
        return 1

    if not args.owner:
        print("❌ 必须提供 --owner 或使用 --interactive")
        parser.print_help()
        return 1

    print(f"\n准备创建仓库: {args.owner}/{args.repo}")
    print(f"私有: {'是' if args.private else '否'}")
    print(f"创建 Release: {'是' if args.create_release else '否'}")

    confirm = input("\n确认继续？ (y/N): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return 0

    # 1. 创建 GitHub 仓库
    print("\n" + "="*60)
    print("步骤 1: 创建 GitHub 仓库")
    print("="*60)

    remote_url = create_github_repo(
        args.token,
        args.owner,
        args.repo,
        private=args.private
    )

    if not remote_url:
        print("❌ 仓库创建失败")
        return 1

    # 2. 配置仓库设置
    print("\n" + "="*60)
    print("步骤 2: 配置仓库设置")
    print("="*60)

    setup_repo_settings(args.owner, args.repo, args.token)

    # 3. 推送代码
    print("\n" + "="*60)
    print("步骤 3: 推送代码")
    print("="*60)

    if not push_to_github(remote_url):
        print("❌ 推送失败")
        return 1

    # 4. 创建 Release
    if args.create_release:
        print("\n" + "="*60)
        print("步骤 4: 创建 Release")
        print("="*60)

        create_release(args.token, args.owner, args.repo, args.version)

    # 完成
    print("\n" + "="*60)
    print("✅ 全部完成！")
    print("="*60)
    print(f"\n仓库地址: https://github.com/{args.owner}/{args.repo}")
    print("\n后续步骤：")
    print("  1. 在 GitHub 仓库 Settings 中配置 Secrets（如 PYPI_API_TOKEN、DOCKER_USERNAME）")
    print("  2. 邀请协作者（Settings -> Collaborators）")
    print("  3. 启用 GitHub Pages（如果需要）：Settings -> Pages -> source: main /docs")
    print("  4. 查看 Actions 运行状态")
    print("  5. 在 README 中更新链接（如果有）")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  已取消")
        sys.exit(130)