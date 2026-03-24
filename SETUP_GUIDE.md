# GitHub 项目创建完整指南

## 🎯 目标

将本地的 `pdf-spec-to-training-data` 项目创建为 GitHub 开源仓库，并配置完整的 CI/CD、文档、Issue 模板等。

## 📦 已准备好的文件

### 核心项目文件 ✅

```
src/                    # 源代码
  pdf_parser.py        - PDF 解析核心
  data_transformer.py  - 数据转换和分块
  dataset_builder.py   - 数据集构建和输出
  utils.py             - 工具函数

scripts/               # 命令行工具
  parse.py             - PDF 解析
  generate_dataset.py  - 完整流程（推荐）
  transform.py         - 数据转换

config/
  config.yaml          - 主配置文件

requirements.txt       - 依赖列表
setup.py              - Python 包配置
```

### GitHub 配置文件 ✅

```
.github/
  ├── workflows/
  │   ├── ci.yml                # CI 流水线（测试 + 发布）
  │   └── code-quality.yml      # 代码质量检查
  ├── ISSUE_TEMPLATE/
  │   ├── bug_report.md         # Bug 报告模板
  │   ├── feature_request.md    # 功能请求模板
  │   ├── docs_issue.md         # 文档问题模板
  │   └── README.md             # 模板说明
  └── dependabot.yml            # 自动依赖更新
  └── pull_request_template.md  # PR 模板

.mergify.yml              # 可选：自动化 PR 合并规则
```

### 文档和许可证 ✅

```
README.md                 # 项目主页（已优化，带徽章）
QUICKSTART.md             # 5 分钟快速开始
docs/USAGE.md             # 详细使用文档
CONTRIBUTING.md           # 贡献指南
CODE_OF_CONDUCT.md        # 行为准则
SECURITY.md               # 安全策略
CHANGELOG.md              # 版本历史
LICENSE                   # MIT 许可证
```

### 基础设施 ✅

```
.gitignore                # Git 忽略文件
.nojekyll                # 禁用 GitHub Pages Jekyll
.github/workflows/       # GitHub Actions
```

## 🚀 创建步骤

### 方式一：自动化脚本（推荐）

```bash
# 1. 生成 GitHub Personal Access Token
# 访问 https://github.com/settings/tokens
# 权限：repo（全控）、write:packages（发布 PyPI 可选）

# 2. 运行脚本
cd /root/.openclaw/workspace/pdf-spec-to-training-data

python github_setup.py --interactive
# 或
python github_setup.py \
  --token YOUR_GITHUB_TOKEN \
  --owner YOUR_GITHUB_USERNAME \
  --repo pdf-spec-to-training-data \
  --create-release
```

脚本会自动：
1. 在 GitHub 创建仓库
2. 配置仓库设置
3. 推送代码
4. 创建初始 Release（可选）

### 方式二：手动创建

#### 第 1 步：在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 仓库名：`pdf-spec-to-training-data`
3. 描述：`将 PDF 规范文档转换为可用于训练的机器学习数据集`
4. 选择 Public 或 Private
5. **不**勾选 "Initialize this repository with a README"
6. 点击 "Create repository"

#### 第 2 步：本地初始化 Git

```bash
cd /root/.openclaw/workspace/pdf-spec-to-training-data

# 初始化
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: PDF to training data converter"

# 重命名主分支为 main
git branch -M main

# 添加远程仓库（替换 YOUR_GITHUB_USERNAME）
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/pdf-spec-to-training-data.git

# 推送
git push -u origin main
```

#### 第 3 步：配置 GitHub Features

在仓库 Settings 页面：

1. **Pages**（可选）：启用 GitHub Pages 托管文档
   - Source: `Deploy from a branch`
   - Branch: `main` / `/docs` 或 `gh-pages`
   - 保存后访问 `https://YOUR_USERNAME.github.io/pdf-spec-to-training-data/`

2. **Actions**：
   - General → Workflow permissions: `Read and write permissions`
   - 允许 Actions 创建和批准 PR

3. **Branches**：
   - 添加 branch protection rule：`main`
   - 勾选：Require status checks before merging
   - 选择需要的 CI 检查（如 ci.yml 中的测试）

4. **Collaborators**：邀请协作者

5. **Secrets**（可选，用于 CI）：
   - `PYPI_API_TOKEN` - 用于自动发布到 PyPI
   - `DOCKER_USERNAME` / `DOCKER_PASSWORD` - 用于 Docker 镜像发布

#### 第 4 步：创建 Release

```bash
# 创建 tag
git tag v1.0.0

# 推送 tag
git push origin v1.0.0

# 然后在 GitHub 上创建 Release（或使用 GitHub CLI）
# https://github.com/YOUR_USERNAME/pdf-spec-to-training-data/releases/new?tag=v1.0.0
```

#### 第 5 步：验证 CI

1. 访问 `https://github.com/YOUR_USERNAME/pdf-spec-to-training-data/actions`
2. 确认 CI 工作流开始运行
3. 检查所有步骤通过

