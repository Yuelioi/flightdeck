# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-03 by 月离 (本会话：preflight 三方审核整改收尾——纠错 B1/B2/B7/B8 + 措辞 C2/C3/C4/C5/C7 全落（protocol 加"三仪式职责分工表"钉 trim owner=landing、walkaround 职责）；triage sketch 提升为 [specs/preflight-tri-review-remediation](specs/2026-06-03-preflight-tri-review-remediation.md)，19 项 dispositioned，仅减重 A1/A3/A4 留 token-reduction。分支仍 unpushed)
**Active focus**: flightdeck 3.0 分支 code-complete、未 push；机械层脚本化(INDEX/init/release) + skill token-reduction 进行中(第一批已落)；待 reload dogfood → 发布 → 合并 main。

1. **token-reduction 余下批次（首要，全部减完再测）** [specs/2026-06-03-token-reduction-design.md](specs/2026-06-03-token-reduction-design.md)：Tier 2 跨文件去重(status flow/80 行 trim/last_updated/HISTORY 行/migration 4-case/pre-3.0)、exit-ritual 内部去重、templates 压缩、A1 拆 migration / A3 git heuristic / A4 拆 protocol；walkaround 压缩待脚本 lint 子命令(scriptable Phase 3)。
2. **行为 dogfood（reload/重装插件后，待减重全完）**：①3.0——git/emit 推断、`### Autonomy overrides` 标准句覆盖、2.3→3.0 迁移改写、when-to-land signal 1/2、walkaround 不报假阳性；②init 重做——干净目录跑首次建档全程。
3. **发布 3.0** [checklists/version-bump.md](checklists/version-bump.md)（marketplace + tag + 同步插件缓存），然后合并分支 → main。
4. 仍开放：INDEX-row `—` 分隔符冲突 [incidents/index-row-summary-delimiter.md](incidents/index-row-summary-delimiter.md)；spec §8 的 no-git HISTORY 格式。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
