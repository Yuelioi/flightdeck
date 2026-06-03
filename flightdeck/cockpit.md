# Cockpit — flightdeck (the flightdeck project itself)

**Last updated**: 2026-06-03 by 月离 (本会话续：bump_version.py 发布助手；flightdeck_init.py 把 init 脚本化（12 写→1 调用、省~5k token、灭 scaffold-ships-verbatim）接进 Branch-0；token-reduction 第一批——preflight SKILL 158→127 拆 setup.md、5 跨文件漂移修、folder-semantics/protocol 去重，升 [specs/token-reduction](specs/2026-06-03-token-reduction-design.md)。分支仍 unpushed)
**Active focus**: flightdeck 3.0 分支 code-complete、未 push；机械层脚本化(INDEX/init/release) + skill token-reduction 进行中(第一批已落)；待 reload dogfood → 发布 → 合并 main。

## Next session

1. **行为 dogfood（reload/重装插件后）**：①3.0——git/emit 推断、`### Autonomy overrides` 标准句覆盖、2.3→3.0 迁移改写、when-to-land signal 1/2、walkaround 不报假阳性；②init 重做——干净目录跑首次建档全程（git 检测+copy 全布局+interview+AGENTS 询问）。
2. **发布 3.0** [checklists/version-bump.md](checklists/version-bump.md)（marketplace + tag + 同步插件缓存），然后合并分支 → main。
3. **token-reduction 余下批次** [specs/2026-06-03-token-reduction-design.md](specs/2026-06-03-token-reduction-design.md)：Tier 2 跨文件去重、templates、walkaround(待脚本 lint 子命令)、A1 拆 migration / A3 git heuristic。
4. **preflight 纠错** [sketches/preflight-tri-review-triage.md](sketches/preflight-tri-review-triage.md)：B1/B3 等（减重项 A1/A2/A3 已并入 token-reduction spec）。
5. 仍开放：INDEX-row `—` 分隔符冲突 [incidents/index-row-summary-delimiter.md](incidents/index-row-summary-delimiter.md)；spec §8 的 no-git HISTORY 格式。

## Hanging tasks

- (none)

## Note on dogfooding

This `flightdeck/` is the flightdeck project's own workbench. `incidents/` / `checklists/` here document **maintaining the flightdeck tool**, not using it on other projects. All `applies_to:` frontmatter must target flightdeck-project paths (`skills/`, `hooks/`, `scaffolds/`, etc.) — never `applies_to: general`.

Users running flightdeck in their own projects see their own `flightdeck/`, not this one.
