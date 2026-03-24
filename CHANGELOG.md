# 更新日志

本项目的版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增功能

- (待添加...)

### 改进

- (待添加...)

### Bug 修复

- (待添加...)

### 安全更新

- (待添加...)

---

## [1.0.0] - 2025-03-23

### 新增功能

- ✨ 初始版本发布
- 📄 支持从 PDF 提取文本内容 (pdfplumber)
- 📊 支持表格提取（有线表/无线表自动检测）
- 🔍 支持 OCR 识别扫描件 (Tesseract/PaddleOCR)
- 🧩 多种文本分块策略（固定长度、按段落、按章节）
- 🎯 支持多种输出格式：JSONL、JSON、CSV、TXT、Parquet
- 🧹 文本清洗功能（页眉页脚移除、空白规范化等）
- 📦 批量处理命令行工具
- ⚙️ 配置文件驱动（YAML）
- 🐍 Python API 和命令行接口

### 技术特性

- 并行处理支持（可配置 worker 数量）
- 内存优化处理（大文件支持）
- 中间结果缓存（避免重复解析）
- 详细日志和统计信息
- 错误恢复和继续处理

### 文档

- 📖 完整的 README.md
- 🚀 QUICKSTART.md 快速开始指南
- 📚 docs/USAGE.md 详细使用文档
- 💻 示例代码和脚本
- ⚙️ 完整的配置示例

### 其他

- MIT 许可证
- GitHub Actions CI/CD 配置
- Dependabot 自动依赖更新
- 完整的测试套件

---

## 版本说明

### 版本号格式

`主版本.次版本.修订号` (Major.Minor.Patch)

- **主版本**：不兼容的 API 修改
- **次版本**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 如何选择版本

- **稳定生产**: 使用标签的正式版本（如 1.0.0）
- **测试新功能**: 使用 pre-release 版本或 main 分支
- **最新修复**: 关注 patch 版本更新

---

## 发布流程

1. 更新 CHANGELOG.md，总结变更
2. 更新版本号：
   - src/__init__.py: `__version__`
   - setup.py: `version`
3. 创建 git tag:
   ```bash
   git tag -a v1.1.0 -m "Bump version to 1.1.0"
   git push origin v1.1.0
   ```
4. GitHub Actions 自动发布到 PyPI 和创建 Release
5. 在 Release Notes 中说明更新内容

---

## 感谢

感谢所有为本项目做出贡献的开发者！

---

**注意**: 本项目的每个版本都经过测试验证，但软件总有不确定因素。生产环境使用前请务必进行充分测试。
