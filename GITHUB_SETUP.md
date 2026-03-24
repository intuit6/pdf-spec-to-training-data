# GitHub 项目创建指南

## 项目结构准备

我将为你创建一个标准的GitHub项目仓库，包含：

1. 完善的文档（README、LICENSE、CONTRIBUTING等）
2. 代码仓库结构
3. CI/CD 配置（GitHub Actions）
4. Issue 模板
5. Pull Request 模板
6. 代码质量检查
7. 自动发布配置

让我先在本地创建完整项目结构，然后你可以推送到GitHub。

## 创建步骤

### 1. 创建 .github 目录结构（GitHub 配置）

```
.mkdir -p .github/workflows .github/ISSUE_TEMPLATE .github/pull_request_template
```

### 2. 添加 GitHub Actions 工作流

- Python 包发布
- 代码质量检查（linting、testing）
- 依赖更新（dependabot）

### 3. 创建项目文件

- LICENSE（MIT）
- README.md（已创建）
- .gitignore
- CODE_OF_CONDUCT.md
- CONTRIBUTING.md
- SECURITY.md

### 4. 初始化 Git 仓库

然后你可以推送到 GitHub：
```bash
git init
git add .
git commit -m "Initial commit: PDF to training data converter"
git branch -M main
git remote add origin https://github.com/intuit6/pdf-spec-to-training-data.git
git push -u origin main
```

## 现在让我为项目添加这些文件...
