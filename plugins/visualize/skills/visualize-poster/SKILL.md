---
name: visualize-poster
description: Create a large, detailed technical poster in the hand-drawn style of visualize-slide. Use for multi-topic explanations, system maps, worked mechanisms, and visual reference sheets.
version: 0.2.11
---

# Visualize Poster

Create one coherent raster poster. Use the larger canvas to explain several related topics in depth, with one question or system tying them together. Choose the aspect ratio to fit the subject and its reading path.

## Ground the design in both sets of examples

Before composing the poster, read the [slide guide](../visualize-slide/SKILL.md) and inspect all three slide examples. Inherit their typography, line work, restrained colors, local diagrams, and use of explanatory text. Apply their layout patterns within individual regions of the poster.

- [Concept](../visualize-slide/assets/style-concept-slide.png) follows the same concrete example through successive representations. Each caption explains what the reader can infer from the drawing above it.
- [Architecture](../visualize-slide/assets/style-architecture-slide.png) pairs an overview with local diagrams. The two mechanisms use the same inputs and positions, so the connections reveal what each operation does.
- [Dense explanation](../visualize-slide/assets/style-dense-slide.png) aligns successive states. The reader can see which values change, which survive, and why.

Then inspect the [poster example](assets/style-dense-poster.png) for overall composition, information density, and reading paths. Notice how the side column traces one request across the larger system, while the local diagrams preserve their implementation details. Use these images as design references. Source the technical content from the user's material.

## Compose the whole poster

Give the reader an entry point and an overview that locates the related topics. Organize each region around a question the reader can answer by inspecting it. A timeline, a system boundary, a shared example, or a set of independent axes can provide the organizing structure. Show independent choices as peers and sequential operations in order.

Use the extra space for worked examples, intermediate states, equations, and implementation details. Where it helps, trace one concrete case end to end. Reuse the overview's names and colors so readers can locate each step. Connect regions only when the line represents a specific relationship.

## Teach each topic at slide scale

Choose the local visual to suit the question. For a comparison, align the same inputs and show the different outputs. For a transition, put the two states side by side and mark the values that change. For an architecture, place the detail beside the component it explains.

Use text where it does explanatory work. Name the operation on the arrow, put the equation beside the transformation, and give the reader a short sentence explaining why the result follows. For code, keep the definition, a concrete call, and its value or type together. Carry a useful example into the next region when the relationship matters there too.

## Verify and render

Trace the worked example through the proposed layout. Check the direction and meaning of each connector, the order of operations, and the agreement between labels, formulas, code, and intermediate results. For revisions, preserve established visual conventions and unrelated content.

Generate the final raster image directly with image generation. Never use SVG, including for drafts, intermediate rendering, or final output. Inspect the actual image at overview size for reading order and at full size for legibility and accuracy, especially code, mathematical symbols, and arrow endpoints. Keep accompanying prose brief.
