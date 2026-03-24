# 贡献指南

感谢你考虑为 **PDF Spec to Training Data** 项目做贡献！🎉

本指南旨在帮助你了解如何参与项目开发。

## 行为准则

本项目遵守 [Contributor Covenant](https://www.contributor-covenant.org/) 行为准则。请阅读 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

## 如何贡献

### 报告 Bug

如果你发现了一个 bug：

1. 检查 [Issue](https://github.com/yourusername/pdf-spec-to-training-data/issues) 是否已经存在类似问题
2. 如果没有，[创建新 Issue](https://github.com/yourusername/pdf-spec-to-training-data/issues/new)，使用 **Bug Report** 模板
3. 提供：
   - 清晰的问题描述
   - 复现步骤
   - 期望和实际行为
   - 环境信息（OS、Python版本等）
   - 相关日志和截图

### 提议新功能

1. 先搜索 Issue 看是否已有类似提议
2. [创建新 Issue](https://github.com/yourusername/pdf-spec-to-training-data/issues/new)，使用 **Feature Request** 模板
3. 描述：
   - 你要解决什么问题
   - 建议的解决方案
   - 用例和受益者
   - 技术考虑（是否破坏API、需要新依赖等）

### 提交 Pull Request

#### 前置准备

1. Fork 本仓库
2. 克隆到本地：
   ```bash
   git clone https://github.com/yourusername/pdf-spec-to-training-data.git
   cd pdf-spec-to-training-data
   ```
3. 创建新的分支：
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

#### 开发流程

1. **设置开发环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .[dev]
   ```

2. **进行修改**
   - 遵循现有代码风格（使用 `black` 和 `isort`）
   - 添加必要的测试
   - 更新相关文档

3. **代码格式化和检查**
   ```bash
   # 格式化代码
   black src/ tests/
   isort src/ tests/

   # Lint 检查
   flake8 src/

   # 运行测试
   pytest tests/ -v
   ```

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   # 或
   git commit -m "fix: fix bug description"
   ```

   **提交信息格式**（遵循 [Conventional Commits](https://www.conventionalcommits.org/)）：
   - `feat:` 新功能
   - `fix:` bug修复
   - `docs:` 文档更新
   - `style:` 代码格式调整（不影响功能）
   - `refactor:` 重构
   - `test:` 测试相关
   - `chore:` 构建或工具变动

5. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**
   - 访问 GitHub 点击 "Compare & pull request"
   - 填写 PR 模板
   - 关联相关 Issue
   - 请求审查（如果需要）

#### 审查流程

- 所有 PR 需要至少一个 Maintainer 审查通过
- 确保所有 CI 检查通过（测试、lint、格式化）
- 根据审查意见进行修改
- 使用 "Squash and merge" 合并 PR

## 开发指南

### 代码结构

```
pdf-spec-to-training-data/
├── src/                    # 源代码
│   ├── pdf_parser.py      # PDF 解析
│   ├── data_transformer.py # 数据转换
│   ├── dataset_builder.py  # 数据集构建
│   └── utils.py            # 工具函数
├── tests/                  # 测试
├── config/                 # 配置文件
├── scripts/                # 命令行脚本
├── examples/               # 使用示例
└── docs/                   # 详细文档
```

### 添加新功能

1. **添加新输出格式**
   - 在 `DatasetBuilder` 中添加 `_save_xxx` 方法
   - 在配置文件中添加对应选项
   - 更新文档和示例

2. **添加新的分块策略**
   - 在 `TextChunker` 中添加 `_chunk_xxx` 方法
   - 更新策略映射
   - 添加配置选项和测试

3. **添加新的清洗规则**
   - 在 `TextCleaner` 中添加处理逻辑
   - 更新配置文件
   - 提供示例

### 测试

#### 单元测试

```python
# tests/test_pdf_parser.py
def test_pdf_parsing():
    parser = PDFParser()
    metadata, pages = parser.parse("tests/sample.pdf")
    assert len(pages) > 0
    assert metadata.total_pages == len(pages)
```

#### 集成测试

```python
# tests/test_integration.py
def test_full_pipeline():
    # 测试完整流程
    pass
```

运行所有测试：
```bash
pytest tests/ -v --cov=src
```

### 文档

- 更新 README.md 或 QUICKSTART.md 中的使用说明
- 在 docs/ 添加详细文档（USAGE.md）
- 更新代码注释和 docstrings
- 更新示例脚本

### 版本发布

项目使用语义化版本（SemVer）：

- **Major** (x.0.0): 破坏性变更
- **Minor** (x.y.0): 新功能，向后兼容
- **Patch** (x.y.z): bug 修复

发布流程：
1. 更新 CHANGELOG.md
2. 更新版本号（setup.py、src/__init__.py）
3. 创建 git tag：
   ```bash
   git tag -a v1.1.0 -m "Release version 1.1.0"
   git push origin v1.1.0
   ```
4. GitHub Actions 会自动发布到 PyPI 和创建 GitHub Release

## 需要帮助？

- 查看 [USAGE.md](docs/USAGE.md) 了解详细使用说明
- 查看示例代码在 [examples/](examples/)
- 搜索 [Issues](https://github.com/yourusername/pdf-spec-to-training-data/issues)
- 创建新 Issue 提问

## 感谢

感谢所有为本项目做出贡献的开发者和用户！❤️

## 许可证

By contributing, you agree that your contributions will be licensed under the MIT License.
