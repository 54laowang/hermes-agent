---
name: github-pr-workflow
description: "GitHub PR lifecycle: branch, commit, open, CI, merge."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Pull-Requests, CI/CD, Git, Automation, Merge]
    related_skills: [github-auth, github-code-review]
---

# GitHub Pull Request Workflow

Complete guide for managing the PR lifecycle. Each section shows the `gh` way first, then the `git` + `curl` fallback for machines without `gh`.

## Prerequisites

- Authenticated with GitHub (see `github-auth` skill)
- Inside a git repository with a GitHub remote

### Quick Auth Detection

```bash
# Determine which method to use throughout this workflow
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  # Ensure we have a token for API calls
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi
echo "Using: $AUTH"
```

### Extracting Owner/Repo from the Git Remote

Many `curl` commands need `owner/repo`. Extract it from the git remote:

```bash
# Works for both HTTPS and SSH remote URLs
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
echo "Owner: $OWNER, Repo: $REPO"
```

---

## 1. Branch Creation

### 【检查点】前置条件确认

在创建分支前，确认以下条件：
- ✅ 当前在正确的仓库目录（`git rev-parse --show-toplevel` 返回预期路径）
- ✅ 工作目录干净或已知未提交文件（`git status` 已检查）
- ✅ 目标分支名符合命名规范（见下文）
- ✅ main/master 分支是最新的（或已知要基于的 commit）

**确认方式**：向用户说明即将创建的分支名称和目的，等待确认后再执行。

---

### 分支创建流程

This part is pure `git` — identical either way:

```bash
# 步骤1: 确保远程信息是最新的
git fetch origin

# 步骤2: 切换到基础分支并拉取最新代码
git checkout main && git pull origin main

# 步骤3: 创建并切换到新分支
git checkout -b feat/add-user-authentication

# 步骤4: 验证分支创建成功
git branch --show-current
```

### 输入/输出

**输入**：
- 分支名称（符合命名规范）
- 基础分支（默认 main）

**输出**：
- 新创建的本地分支
- 当前已切换到新分支

### Branch naming conventions
- `feat/description` — new features
- `fix/description` — bug fixes
- `refactor/description` — code restructuring
- `docs/description` — documentation
- `ci/description` — CI/CD changes

## 2. Making Commits

### 【检查点】提交前确认

在执行 commit 前，确认：
- ✅ 已使用 `read_file` 或 `search_files` 检查变更内容
- ✅ 变更符合预期（无意外修改）
- ✅ commit message 符合 Conventional Commits 规范
- ✅ 相关文件已全部 stage（`git status` 已验证）

---

Use the agent's file tools (`write_file`, `patch`) to make changes, then commit:

```bash
# Stage specific files
git add src/auth.py src/models/user.py tests/test_auth.py

# Commit with a conventional commit message
git commit -m "feat: add JWT-based user authentication

- Add login/register endpoints
- Add User model with password hashing
- Add auth middleware for protected routes
- Add unit tests for auth flow"
```

### 输入/输出

**输入**：
- 变更的文件列表
- commit message（符合 Conventional Commits）

**输出**：
- 新的 commit（可通过 `git log -1` 查看）

### Commit message format (Conventional Commits):
```
type(scope): short description

Longer explanation if needed. Wrap at 72 characters.
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `ci`, `chore`, `perf`

## 3. Pushing and Creating a PR

### 【检查点】PR 创建前确认

在推送和创建 PR 前，确认：
- ✅ 本地测试已通过（如有测试）
- ✅ commit history 清晰（`git log --oneline -5` 已检查）
- ✅ PR title 简洁明了（通常与最后一个 commit title 一致）
- ✅ PR body 包含 Summary 和 Test Plan
- ✅ 关联的 issue 已标注（如 Closes #42）

---

### Push the Branch (same either way)

```bash
git push -u origin HEAD
```

### 输入/输出

**输入**：
- 本地分支名称
- PR title 和 body
- 可选：reviewers, labels, base branch

**输出**：
- 远程分支
- PR URL（可通过浏览器访问）

### Create the PR

**With gh:**

```bash
gh pr create \
  --title "feat: add JWT-based user authentication" \
  --body "## Summary
- Adds login and register API endpoints
- JWT token generation and validation

## Test Plan
- [ ] Unit tests pass

Closes #42"
```

Options: `--draft`, `--reviewer user1,user2`, `--label "enhancement"`, `--base develop`

**With git + curl:**

```bash
BRANCH=$(git branch --show-current)

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{
    \"title\": \"feat: add JWT-based user authentication\",
    \"body\": \"## Summary\nAdds login and register API endpoints.\n\nCloses #42\",
    \"head\": \"$BRANCH\",
    \"base\": \"main\"
  }"
