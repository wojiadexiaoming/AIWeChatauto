import subprocess
import sys
import os

def run(cmd):
    print(f"执行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
        sys.exit(1)
    print(result.stdout)
    return result.stdout.strip()

def ensure_gitignore():
    gitignore_path = ".gitignore"
    need_update = False
    lines = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    else:
        print("未找到.gitignore，将自动创建。")
        need_update = True

    if "config.json" not in lines:
        lines.append("config.json")
        need_update = True
    if "cache/" not in lines:
        lines.append("cache/")
        need_update = True
    if "attached_assets/" not in lines:
        lines.append("attached_assets/")
        need_update = True
    if "README.md" not in lines:
        lines.append("README.md")
        need_update = True

    if need_update:
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print("已自动更新 .gitignore，忽略 config.json 和 cache/。")
    else:
        print(".gitignore 已包含 config.json 和 cache/。")

def main():
    ensure_gitignore()

    # 1. 拉取最新代码
    run("git pull origin main --allow-unrelated-histories")

    # 2. 选择版本号
    new_tag = input("请输入新版本号（如 v1.0.1）：").strip()
    if not new_tag:
        print("未输入版本号，退出。")
        return

    # 3. 打标签
    run(f'git tag -a {new_tag} -m "发布 {new_tag}"')

    # 4. 推送代码和标签
    run("git push origin main")
    run("git push origin --tags")

    print(f"已自动推送到GitHub，并打上新版本号 {new_tag}！")

if __name__ == '__main__':
    main()