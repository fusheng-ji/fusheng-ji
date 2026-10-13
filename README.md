<h1 align="center">Wenbo Ji - 嵇文博</h1>

<p align="center">
  <strong>Video Generation · 3D/4D Reconstruction · AI Infra</strong>
</p>

<p align="center">
  <a href="https://fusheng-ji.github.io/" title="Homepage"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/navigation/homepage-dark.svg"><source media="(prefers-color-scheme: light)" srcset="assets/navigation/homepage-light.svg"><img src="assets/navigation/homepage-light.svg" width="32" height="32" alt="Homepage"></picture></a><img src="assets/navigation/spacer.svg" width="4" height="1" alt=""><a href="https://fusheng-ji.github.io/blog/" title="Blog"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/navigation/blog-dark.svg"><source media="(prefers-color-scheme: light)" srcset="assets/navigation/blog-light.svg"><img src="assets/navigation/blog-light.svg" width="32" height="32" alt="Blog"></picture></a><img src="assets/navigation/spacer.svg" width="4" height="1" alt=""><a href="https://fusheng-ji.github.io/assets/doc/WenboJi_CV_English.pdf" title="CV"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/navigation/cv-dark.svg"><source media="(prefers-color-scheme: light)" srcset="assets/navigation/cv-light.svg"><img src="assets/navigation/cv-light.svg" width="32" height="32" alt="CV"></picture></a><img src="assets/navigation/spacer.svg" width="4" height="1" alt=""><a href="https://scholar.google.com/citations?user=ZTUMczEAAAAJ&amp;hl=en" title="Google Scholar"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/navigation/scholar-dark.svg"><source media="(prefers-color-scheme: light)" srcset="assets/navigation/scholar-light.svg"><img src="assets/navigation/scholar-light.svg" width="32" height="32" alt="Google Scholar"></picture></a><img src="assets/navigation/spacer.svg" width="4" height="1" alt=""><a href="https://x.com/wenbo_ji_" title="X"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/navigation/x-dark.svg"><source media="(prefers-color-scheme: light)" srcset="assets/navigation/x-light.svg"><img src="assets/navigation/x-light.svg" width="32" height="32" alt="X"></picture></a><img src="assets/navigation/spacer.svg" width="4" height="1" alt=""><a href="https://www.linkedin.com/in/wenbo-ji-6950b9187/" title="LinkedIn"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/navigation/linkedin-dark.svg"><source media="(prefers-color-scheme: light)" srcset="assets/navigation/linkedin-light.svg"><img src="assets/navigation/linkedin-light.svg" width="32" height="32" alt="LinkedIn"></picture></a><img src="assets/navigation/spacer.svg" width="4" height="1" alt=""><a href="mailto:wenboji0420@gmail.com" title="Email"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/navigation/email-dark.svg"><source media="(prefers-color-scheme: light)" srcset="assets/navigation/email-light.svg"><img src="assets/navigation/email-light.svg" width="32" height="32" alt="Email"></picture></a>
</p>

## About Me

I'm an M.Sc. student in **Electrical Engineering and Information Technology** at the [Technical University of Munich](https://www.cit.tum.de/en/cit/home/) and a **Research Intern** at [Agile Robots SE](https://www.agile-robots.com/en/). I hold an M.Sc. in **Computer Science** from [Tongji University](https://see.tongji.edu.cn/index.htm) (2025).

My research focuses on **video generation and 3D/4D reconstruction**, from camera-controlled video diffusion and avatar animation to sparse-view reconstruction. My open-source work in **AI infrastructure and CUDA/Triton GPU kernels** complements this research through distributed execution, numerical correctness, and memory-efficient implementation.

> [!NOTE]
> I'm interested in **Research Scientist or Algorithm Engineer roles** focused on **video generation and 3D/4D reconstruction**.
>
> I'm also seeking **Ph.D. opportunities starting in Fall 2027** in 3D/4D scene representation, video generation, and robot world models.

---

## Experiences

