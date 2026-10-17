# Blender Optical Path

一个在 Blender 里画光路图的 agent skill。描述好光路布局后，agent 会绘制可编辑光束，摆放元件库里的组件，渲染场景，再在单独的 2D 图层里加标注。最终得到可编辑的 `.blend`、不带文字的渲染图和带标注的 SVG。

常见用途：成像与显微光路、干涉仪、光刻装置。

[English](README.md)

https://github.com/user-attachments/assets/b63bad65-843b-46b2-bf64-ec6e713d0830

![透明玻璃的 Journal Editorial 双波长光路](docs/examples/dual-editorial.webp)

双波长示例组合了 17 个组件、可编辑 Geometry Nodes 光束和独立 SVG 标注。这张预览中的四片透明单透镜使用 OptiCore 生成的网格。默认使用 floating，隐藏镜架和支撑件。

[生成插图](examples/README.md) · [可编辑 SVG](docs/examples/dual-editorial.svg) · [示例脚本](examples/dual_wavelength_interferometer.py)

## 三种呈现模式

论文模板默认使用 `floating`：保留光学元件及必要的光源、探测器外形，隐藏镜架和支撑件。需要展示镜架时选 `compact`；需要原尺寸完整装配时选 `full`。

[双波长示例](examples/dual_wavelength_interferometer.py) 继续提供 `floating` 和 `mechanical` 模式，展示 17 个组件和两个示意波长通道。[带标注的浮动视图](docs/examples/dual-editorial.svg) · [机械视图](docs/examples/mechanical-matte.svg)。

## 默认 Journal Editorial

**Journal Editorial**（`illustrated`，别名 `journal-editorial`）采用组件包的 Cycles 材质、柔和灯光和 Filmic 色彩管理。玻璃通光面保持抛光透明，透镜圆柱侧面使用磨砂玻璃。画面背景不显示地面投影。详见[材质来源](references/style-sources.md#local-component-pack-glass)。

[简单中继光路 SVG](docs/examples/paper-editorial.svg)。紫色表示合束后的光。其他渲染选项见[着色说明](references/shading-presets.md)。

配方与提示词：[着色预设](references/shading-presets.md) · [紧凑构图](references/compact-floating-prompt.md) · [视觉风格](references/visual-style.md)

## 工作流程

1. 描述拓扑、通道含义和目标成图尺寸。
2. 放置元件库组件，按需使用经过检查的 Thorlabs 标准件。
3. 绘制 Geometry Nodes 光束，自由设置各点半径。
4. 应用风格，检查实际渲染的构图。
5. 在单独的 SVG 图层添加可编辑文字。
6. 检查场景结构和最终尺寸下的可读性。

普通论文示意图无需提供光学处方。任务涉及定量设计时，再使用[可选物理计算](references/optional-physics.md)。

## 安装

需要 Blender 5.2 或更高版本，已在 5.2.2 LTS 上测试。pi 用户：

```bash
git clone https://github.com/lychen2/blender-optical-path.git \
  ~/.pi/agent/skills/blender-optical-path
```

执行 `/reload`，再用 `/skill:blender-optical-path` 调用。其他 agent 把整个文件夹复制到对应的 skill 目录，并加载 [`SKILL.md`](SKILL.md)。

示例请求：

> 画一个可编辑的迈克尔逊干涉仪。使用浮动光学元件、透明玻璃、较细的彩色光束、白色背景和高角度斜视相机。标注单独放在 SVG 中：BS、M1、M2 和 Detector。

请写明拓扑、已知尺寸和目标成图尺寸。

## 默认设置

- 标注放在单独的 2D 图层，3D 渲染图里只有几何体，改标注不用重新渲染。
- 论文模板使用较细的可编辑光束，可自由设置各点半径，并在 Geometry Nodes 中通过 **Radius Scale** 调整整体宽度。

## Python 与 MCP

在 Blender 里：

```python
import runpy
api = runpy.run_path('/path/to/blender-optical-path/tools/optics.py')
scene = api['new_workspace']('Optical diagram')
api['place_asset']('assembly/biconvex_lens', (0, 0, 100),
                   scene=scene, at_optical_center=True)
api['add_beam_nodes']([(-100, 0, 100), (100, 0, 100)], scene=scene)
api['apply_style'](scene)  # Journal Editorial
```

坐标单位为毫米。传入一个新的输出目录，即可生成完整论文插图模板：

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python tools/paper_scene.py -- --output /chosen/new-figure
```

输出包括 `figure.blend`、`clean.png`、`annotated.svg` 和 `scene.json`。模板有 `beam-relay`、`polarimetry`、`microscope`。`--presentation compact` 保留镜架并隐藏支柱底座，`floating` 显示光学符号，`full` 保留原尺寸装配。`--style illustrated` 选择 Journal Editorial。选中光束后，可以在 Geometry Nodes 修改器里调节 **Radius Scale**。

`tools/example_scene.py` 保留最小装配示例。论文模板无需输入定量参数。

需要 OptiCore 镜片网格时，向复杂示例传入本地源码目录：

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python examples/dual_wavelength_interferometer.py -- \
  --opticore /path/to/OptiCore --output /chosen/new-dual-figure
```

适配器只在当前 Blender 进程加载 OptiCore，玻璃材质单独赋予。参见[重现命令与源材质选项](examples/README.md#opticore-lenses-and-source-glass)。

连接 Blender MCP 服务器后，`tools/blender_mcp_entry.py` 可以通过 JSON 请求调用同一套 API。详见 [API 与 MCP 参考](references/python-mcp.md)。

## 元件库

`library/Optical_Components.blend` 收录 70 个元件：24 个带支架的装配体、18 个厂商 CAD 零件、28 个示意模块。可以直接打开浏览，也可以通过 API 按 id 放置。元件 id 和来源记录在 `library/index.json` 与 `library/provenance/` 中。

- [手动装配](references/manual.md)
- [支持的光路系统](references/system-coverage.md)
- [从官方 CAD 添加零件](references/thorlabs-workflow.md)

## 自检

```bash
blender -b --factory-startup --python-exit-code 1 \
  --python tools/check_package.py
```

在 Blender 中运行 `tools/check_illustration.py` 检查模板、风格、SVG 和可选功能入口。运行 `tools/check_geometry_nodes.py` 检查可编辑光束几何。运行 `python tools/check_optical_model.py` 检查可选数值计算。

`tools/validate_layout.py` 用于检查已保存的布局。

## 许可

代码和文档采用 [MIT 许可证](LICENSE)。厂商 CAD 沿用其原有条款，见[第三方声明](THIRD_PARTY_NOTICES.md)。
