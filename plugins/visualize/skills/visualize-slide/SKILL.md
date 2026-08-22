---
name: visualize-slide
description: Create a single, self-contained technical presentation slide in a dense Excalidraw-style hand-drawn visual language. Use for visual explanations of mechanisms, architectures, data flows, algorithms, mathematical ideas, or technical narratives. Match the bundled PNG style references and prioritize technical correctness over visual symmetry.
version: 0.2.8
---

# Visualize Slide

Create exactly one self-contained technical presentation slide as an image.

## Style grounding

Before generating the slide, inspect the bundled style references in `assets/`:

- `style-concept-slide.png` — concept/explanation layout
- `style-architecture-slide.png` — architecture/mechanism layout
- `style-dense-slide.png` — dense technical slide layout

Use them as visual ground truth for style and composition, not as factual sources or templates whose content must be copied.

The target visual language is explicitly **Excalidraw-style**:

- white background
- hand-drawn / whiteboard feel
- thin dark outlines
- handwritten-looking headings and labels
- restrained pastel fills
- clear arrows and connectors
- dense but structured composition
- technical diagrams rather than decorative illustrations

## Core contract

- Produce **one image = one slide**. Never turn one requested slide into a collage or multi-slide canvas.
- Default to **16:9** unless the user asks for another aspect ratio.
- Preserve technical correctness, topology, ordering, direction, and causality of the mechanism being explained.
- Every arrow and connector must carry semantic meaning: data flow, control flow, dependency, recurrence, causality, or an explicitly labeled relationship.
- Never add connections merely for balance, symmetry, or decoration.
- Prefer an asymmetric but correct diagram over a neat but false one.
- If the user supplies an existing slide and asks for a localized edit, preserve all unrelated content, layout, labels, and connections.
- Do not silently simplify away the mechanism the user is trying to teach.
- Dense slides are allowed. Organize density locally instead of deleting useful detail.
- Do not add slide numbers unless explicitly requested.

## Information-flow conventions

Use direction deliberately and consistently:

- For stacked architectures, prefer **input at the bottom and output at the top** when that matches the user's deck.
- For recurrence or temporal progression, prefer **left to right**.
- Align inputs, states, and outputs precisely when time steps matter.
- For encoder/decoder diagrams, distinguish internal state propagation from externally consumed outputs.
- When a diagram has multiple layers, do not imply cross-layer dependencies that do not exist.

If the user has already established a flow convention in the visual series, follow it even when another convention would also be valid.

## Color semantics

Do not impose universal domain colors. Instead:

1. Reuse an established color vocabulary from the user's current visual series.
2. Keep a semantic object the same color across related slides.
3. Use color to encode meaning, not decoration.
4. If no palette exists, choose a restrained pastel palette with strong local contrast.

Domain-specific color rules belong to the user's deck, not to this general skill.

## Layout patterns

Choose the layout that best explains the mechanism:

- **Concept slide:** one dominant idea plus 2–4 supporting panels.
- **Mechanism slide:** explicit pipeline or state transition with supporting annotations.
- **Architecture slide:** system/block diagram with a stable legend or color vocabulary.
- **Comparison slide:** two or three aligned alternatives with the same abstraction level.
- **Dense slide:** several tightly organized regions, but still one coherent visual argument.

Prefer a strong visual hierarchy:

- title / thesis at top
- mechanism in the main canvas
- equations adjacent to the mechanism they explain
- concise takeaway at the bottom when useful

## Technical integrity

Before generating, reason through the mechanism and verify:

- What are the inputs and outputs?
- What state is carried or reused?
- Which arrows are true dependencies?
- Which operations happen sequentially versus in parallel?
- Which values are recomputed versus cached?
- Are repeated structures aligned correctly?
- Do equations match the visual data flow?

When there is ambiguity, make the abstraction explicit rather than inventing details.

## Editing existing visuals

For correction requests:

- Change only what the user requested unless the change requires a dependent correction.
- Preserve the established style exactly.
- Preserve aspect ratio, overall composition, and unrelated labels.
- Do not re-layout the whole slide merely because one arrow or color is wrong.
- Re-check all neighboring connections after the edit so a local repair does not break another path.

## Avoid

- decorative arrows without semantics
- arbitrary icons that distract from the mechanism
- repeated content solely to fill space
- prose-heavy slides when a diagram can carry the explanation
- changing factual content while performing a style-only edit
- changing style while performing a factual correction
- numbering sections unless it improves the explanation or the user asks for it
- using the bundled reference images as factual evidence

## Output

Generate the final slide image directly. Keep accompanying prose minimal unless the user asks for explanation or iteration notes.