- **[Agile Robots SE](https://www.agile-robots.com/en/) — Cross-Embodiment Video Generation**  
  *Research Intern · Apr 2026–Present*

  Developing cross-embodiment video generation to translate egocentric human demonstrations into robot-domain videos for policy learning in dexterous manipulation.

- **[TUM Visual Computing](https://niessnerlab.org/) — Camera-Controlled Video Generation**  
  *Master's Thesis · Feb 2026–Present*

  Developing camera-controlled video diffusion to synthesize human motion and human–scene interactions across changing viewpoints.

- **[TUM Visual Computing](https://niessnerlab.org/) — 3D-Aware Avatar Animation**  
  *Guided Research · Apr 2025–Mar 2026*

  Developed [ViDS](https://fusheng-ji.github.io/ViDS/) by conditioning video diffusion on 3D face tracking, enabling identity-preserving, long-form portrait animation from a single image.

- **[TUM Computer Vision Group](https://cvg.cit.tum.de/) — Sparse-View 3D Reconstruction**  
  *Guided Research · Feb 2024–Aug 2025 · In collaboration with [Oxford VGG](https://www.robots.ox.ac.uk/~vgg/)*

  Co-developed [CSG-Fusion](https://openaccess.thecvf.com/content/ICCV2025W/E2E3D/html/Xia_CSG-Fusion_Consistent_Sparse-View_Gaussian_Splatting_via_Matching-based_Fusion_ICCVW_2025_paper.html) through matching-based pruning, mask-based feature aggregation, cross-view supervision, and experimental evaluation for compact, consistent sparse-view 3D reconstruction.

- **[ImFusion GmbH](https://www.imfusion.com/) / [TUM CAMP](https://www.cs.cit.tum.de/camp/) — Online Long-Term Video Tracking**  
  *Research Intern · Aug 2024–Apr 2025*

  Implemented online inference and EMA-flow initialization for [LiteTracker](https://arxiv.org/abs/2504.09904), supporting low-latency, frame-by-frame tissue tracking in endoscopic video streams.

---

## Open Source Contributions

<!-- OPEN-SOURCE:START -->

Selected engineering contributions span generative model execution, GPU kernels, and differentiable rendering. Each repository is an independent project.

### Generative Model Systems

- **[xDiT](https://github.com/xdit-project/xDiT)** · Reliable distributed generation

  Merged request isolation and cache fixes strengthen distributed generation; further execution fixes remain proposed.

  <details>

  <summary>Technical details and selected PRs</summary>

  - **Request state and collectives.** Request-local state is reset while communication groups are reused. The dedicated-VAE path then creates those groups consistently across DiT ranks, preventing leaks and mismatched collective order.

    Request lifecycle [#836](https://github.com/xdit-project/xDiT/pull/836 "fix(runtime): keep per-request state from leaking into later requests") (Merged) → VAE-rank collectives [#842](https://github.com/xdit-project/xDiT/pull/842 "fix(pipelines): create the VAE-rank latent group once on every rank") (Merged)

  - **Cache validity.** Shape guards prevent incompatible cache reuse; scheduler request hooks additionally reset step counts and residuals for same-shape requests. Regression and pipeline tests exercise consecutive generation calls.

    Shape compatibility [#813](https://github.com/xdit-project/xDiT/pull/813 "fix(cache): restart step caches when the token count changes") (Merged) → Request boundaries [#864](https://github.com/xdit-project/xDiT/pull/864 "fix(cache): restart the TeaCache step period on every request") (Merged)

  - **Sequence and prompt masking.** Valid-token bounds first exclude sequence-parallel padding from attention keys; prompt-specific masks then preserve shorter samples in mixed-length Z-Image and Qwen-Image batches. Current validation uses tiny-model parity; historical pretrained comparisons provide additional output evidence, with ring-attention limitations explicit.

    Valid-key boundaries [#837](https://github.com/xdit-project/xDiT/pull/837 "fix(sp): keep sequence-parallel padding out of attention keys") (Open) → Mixed-length prompt masks [#856](https://github.com/xdit-project/xDiT/pull/856 "fix(sp): honour text masks for batched prompts of different lengths in Z-Image and Qwen-Image") (Open)

  - **Cache layout and execution ownership.** Draft changes align PipeFusion warmup and patch-mode KV layouts, exclude Ideogram padding, and pad/unpad uneven HunyuanVideo shards. A separate runner fix assigns prompt splitting, output gathering, and parallel VAE ownership to one layer each, preventing double processing and missing outputs. These are independent execution contracts, with draft paths still under review.

    Patch-major KV cache [#899](https://github.com/xdit-project/xDiT/pull/899 "fix(cache): store the Ulysses PipeFusion KV cache patch-major") (Draft) · Ideogram attention bounds [#900](https://github.com/xdit-project/xDiT/pull/900 "fix(ideogram4): keep sequence-parallel padding out of attention") (Draft) · HunyuanVideo shard boundaries [#901](https://github.com/xdit-project/xDiT/pull/901 "fix(hunyuan-video): pad sequence-parallel shards when tokens do not divide evenly") (Draft) · Runner and wrapper ownership [#902](https://github.com/xdit-project/xDiT/pull/902 "fix(runner): let one layer own DP, output rank and parallel VAE for legacy pipelines") (Open)

  </details>

- **[SGLang](https://github.com/sgl-project/sglang)** · Native diffusion serving and cache lifecycle

  Merged cache resets isolate requests; proposed Ovis-Image serving extends model integration and attention consistency.

  <details>

  <summary>Technical details and selected PRs</summary>

  - **Native Ovis-Image integration.** A native pipeline connects checkpoint mapping, text conditioning, CFG, TP/SP, offload, and image serving. The PR reports bitwise agreement with pinned Diffusers for tested single-GPU exact-tier runs on B200; parallel runs are checked against explicit BF16 noise controls. Unsupported features fail with explicit errors.

    Ovis-Image model and serving [#43152](https://github.com/sgl-project/sglang/pull/43152 "[diffusion] model: add native Ovis-Image support") (Open)

  - **Request entry to expert state.** Resetting all DiT caches when a request starts covers experts that never execute denoising step zero, preventing stale TeaCache/Spectrum state across requests.

    Per-request DiT reset [#42437](https://github.com/sgl-project/sglang/pull/42437 "[diffusion] Reset DiT cache state at the start of each request") (Merged)

  - **Sharded SDPA consistency.** Eligible exact-tier torch-SDPA calls pad query rows so TP/Ulysses head shards select the unsharded attention kernel. B200 operator and two-GPU Ulysses tests report bitwise agreement; whole-model differences remain. The proposal retains the existing lossless-tier and unaffected backend behavior.

    Exact-tier head shards [#43242](https://github.com/sgl-project/sglang/pull/43242 "[diffusion] keep TP/Ulysses head shards on the unsharded torch SDPA kernel") (Open)

  </details>

- **[vLLM-Omni](https://github.com/vllm-project/vllm-omni)** · Error propagation in diffusion serving

  Typed validation errors retain their original API status through the single-GPU diffusion executor.

  <details>

  <summary>Technical details and selected PRs</summary>

  - **Typed worker errors.** Single-GPU execution retains client-error type and status instead of flattening exceptions into generic server failures, so API responses reflect the original validation error.

    Executor error metadata [#8474](https://github.com/vllm-project/vllm-omni/pull/8474 "[Bugfix] Keep client error status in the single-GPU diffusion executor") (Merged)

  </details>

- **[DiffSynth-Studio](https://github.com/modelscope/DiffSynth-Studio)** · Adapter semantics and memory-efficient execution

  Proposed LoRA scaling and VAE tiling fixes preserve adapter semantics and memory-saving execution.

  <details>

  <summary>Technical details and selected PRs</summary>

  - **Independent pipeline modules.** LoRA loading applies alpha/rank metadata; QwenImage VAE encoding and decoding execute spatial tiling instead of ignoring the requested memory-saving path.

    LoRA scaling [#1719](https://github.com/modelscope/DiffSynth-Studio/pull/1719 "fix(lora): apply the alpha stored in safetensors metadata") (Open) · VAE tiling [#1720](https://github.com/modelscope/DiffSynth-Studio/pull/1720 "fix(qwen-image): implement tiled encode and decode in QwenImageVAE") (Open)

  </details>

- **[Diffusers](https://github.com/huggingface/diffusers)** · Branch-aware video cache integration

  Proposed Wan cache isolation keeps conditional and unconditional guidance branches separate.

  <details>

  <summary>Technical details and selected PRs</summary>

  - **Conditional and unconditional contexts.** Conditional and unconditional calls receive separate cache contexts, preserving classifier-free guidance branch isolation and enabling cached execution in the Wan pipeline.

    Wan V2V cache contexts [#14948](https://github.com/huggingface/diffusers/pull/14948 "Fix missing cache contexts in Wan video-to-video") (Open)

  </details>

### GPU Training &amp; Inference

- **[FastVideo](https://github.com/hao-ai-lab/FastVideo)** · Hardware-aware video inference and training

  Merged Triton layout fusion removes GPU passes; proposed GB10 inference and NVFP4 training extend hardware coverage.

  <details>

  <summary>Technical details and selected PRs</summary>

  - **SM100 and GB10 inference.** A fused Triton kernel removes separate scatter and transpose passes. The PR reports 1.155× end-to-end speedup for Wan2.1-VSA-T2V-14B on one B200 with 50 steps, with bitwise-identical frames in the tested configurations. A proposed GB10/SM121 extension reuses the same fused layout for eligible BF16, tile-64, D128 inference. DGX Spark tests report exact paired outputs for the tested FastWan2.1 1.3B configurations, with memory-safety checks and full-model validation; the reported timing benefit varies by prompt.

    Fused VSA layout [#1900](https://github.com/hao-ai-lab/FastVideo/pull/1900 "[perf] Fuse VSA64 tile layout for SM100 inference") (Merged) → GB10 fused-layout support [#1948](https://github.com/hao-ai-lab/FastVideo/pull/1948 "[perf] Enable VSA64 fused layout on DGX Spark GB10") (Open)

  - **GB10 / SM121 QAT.** Padding-aware NVFP4 scales and SM121 split-path routing underpin forward-consistent dV. The proposed backward reconstructs forward quantization statistics; its training-gradient contract remains under evaluation.

    Quantization and routing prerequisites ([#1933](https://github.com/hao-ai-lab/FastVideo/pull/1933 "[bugfix] NVFP4 fake-quant: mask padding lanes and guard zero-scale groups") (Open) + [#1934](https://github.com/hao-ai-lab/FastVideo/pull/1934 "[bugfix] Keep the split P@V path for Attn-QAT training on GB10 (SM121)") (Open)) → Forward-consistent dV [#1938](https://github.com/hao-ai-lab/FastVideo/pull/1938 "[kernel] GB10: forward-consistent dV for Attn-QAT training") (Open)

  </details>

- **[RL-Kernel](https://github.com/RL-Align/RL-Kernel)** · Model operators and numerical contracts

  Merged CUDA dispatch fixes and proposed kernels target numerical correctness, distributed reproducibility, and logprob efficiency.

  <details>

  <summary>Technical details and selected PRs</summary>

  - **MiniMax-H3 conditioning.** These representative stages belong to a larger PR stack: three-modality AdaLN projection, fused RMSNorm/modulation, and sequence-parallel reductions with fixed accumulation order. Reported BF16 tests on 2/4/8 B200 ranks match single-GPU outputs and gradients bitwise in a norm/residual region with seeded sublayer stand-ins. A one-block closeout adds per-node forward/backward drift reporting; 11 of 17 nodes still use interim operators or provider replay. The latest evidence migration preserves historical measurements.

    AdaLN projection [#485](https://github.com/RL-Align/RL-Kernel/pull/485 "[WS1][CUDA][MiniMax-H3] adaln_projection_3mod: three-modality AdaLN projection (RFC #420 stack 3/9)") (Open) · Fused norm and modulation [#487](https://github.com/RL-Align/RL-Kernel/pull/487 "[WS1][CUDA][MiniMax-H3] h3_rmsnorm: RMSNorm with fused AdaLN modulation (RFC #420 stack 5/9)") (Open) · Sequence-parallel reductions [#494](https://github.com/RL-Align/RL-Kernel/pull/494 "[WS2][CUDA][MiniMax-H3] sp_norm_adaln: sequence-parallel norm/AdaLN/gated residual, byte-equal to WS1 (RFC #420 stack 9/9)") (Open) · One-block drift validation [#539](https://github.com/RL-Align/RL-Kernel/pull/539 "[WS1][CUDA][MiniMax-H3] ws1_one_h3_block: one real block forward/backward with first-drift report (RFC #420 stack 10/10)") (Open)

  - **Qwen3-Next normalization.** The stack restores CUDA dispatch, specifies zero-centred normalization, adds gated forward/backward kernels, then defines GDN decode-state goldens. The final stage supplies PyTorch recurrent and convolution state references. Reference and provider checks expose casting and state differences before model integration.

    CUDA dispatch [#466](https://github.com/RL-Align/RL-Kernel/pull/466 "[WS1][CUDA][Qwen3-Next] Restore CUDA dispatch for rms_norm (RFC #428 stack 1/4)") (Merged) → Zero-centred RMSNorm [#467](https://github.com/RL-Align/RL-Kernel/pull/467 "[WS1][CUDA][Qwen3-Next] C1: zero-centred RMSNorm references and CUDA kernel (RFC #428 stack 2/4)") (Open) → Gated RMSNorm [#468](https://github.com/RL-Align/RL-Kernel/pull/468 "[WS1][CUDA][Qwen3-Next] Gated RMSNorm CUDA kernel for the GDN block (RFC #428 stack 3/4)") (Open) → Decode-state contracts [#469](https://github.com/RL-Align/RL-Kernel/pull/469 "[WS1][CUDA][Qwen3-Next] C6: GDN decode-step goldens and recurrent/conv state contract (RFC #428 stack 4/4)") (Open)

  - **Qwen3-Next integration and reproducibility.** This dependent stack extends the normalization and state contracts through MoE routing, TP4 mixers, full-model rollout/recompute, batch invariance, and fixed-order distributed logprob. Historical single-node 4 × B200 evidence covers 97 batch-invariance cells and 13 NCCL settings: selected-token logprob and LSE match TP1 on the same logits, while entropy is invariant only at a fixed TP degree. The latest \#549 layout update reproduces archived reports; its fresh GPU validation run is pending.

    MoE route/combine [#503](https://github.com/RL-Align/RL-Kernel/pull/503 "[WS1][CUDA][Qwen3-Next] MoE route/combine contract with a batch-invariant grouped expert GEMM (RFC #428 stack 5/8)") (Open) → TP4 model mixers [#507](https://github.com/RL-Align/RL-Kernel/pull/507 "[WS1][CUDA][Qwen3-Next] TP4 GDN, convolution and D=256 attention mixers on real weights (RFC #428 stack 6/8)") (Open) → Rollout/recompute chain [#543](https://github.com/RL-Align/RL-Kernel/pull/543 "[WS1][CUDA][Qwen3-Next] Full-model chain: vLLM rollout vs VIME recompute, raw-bit through two updates and a reload (RFC #428 stack 7/8)") (Open) → Batch-invariance validation [#544](https://github.com/RL-Align/RL-Kernel/pull/544 "[WS1][CUDA][Qwen3-Next] Batch-invariance matrix for the full model, 97/97 cells bitwise (RFC #428 stack 8/8)") (Open) → Distributed logprob parity [#549](https://github.com/RL-Align/RL-Kernel/pull/549 "[WS1][CUDA][Qwen3-Next] TP distributed logprob parity: fixed reduction order, selected-token logprob exact across NCCL settings (RFC #428 stack 9/10)") (Open)

  - **Memory-efficient logp backward.** A fused CUDA backward writes the returned gradient directly, with no extra temporary workspace; older builds retain a bounded chunked fallback. For BF16 logits with 32,768 rows and vocabulary 151,936 on one B200, the PR reports forward/backward peak memory falling from 46.37 to 9.27 GiB and median latency from 57.1 to 27.2 ms versus the previous VJP. The peak still includes the returned gradient.

    Fused logp backward [#495](https://github.com/RL-Align/RL-Kernel/pull/495 "perf(logp): fused zero-workspace backward for the generic CUDA fused logp (#174)") (Open)

  - **Recursive deterministic autograd.** An independent deterministic LogP path composes reusable VJP/JVP primitives and torch.func rules while retaining the first-order fast path. Fresh single-B200 tests cover derivative orders 1–8 in four precisions, with additional FP64 reverse-mode checks through order 10; hardware skips remain separate from passes. External performance for the expanded contract is unmeasured, and the memory figures above apply only to the generic backward proposal.

    Recursive LogP autograd [#547](https://github.com/RL-Align/RL-Kernel/pull/547 "feat(cuda): enable recursive deterministic LogP autograd on B200") (Open)

  </details>

- **[FlashAttention](https://github.com/Dao-AILab/flash-attention)** · SM100 attention kernels and validation

  Proposed SM100 attention fixes address backward correctness, cache isolation, and reproducible kernel validation.

  <details>

  <summary>Technical details and selected PRs</summary>

  - **dV memory transfers.** Deriving V tensor-memory transfers independently of Q/K fixes the SM100 dV epilogue when forward succeeds but backward silently uses the wrong transfer width.

    Asymmetric-head dV [#2975](https://github.com/Dao-AILab/flash-attention/pull/2975 "[CuTe, Bwd, SM100] Fix dV epilogue for asymmetric head dimensions") (Open)

  - **Cache-safe forward.** Sequence-bounded nonpaged V loads zero-fill unused cache rows before P@V, preventing 0 × NaN contamination in dense and packed forward. The PR reports B200 correctness and memory-check coverage; valid V NaNs and paged-KV behavior retain their existing contracts.

    Unused V-cache isolation [#2983](https://github.com/Dao-AILab/flash-attention/pull/2983 "[CuTe, Fwd, SM100] Prevent NaN contamination from unused V cache entries") (Open)

  - **Scheduling and reproducible validation.** Adapts an existing CLC L2-swizzle implementation while preserving STATIC 2CTA compatibility. A separate dense/varlen benchmark records CUDA Graph timings, source revisions, compiler identity, and kernel hashes. The report credits upstream work for the observed register-spill gains.

    CLC and STATIC scheduling [#2976](https://github.com/Dao-AILab/flash-attention/pull/2976 "[CuTe, SM100] Apply L2 swizzling to CLC scheduling and preserve STATIC 2CTA") (Open) · Dense/varlen validation tool [#2982](https://github.com/Dao-AILab/flash-attention/pull/2982 "[CuTe, Fwd, SM100] Add a dense/varlen validation benchmark") (Open)

  </details>

### 3D Geometry &amp; Differentiable Rendering

- **[gsplat](https://github.com/nerfstudio-project/gsplat)** · Robust differentiable rendering

  Proposed rasterization and loss fixes preserve valid outputs and gradients across degenerate inputs.

  <details>

  <summary>Technical details and selected PRs</summary>

  - **Rendering contracts.** Empty scenes retain background outputs and gradient shapes; depth-mode backward handles strided gradients and median-depth channels; degenerate masked selections return a differentiable zero without leaking excluded NaN/Inf values. Targeted regressions cover packed/unpacked rendering, geometry gradients, and zero-loss backward.

    Empty-scene inputs [#1079](https://github.com/nerfstudio-project/gsplat/pull/1079 "[fix] Handle empty scenes in 3DGS and 2DGS rasterization") (Open) · Depth gradients [#1068](https://github.com/nerfstudio-project/gsplat/pull/1068 "[fix] 2DGS: backward in RGB+D / RGB+ED modes and render_median in RGB mode") (Open) · Masked losses [#1082](https://github.com/nerfstudio-project/gsplat/pull/1082 "[fix] Keep degenerate masked losses finite") (Open)

  - **Clamped-alpha geometry gradients.** The 3DGUT backward proposal gates only the alpha-dependent path at the clamp, preserving hit-distance and normal terms for geometry gradients. PyTorch-reference comparisons and a synthetic depth-only optimization check support the correction; remaining scale growth follows the reference and reflects the underconstrained loss.

    Clamped-alpha distance and normals [#1083](https://github.com/nerfstudio-project/gsplat/pull/1083 "[fix] 3DGUT: hit-distance and normal gradients at clamped alpha") (Open)

  </details>

- **[PyTorch3D](https://github.com/facebookresearch/pytorch3d)** · Camera visibility and bounded box overlap

  Proposed visibility and bounded box-clipping fixes prevent invalid feature sampling and CUDA buffer overflow.

  <details>

  <summary>Technical details and selected PRs</summary>

  - **Visibility contract.** World-to-view depth rejects points behind a camera, preventing invalid projections from contributing sampled features and gradients.

    Camera visibility [#2056](https://github.com/facebookresearch/pytorch3d/pull/2056 "Exclude points behind cameras from view sampling") (Open)

  - **Bounded box clipping.** A bounded CUDA workspace first prevents triangle-buffer overflow. Polygon clipping then bounds each clipped triangle to nine vertices, removes that workspace, and aligns CPU/CUDA treatment of coincident faces. On one B200, the PR reports 100 × 100 box pairs dropping from 1.315 to 0.675 ms versus valid upstream controls, using the median of 31 CUDA-event samples; the 22-test box-IoU module passes.

    CUDA capacity bounds [#2059](https://github.com/facebookresearch/pytorch3d/pull/2059 "Fix CUDA box IoU triangle buffer capacity") (Open) → Bounded polygon clipping [#2060](https://github.com/facebookresearch/pytorch3d/pull/2060 "Clip box triangles as polygons in box3d_overlap") (Open)

  </details>

- **[NVIDIA Warp](https://github.com/NVIDIA/warp)** · Half-precision numerical stability

  Draft FP16 SVD and proposed zero-adjoint fixes address distinct forward and backward NaN paths.

  <details>

  <summary>Technical details and selected PRs</summary>

  - **SVD3 forward precision.** Input scaling and FP32 decomposition produce half-precision factors while preserving public signatures and existing adjoints. Reported CPU/B200 tests cover zero, rank-deficient, repeated-singular-value, and scaled inputs. The forward-only contribution remains draft pending maintainer guidance.

    FP16 SVD3 forward [#2063](https://github.com/NVIDIA/warp/pull/2063 "Fix half-precision SVD3 NaNs (GH-2055)") (Draft)

  - **Zero-adjoint SVD gradients.** A separate proposal bypasses reciprocal singular-value gaps when both U/V adjoints are zero, preserving singular-value gradients and preventing unused SVD diagnostics from contaminating other gradients. CPU and B200 regressions cover repeated singular values and small nonzero seeds. Maintainer guidance remains pending; the general nonzero U/V adjoint formula is unchanged, and downstream impact is unmeasured.

    Zero-adjoint gradient contract [#2064](https://github.com/NVIDIA/warp/pull/2064 "Fix zero-adjoint SVD gradients (GH-2054)") (Open)

  </details>

<sub>Selected public contributions · PR status verified 2026-10-12.</sub>

<!-- OPEN-SOURCE:END -->

[xdit-runtime]: https://github.com/xdit-project/xDiT/pull/836
[fastvideo-inference]: https://github.com/hao-ai-lab/FastVideo/pull/1900
[rl-kernel-rmsnorm]: https://github.com/RL-Align/RL-Kernel/pull/466
[sglang-cache]: https://github.com/sgl-project/sglang/pull/42437
[vllm-error]: https://github.com/vllm-project/vllm-omni/pull/8474