```

The response JSON includes the PR `number` — save it for later commands.

To create as a draft, add `"draft": true` to the JSON body.

## 4. Monitoring CI Status

### Check CI Status

**With gh:**

```bash
# One-shot check
gh pr checks

# Watch until all checks finish (polls every 10s)
gh pr checks --watch
```

**With git + curl:**

```bash
# Get the latest commit SHA on the current branch
SHA=$(git rev-parse HEAD)

# Query the combined status
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Overall: {data['state']}\")
for s in data.get('statuses', []):
    print(f\"  {s['context']}: {s['state']} - {s.get('description', '')}\")"

# Also check GitHub Actions check runs (separate endpoint)
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/check-runs \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for cr in data.get('check_runs', []):
    print(f\"  {cr['name']}: {cr['status']} / {cr['conclusion'] or 'pending'}\")"
```

### Poll Until Complete (git + curl)

```bash
# Simple polling loop — check every 30 seconds, up to 10 minutes
SHA=$(git rev-parse HEAD)
for i in $(seq 1 20); do
  STATUS=$(curl -s \
    -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['state'])")
  echo "Check $i: $STATUS"
  if [ "$STATUS" = "success" ] || [ "$STATUS" = "failure" ] || [ "$STATUS" = "error" ]; then
    break
  fi
  sleep 30
done
```

## 5. Auto-Fixing CI Failures

When CI fails, diagnose and fix. This loop works with either auth method.

### Step 1: Get Failure Details

**With gh:**

```bash
# List recent workflow runs on this branch
gh run list --branch $(git branch --show-current) --limit 5

# View failed logs
gh run view <RUN_ID> --log-failed
```

**With git + curl:**

```bash
BRANCH=$(git branch --show-current)

# List workflow runs on this branch
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?branch=$BRANCH&per_page=5" \
  | python3 -c "
import sys, json
runs = json.load(sys.stdin)['workflow_runs']
for r in runs:
    print(f\"Run {r['id']}: {r['name']} - {r['conclusion'] or r['status']}\")"

# Get failed job logs (download as zip, extract, read)
RUN_ID=<run_id>
curl -s -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/logs \
  -o /tmp/ci-logs.zip
cd /tmp && unzip -o ci-logs.zip -d ci-logs && cat ci-logs/*.txt
```

### Step 2: Fix and Push

After identifying the issue, use file tools (`patch`, `write_file`) to fix it:

```bash
git add <fixed_files>
git commit -m "fix: resolve CI failure in <check_name>"
git push
```

### Step 3: Verify

Re-check CI status using the commands from Section 4 above.

### Auto-Fix Loop Pattern

When asked to auto-fix CI, follow this loop:

1. Check CI status → identify failures
2. Read failure logs → understand the error
3. Use `read_file` + `patch`/`write_file` → fix the code
4. `git add . && git commit -m "fix: ..." && git push`
5. Wait for CI → re-check status
6. Repeat if still failing (up to 3 attempts, then ask the user)

## 6. Merging

**With gh:**

```bash
# Squash merge + delete branch (cleanest for feature branches)
gh pr merge --squash --delete-branch

# Enable auto-merge (merges when all checks pass)
gh pr merge --auto --squash --delete-branch
```

**With git + curl:**

```bash
PR_NUMBER=<number>

# Merge the PR via API (squash)
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/merge \
  -d "{
    \"merge_method\": \"squash\",
    \"commit_title\": \"feat: add user authentication (#$PR_NUMBER)\"
  }"

# Delete the remote branch after merge
BRANCH=$(git branch --show-current)
git push origin --delete $BRANCH

# Switch back to main locally
git checkout main && git pull origin main
git branch -d $BRANCH
```

Merge methods: `"merge"` (merge commit), `"squash"`, `"rebase"`

### Enable Auto-Merge (curl)

```bash
# Auto-merge requires the repo to have it enabled in settings.
# This uses the GraphQL API since REST doesn't support auto-merge.
PR_NODE_ID=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['node_id'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/graphql \
  -d "{\"query\": \"mutation { enablePullRequestAutoMerge(input: {pullRequestId: \\\"$PR_NODE_ID\\\", mergeMethod: SQUASH}) { clientMutationId } }\"}"
```

## 7. Complete Workflow Example

```bash
# 1. Start from clean main
git checkout main && git pull origin main

# 2. Branch
git checkout -b fix/login-redirect-bug

# 3. (Agent makes code changes with file tools)

# 4. Commit
git add src/auth/login.py tests/test_login.py
git commit -m "fix: correct redirect URL after login

Preserves the ?next= parameter instead of always redirecting to /dashboard."

# 5. Push
git push -u origin HEAD

# 6. Create PR (picks gh or curl based on what's available)
# ... (see Section 3)

# 7. Monitor CI (see Section 4)

# 8. Merge when green (see Section 6)
```

## Useful PR Commands Reference

|| Action | gh | git + curl ||
||--------|-----|-----------||
|| List my PRs | `gh pr list --author @me` | `curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$OWNER/$REPO/pulls?state=open"` ||
|| View PR diff | `gh pr diff` | `git diff main...HEAD` (local) or `curl -H "Accept: application/vnd.github.diff" ...` ||
|| Add comment | `gh pr comment N --body "..."` | `curl -X POST .../issues/N/comments -d '{"body":"..."}'` ||
|| Request review | `gh pr edit N --add-reviewer user` | `curl -X POST .../pulls/N/requested_reviewers -d '{"reviewers":["user"]}'` ||
|| Close PR | `gh pr close N` | `curl -X PATCH .../pulls/N -d '{"state":"closed"}'` ||
|| Check out someone's PR | `gh pr checkout N` | `git fetch origin pull/N/head:pr-N && git checkout pr-N` ||

---

## 异常处理与边界条件

### 常见错误场景

#### 1. 分支创建失败

**场景**：分支名已存在或命名不规范

```bash
# 错误: fatal: A branch named 'feat/auth' already exists.
# 处理: 检查是否应该切换到现有分支，或使用新名称
git branch -a | grep feat/auth
git checkout feat/auth  # 或使用新名称
```

**场景**：main 分支不存在

```bash
# 错误: fatal: could not find remote ref main
# 处理: 确认默认分支名称
git branch -r  # 查看远程分支
git checkout master  # 或其他默认分支
```

#### 2. Push 失败

**场景**：远程分支已存在或权限不足

```bash
# 错误: ! [rejected] (fetch first)
# 处理: 拉取远程更改
git pull origin feat/auth --rebase
git push origin feat/auth

# 错误: remote: Permission to owner/repo.git denied
# 处理: 检查认证状态
gh auth status  # 或检查 GITHUB_TOKEN
```

#### 3. PR 创建失败

**场景**：API 限流或权限问题

```bash
# 错误: HTTP 403 - API rate limit exceeded
# 处理: 等待或使用认证的 token
# 检查限流状态
curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit

# 错误: HTTP 422 - Validation failed
# 处理: 检查必填字段
# - title 不能为空
# - head 分支必须存在
# - base 分支必须存在
```

#### 4. CI 检查失败

**场景**：测试失败或代码检查不通过

```bash
# 查看详细失败信息
gh run view <RUN_ID> --log-failed

# 常见失败原因：
# - 单元测试失败 → 修复测试用例或代码
# - 代码格式问题 → 运行 linter 自动修复
# - 类型检查失败 → 修复类型注解
```

#### 5. 合并冲突

**场景**：目标分支有新提交

```bash
# 拉取目标分支最新代码
git fetch origin main
git rebase origin/main

# 或使用 merge
git merge origin/main

# 解决冲突后
git add <resolved-files>
git rebase --continue  # 或 git commit
git push origin feat/auth --force-with-lease
```

#### 6. Auto-merge 不生效

**场景**：仓库未启用 auto-merge

```bash
# 错误: Auto-merge is not enabled for this repository
# 处理: 
# 1. 检查仓库设置: Settings → Pull Requests → Allow auto-merge
# 2. 或手动合并: gh pr merge --squash
```

### Fallback 策略

当 `gh` 命令不可用时：

```bash
# 检测可用方法
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  METHOD="gh"
elif [ -n "$GITHUB_TOKEN" ]; then
  METHOD="curl"
else
  echo "❌ 需要配置 GitHub 认证"
  echo "方案1: 安装并认证 gh CLI"
  echo "方案2: 设置 GITHUB_TOKEN 环境变量"
  exit 1
fi
```

---

## 相关资源

### 参考文档
- [GitHub REST API - Pulls](https://docs.github.com/en/rest/pulls/pulls)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub CLI Manual](https://cli.github.com/manual/)

### 相关 Skills
- `github-auth` - GitHub 认证配置
- `github-code-review` - Code Review 最佳实践
- `github-issues` - Issue 管理

### 模板文件

PR Body 模板（参考 `templates/pr-body.md`）：

```markdown
## Summary
<!-- 简要描述这个 PR 做了什么 -->

## Changes
<!-- 列出主要变更 -->
- 
- 

## Test Plan
<!-- 如何验证这些变更 -->
- [ ] 单元测试通过
- [ ] 手动测试场景:
  1. 
  2. 

## Screenshots (if applicable)
<!-- 如有 UI 变更，附上截图 -->

Closes #
```
