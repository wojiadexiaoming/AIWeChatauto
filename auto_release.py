import subprocess
import sys

def run(cmd):
    print(f"执行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
        sys.exit(1)
    print(result.stdout)
    return result.stdout.strip()

def main():
    # 1. 拉取最新代码
    run("git pull origin main")

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