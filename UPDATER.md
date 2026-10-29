# 开源贡献自动更新

这个更新器维护人工精选的工程项目与 PR 链接：领域、项目顺序、技术分析和展示标签由 `contributions.json` 决定；自动更新仅核验所选 PR 的当前标题、状态和 draft 标记。正文以英文三级标题划分领域，每个领域内按仓库排列为 bullet list，每项展示项目定位和一句贡献摘要；技术分析、PR 链路及验证结果放入各自独立的折叠区，交付版全部默认关闭。它使用 Python 3 标准库和 GitHub 自带的 `GITHUB_TOKEN`，无需安装依赖、创建 PAT 或部署服务。

## 放入个人简介仓库

将以下文件按原路径复制到 `fusheng-ji/fusheng-ji` 的 `main` 分支：

- `README.md`
- `contributions.json`
- `scripts/update_contributions.py`
- `.github/workflows/update-contributions.yml`
- `assets/contributions-data.json`
- `assets/navigation/` 整个目录，包含七个 `*-blue.svg` 导航图标、透明间隔图 `spacer.svg` 和兼容旧链接的深浅色 SVG
- `tests/test_update_contributions.py`（可选），用于本地验证更新器

导航图标统一使用蓝色 `#2f81f7`，背景透明；主页和 Blog 使用蓝色描边，其余图标使用蓝色填充，X 图标的内部填充也一并处理。README 的 `<picture>`、深浅色 `<source>` 和回退图片均指向同一套 `*-blue.svg`；新的文件名避免 GitHub 重定向后继续复用旧图片缓存。旧的深浅色文件也已改为相同蓝色，保留以兼容既有链接。图标统一显示为 30 × 30px，六个透明间隔均为 7px；整组宽 252px，兼顾桌面与 320px、375px 手机页面的单行显示。README 不依赖自定义 CSS；这些静态资源不由开源贡献更新器改写。

`UPDATER.md` 可一并保留；本地 `preview.html` 不需要上传。更新器只替换 README 中下面两个标记之间的内容，请各保留一次：

```markdown
<!-- OPEN-SOURCE:START -->
<!-- OPEN-SOURCE:END -->
```

在 GitHub 仓库的 **Settings → Actions → General** 中允许运行工作流，并检查 **Workflow permissions** 支持写入。工作流的更新任务已明确设置 `contents: write`，使用默认 token；无需新增 secrets。首次上传后，在 **Actions → Update open-source contributions → Run workflow** 手动运行一次。

如果 `main` 的保护规则禁止 bot 直接提交，工作流会失败并留下日志；本配置不会修改保护规则，也不会强制推送。文件必须位于默认分支；此交付版按 `main` 配置。

## 简介与搜索可读性

顶端关键词为 `Video Generation · 3D/4D Reconstruction · AI Infra`。姓名使用一级标题；About Me 保留 TUM 在读身份、Agile Robots 实习与同济学位，以视频生成和 3D/4D 重建为研究主线，具体关联相机可控视频扩散、avatar animation 与稀疏视角重建。AI infrastructure 和 CUDA/Triton GPU kernels 开源项目作为工程理解与实现能力的证据，体现分布式执行、数值正确性和内存效率。职位与博士申请意向统一放在 NOTE 中：视频生成及 3D/4D 重建方向的 Research Scientist 或 Algorithm Engineer，以及 Fall 2027 博士机会。贡献部分继续由 PR 链接、状态和实验条件支持，避免把 Open / Draft 写成已采用或生产成果。