## 📝 重要提醒

### 更新用户名

创建仓库后，需要更新以下地方的 `yourusername`：

1. `README.md` - 所有 GitHub 链接
2. `CONTRIBUTING.md` - 提及 GitHub 仓库的部分
3. `docs/USAGE.md` - 仓库链接
4. `setup.py` - project_urls
5. `CODE_OF_CONDUCT.md` - 联系方式

快速替换：
```bash
cd /root/.openclaw/workspace/pdf-spec-to-training-data
grep -r "yourusername" --include="*.md" --include="*.py" --include="*.yml"
# 使用 sed 批量替换
find . -type f \( -name "*.md" -o -name "*.py" -o -name "*.yml" \) -exec sed -i 's/yourusername/YOUR_GITHUB_USERNAME/g' {} +
```

### 配置 Dependabot

`.github/dependabot.yml` 已配置，自动检查：
- Python 依赖（每周一）
- GitHub Actions（每周一）

### 代码质量保证

CI 工作流包括：
- ✅ **测试** - pytest + 覆盖率（target 80%+）
- ✅ **Lint** - flake8 代码检查
- ✅ **Formatting** - Black 代码格式化检查
- ✅ **Import 排序** - isort 检查
- ✅ **类型检查** - mypy（可选）
- ✅ **安全扫描** - bandit

### Issue 模板

仓库创建后，Contributors 可以创建 Issue 时自动显示模板：
- 🐛 Bug Report
- ✨ Feature Request
- 📚 Documentation

### Pull Request 模板

PR 模板要求填写：
- 变更类型
- 相关 Issue
- 测试方法
- 检查清单

## 🔧 后续优化

### 1. 添加徽章（可选）

在 README 添加更多徽章（替换 `yourusername`）：

```markdown
[![Build Status](https://github.com/yourusername/pdf-spec-to-training-data/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/pdf-spec-to-training-data/actions)
[![codecov](https://codecov.io/gh/yourusername/pdf-spec-to-training-data/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/pdf-spec-to-training-data)
[![PyPI version](https://badge.fury.io/py/pdf-spec-to-training-data.svg)](https://badge.fury.io/py/pdf-spec-to-training-data)
[![Downloads](https://pepy.tech/badge/pdf-spec-to-training-data)](https://pepy.tech/project/pdf-spec-to-training-data)
```

### 2. 配置 PyPI 自动发布

1. 注册 PyPI 账号：https://pypi.org
2. 获取 API token：Account Settings → API tokens
3. 在 GitHub 仓库 Settings → Secrets → Actions 添加：
   - `PYPI_API_TOKEN` = your-token

之后每次创建 Git tag 时（如 `v1.0.1`），CI 会自动发布到 PyPI。

### 3. Docker 镜像（可选）

更新 CI 中的 `docker` job，替换 `yourusername` 为你的 Docker Hub 用户名：

```yaml
- name: Log in to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    tags: |
      yourusername/pdf-spec-to-training-data:latest
      yourusername/pdf-spec-to-training-data:${{ github.sha }}
```

然后配置 Docker Hub secrets：
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`

### 4. 启用 Discussions（可选）

Settings → Features → Discussions ✅

用于社区问答、功能提议投票等。

### 5. 配置 GitHub Pages（可选）

Settings → Pages → Source:
- Branch: `main`
- Folder: `/docs`

然后文档将可在：`https://YOUR_USERNAME.github.io/pdf-spec-to-training-data/`

## 📊 仓库状态检查清单

- [x] 代码已提交到本地 Git
- [ ] GitHub 仓库已创建
- [ ] 代码已推送到 GitHub
- [ ] CI 工作流文件已添加（`.github/workflows/`）
- [ ] Issue 模板已配置（`.github/ISSUE_TEMPLATE/`）
- [ ] PR 模板已配置
- [ ] 许可证已添加（MIT）
- [ ] README 已更新（含徽章）
- [ ] 文档结构完整（docs/）
- [ ] Dependabot 已配置
- [ ] GitHub Pages 已启用（可选）
- [ ] PyPI 自动发布已配置（可选）
- [ ] 协作者已添加

## 🎉 完成！

现在你的项目已准备好：

- ✅ 完整的源代码和文档
- ✅ CI/CD 自动化测试
- ✅ Issue 和 PR 模板
- ✅ 代码质量检查
- ✅ 安全策略
- ✅ 贡献指南
- ✅ 行为准则
- ✅ MIT 开源许可证

### 分享你的项目

1. 在社交媒体分享仓库链接
2. 在相关社区（如 Reddit r/MachineLearning、HackerNews）发帖
3. 提交到 Awesome LLM、Awesome Data 等列表
4. 撰写博客介绍项目

### 管理建议

- **定期 review issues**：及时回复用户反馈
- **保持 CI 健康**：所有检查必须通过才能合并 PR
- **遵循 semantic release**：使用标准和有意义的版本号
- **更新文档**：代码更新时同步更新文档

祝你的开源项目成功！🚀✨
