# 🚀 推送指南 - 上传到 GitHub

## 步骤 1: 在 GitHub 上创建仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `academic-literature-guide`（或你喜欢的名字）
   - **Description**: 文献导读助手 - 全自动学术文献解读专家
   - **Visibility**: Public（公开）或 Private（私有）
   - **不要勾选** "Add a README file"、"Add .gitignore"、"Choose a license"
3. 点击 **Create repository**

## 步骤 2: 配置 Git 用户信息（首次使用）

```bash
cd "/Users/jefeer/Downloads/我的任务/文献导读技能分享包"

# 配置你的 GitHub 用户名和邮箱
git config --global user.name "你的 GitHub 用户名"
git config --global user.email "你的 GitHub 邮箱"
```

## 步骤 3: 关联远程仓库

在 GitHub 创建仓库后，复制仓库地址，然后运行：

```bash
# 替换为你的 GitHub 仓库地址
git remote add origin https://github.com/你的用户名/academic-literature-guide.git

# 验证
git remote -v
```

## 步骤 4: 推送到 GitHub

```bash
# 推送到 main 分支
git branch -M main
git push -u origin main
```

## 步骤 5: 验证推送

在浏览器中访问你的 GitHub 仓库，确认文件已上传成功。

---

## 🔧 常见问题

### Q1: 提示认证失败？

**使用 HTTPS**：
- 输入 GitHub 用户名和密码
- 或使用 Personal Access Token（推荐）
  - 生成 Token: https://github.com/settings/tokens
  - 使用 Token 代替密码

**使用 SSH**（推荐）：
```bash
# 生成 SSH 密钥（如已有可跳过）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 添加公钥到 GitHub
cat ~/.ssh/id_ed25519.pub
# 复制输出，粘贴到 https://github.com/settings/keys

# 使用 SSH 地址
git remote set-url origin git@github.com:你的用户名/academic-literature-guide.git
git push -u origin main
```

### Q2: 推送失败，提示 remote 已存在？

```bash
# 删除现有 remote
git remote remove origin

# 重新添加
git remote add origin https://github.com/你的用户名/academic-literature-guide.git
```

### Q3: 想要更新 README 中的用户名？

编辑 `README.md` 文件，将以下内容替换为你的信息：
- `https://github.com/yourusername/academic-literature-guide` → 你的仓库地址
- `your.email@example.com` → 你的邮箱
- `@lobsterai` → 你的 GitHub 用户名

然后提交：
```bash
git add README.md
git commit -m "docs: 更新作者信息"
git push
```

---

## 📦 后续更新

修改文件后推送：

```bash
git add .
git commit -m "feat: 描述你的更新内容"
git push
```

---

## 🎉 完成！

现在你的技能已经发布到 GitHub，可以分享给其他人使用了！

**分享链接**：
```
https://github.com/你的用户名/academic-literature-guide
```