文案参考 [ASu 的 great-resume](https://github.com/Hisn00w/ASu-skills/blob/main/skills/great-resume/SKILL.md)，按真实经历与可核验证据整理求职定位；SEO/GEO 内容依据 [Google 官方 AI 搜索指南](https://developers.google.com/search/docs/appearance/ai-features)，优化重点是可读文本、明确实体、可靠内容和语义层级。GitHub 托管页面的索引和页面级元数据由平台管理，本次仅调整 README 内容；无需加入隐藏关键词、JSON-LD 或额外 AI 文件。

项目公开摘要保持一句简短英文，突出核心工程改动与价值，不罗列完整技术链；已合并和在研部分分开表述，未合并的工作使用 proposed / draft 等限定。新增 PR 的技术链路、性能数字、实验条件及完整证据保留在项目折叠区，由人工维护。当前稿件于 2026-10-22 重新核验，配置保留 59 个精选 PR，其中 58 个 Merged、Open 或 Draft PR 展示在 README 中；未合并关闭的 xDiT #837 保留在配置与快照中，但不展示其链接及专属分析。单纯编辑润色时沿用已有快照，避免将文案修改误记为重新查询 GitHub。

README 保留三个领域和 11 个项目。2026-10-12 补入 11 个关联 PR，涵盖 SGLang 分片注意力、FastVideo GB10 融合布局、RL-Kernel 模型验证和 autograd，以及 gsplat、Warp 梯度修复；Diffusers #14948 已从 Draft 转为 Open。2026-10-13 更新 DiffSynth-Studio：#1720 已合并，新增已合并的 #1718、#1721、#1723、#1725。五项合并工作按 VAE 内存、精度与条件约束、模型驻留与依赖解析组织为独立技术主题，相关指标保留实验条件。2026-10-22 将 FlashAttention #2983 更新为已合并，新增已合并的 SGLang #44260、Open 的 RL-Kernel #571、#575、#557 和 Warp #2072、#2073，并更新 RL-Kernel #549 已完成 GPU 复测的描述；保留轨迹误差、TP1 适配器范围、EP4 训练及导出禁用等限制。PR 状态以 GitHub API 为准；全文精选元数据已核验，人工筛选未改变每周只核验精选 PR 的机制。

开源贡献折叠区内部也使用 bullet list：每个技术主题为一个条目，其分析和 PR 链路位于同一条目内；真实依赖仍使用箭头，独立模块仍使用间隔点。更新器会保留这种列表排版。

页面顺序为 About Me（含 NOTE）→ Experiences → Open Source Contributions。`Experiences` 先展示视频生成与重建研究背景，开源贡献随后展示工程能力。五段经历包含 Agile Robots、TUM 硕士论文、ViDS、CSG-Fusion 和 ImFusion；每段仅保留机构、研究主题、角色或项目性质、日期及一句职责介绍，项目链接保留在简介中。当前研究使用进行时，Oxford VGG 标注为合作机构。该部分在生成标记之外，按人工履历维护，不由每周 PR 更新改写。

本地 `output/experiences-evidence.json` 记录职责依据及此前版本差异，不包含在上传包中。用户已确认 ViDS 标注为 Guided Research、CSG-Fusion 时间为 `Feb 2024–Aug 2025`、TUM 硕士论文时间为 `Feb 2026–Present`。五段经历的日期统一使用月份缩写、年份和连接号 `–`，不单独加粗。邮箱仅保留在顶部导航中，正文不再设置单独的联系模块或重复的邮箱邀请；NOTE 继续保留职位与博士申请意向，其余个人贡献表述保持原样。

## 更新节奏与失败处理

默认每周一 **07:17 UTC** 检查一次，约为柏林夏令时 09:17、冬令时 08:17；也可随时手动运行。这是定时同步，GitHub 可能延迟执行，并非 PR 提交或合并后立即刷新。

只有所选 PR 的元数据或展示配置改变时，才写入有变化的文件；工作流只会提交 `README.md` 和 `assets/contributions-data.json`。没有变化时不制造提交；连续 42 天没有内容变化后，下一次成功检查会刷新核验日期并提交，用于保持定时任务活跃。API 查询失败、限流未恢复、任一所选 PR 缺失或数据校验失败时，会保留上一版输出并让任务失败；可从 Actions 日志查看原因后重试。

在线查询逐个读取人工选定 PR 的详情，不扫描完整贡献历史，也不自动添加新 PR。所选 PR 须由 `fusheng-ji` 提交到公开外部仓库；私有项目和自己的仓库不纳入展示。展示仅保留 Merged、Open 和 Draft：先根据 `merged_at` 判断已合并，再过滤未合并就关闭的 PR，避免把 GitHub 中同样处于 closed 状态的已合并 PR 误删。当前 GitHub 标题放在悬停提示中。

过滤只作用于 README 展示，配置和元数据快照保留完整核验记录，以便后续重新打开的 PR 自动恢复。全被过滤的技术主题、项目和领域不生成空条目；混合主题保留其余 PR 的顺序，但使用中性的 `Selected PRs` 标题并隐藏共同技术分析，依赖箭头改为间隔点，避免跳过已关闭环节后制造新的依赖关系。受影响项目的总述标题和摘要也暂时隐藏，其他主题的说明保持原样；人工调整配置后可恢复更精确的描述。更新器不改写原始工程分析。

GitHub 对公开仓库 60 天无仓库活动的定时工作流会自动禁用。42 天刷新可以在持续成功运行时避免这一情况；如果任务长时间失败或已被禁用，需要在 Actions 中重新 **Enable workflow** 后手动运行。

## 调整项目、技术链与精选 PR

编辑 `contributions.json`：

- `schema_version` 为 `2`，`username` 固定为 `fusheng-ji`。
- `introduction` 是人工维护的英文导语。
- 导语、项目摘要和技术分析直接描述工程问题、改动与收益，避免使用 `I`、`we`、`my`、`our` 等第一人称表达；未完成的工作保留在研语气。
- `projects` 是有序数组。每个项目包含 `repository`（`owner/repo`）、`name`、`title`、`area`、`summary` 和 `expanded`。领域按其在数组中首次出现的顺序生成，同一领域内的项目保持人工数组顺序，不按日期或展开状态重新排列。不同领域的项目可在数组中交错，生成时仍会归入各自领域。
- `area` 是人工维护的英文领域标题，渲染为 Markdown 三级标题（`###`）；交付版使用 `Generative Model Systems`、`GPU Training & Inference` 和 `3D Geometry & Differentiable Rendering`。领域只在组标题中显示，不在各项目折叠区重复添加标签。
- 交付版项目按既定领域顺序排列，新纳入的 NVIDIA Warp 位于 3D 领域；尚未完成的贡献保留 Open 或 Draft，技术说明中的实验数据标明比较对象和条件。
- 项目名称、定位和 `summary` 始终可见。`expanded: false` 表示技术分析、PR 链路及验证结果默认折叠；交付版全部设为 `false`，改为 `true` 可让对应项目默认展开。
- 每个项目的 `chains` 包含 `title`、`kind`、`analysis` 和 `steps`。`kind` 使用 `dependency` 表示真实代码依赖，`stages` 表示模块阶段，`independent` 表示独立修复；技术关系和分析由人工确认。
- 每个 `steps` 条目包含人工展示 `label` 和 `prs` 数组，后者填写 GitHub PR 完整 URL。新增精选 PR 时在这里添加，更新器不会自行扩充列表。

修改后可手动运行工作流，使新的展示配置生效。不要直接编辑 README 的标记区，它会按配置重新生成。`assets/contributions-data.json` 的第 2 版快照保存 PR 核验元数据、日期和对应的展示配置，用于判断内容是否变化；人工稿件仍以配置为准。

从旧版迁移时，请同时替换配置、脚本、工作流和 README。新版不再使用 `assets/contributions-light.svg` 与 `assets/contributions-dark.svg`；本地交付包已移除这两个文件。若个人简介仓库中还保留旧文件，可手动删除，工作流不会自动删除远端文件。

## 本地检查

在个人简介仓库根目录运行以下命令，只检查和预览结果，不写入文件：

```sh
python3 scripts/update_contributions.py --dry-run
```

不在仓库根目录时，可用 `--root /absolute/path/to/profile-repo` 指定目录；默认目录是脚本所在 `scripts` 的上一级。在线检查可使用环境中已有的 `GITHUB_TOKEN`；没有 token 时公开 API 的额度更低。不要把 token 写入文件或提交到 Git。

离线输入为 PR 详情对象数组，须包含配置中全部精选 PR。每项保留 `html_url`、`number`、`user.login`、`title`、`state`、`merged_at`、`draft`、`base.repo.full_name` 和 `base.repo.private`；未合并时 `merged_at` 为 `null`，公开仓库的 `private` 为 `false`。也兼容旧的 GitHub Search item 数组，使用 `pull_request.merged_at` 与 `repository_url`；旧数据应来自公开 PR 查询。离线模式不会补查网络数据。

```sh
python3 scripts/update_contributions.py --dry-run --input-json /absolute/path/to/prs.json
```

去掉 `--dry-run` 会更新本地交付文件；本地脚本不会运行 `git commit` 或 `git push`。自动提交仅发生在 GitHub Actions 工作流中。

如已复制测试文件，可运行以下命令验证精选 PR 核验、状态更新、项目结构、标记外内容保留及失败处理；测试无需 token 或网络：

```sh
python3 -m unittest discover -s tests -v
```

## 参考

- [GitHub PR 详情 API](https://docs.github.com/en/rest/pulls/pulls#get-a-pull-request)
- [定时工作流与 60 天限制](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
- [默认 GITHUB_TOKEN](https://docs.github.com/en/actions/concepts/security/github_token)
- [已固定的官方 checkout v7.0.1](https://github.com/actions/checkout/commit/3d3c42e5aac5ba805825da76410c181273ba90b1)
