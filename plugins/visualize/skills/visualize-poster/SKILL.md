---
name: visualize-poster
description: Create an extremely dense technical poster in a structured Excalidraw-style hand-drawn visual language. Use for one-page system maps, architecture posters, deep technical overviews, request/data/control-path explainers, and visual cheat sheets where preserving detail matters more than minimalism. Match the bundled PNG style reference.
version: 0.2.9
---

# Visualize Poster

Create exactly one large, coherent technical poster as an image.

## Style grounding

Before generating the poster, inspect `assets/style-dense-poster.png`.

Use it as visual ground truth for style and information density, not as a factual source or content template.

The target visual language is explicitly **Excalidraw-style**:

- white background
- hand-drawn / whiteboard aesthetic
- thin dark outlines
- handwritten-looking labels
- restrained pastel fills
- dense local grouping
- explicit arrows and paths
- many details without losing structure

## Poster contract

- Produce **one coherent poster**, never a collage of unrelated images.
- The poster may be extremely dense. Do not simplify merely because there are many concepts.
- Preserve as much useful technical detail as possible by organizing it into coherent regions.
- Every arrow and connector must represent real data flow, control flow, dependency, lifecycle, state movement, ownership, or another explicitly labeled semantic relationship.
- Preserve the actual topology, ordering, and direction of the system.
- Prefer correctness over symmetry.
- If the user provides an existing poster, reuse its established visual vocabulary and hierarchy.

## Structure

A strong poster often combines several levels of explanation on one canvas:

- big-picture architecture
- component responsibilities
- request journey / lifecycle
- data path
- control path
- state / memory placement
- hardware or runtime layer
- important equations or invariants
- legends and terminology
- trade-offs / failure modes / misconceptions
- compact bottom or side summary

Not every poster needs every region. Include only regions that help explain the system.

## Density without chaos

Maintain high information density through structure, not by shrinking everything indiscriminately:

- divide the poster into named regions
- keep local diagrams simple
- use repeated visual grammar for repeated mechanisms
- reserve strong colors for semantic categories
- use legends where they reduce repetition
- visually trace important end-to-end paths
- keep related equations beside the mechanism they govern
- use whitespace as separation between regions, not as an excuse to omit detail

## Flow conventions

Use direction consistently:

- stacked architecture: prefer bottom-to-top when consistent with the user's series
- time / recurrence: left-to-right
- request journeys: choose one dominant direction and preserve it
- clearly distinguish data plane, control plane, state movement, and observation paths when relevant

Never add a path just because a region otherwise looks disconnected.

## Color semantics

- Reuse the user's established color vocabulary when one exists.
- Keep semantic categories stable across the entire poster.
- Do not impose domain-specific colors globally.
- If starting fresh, use a restrained pastel palette and a small legend.

## Technical integrity pass

Before generating, verify:

- all components and boundaries are correctly named
- every connector has a real meaning
- arrows point in the correct direction
- replicated or cached state is shown where it actually lives
- sequential and parallel work are visually distinguishable
- repeated layers/stages are represented consistently
- equations match the data paths
- examples do not contradict the architecture

For uncertain details, label them as conceptual or omit them rather than inventing precision.

## Avoid

- decorative network spaghetti
- collage-like grids of disconnected mini-posters
- redundant arrows
- factual claims inferred only from visual symmetry
- removing detail merely to make the poster look cleaner
- mixing abstraction levels without labels
- silently changing content while applying a style edit
- using the bundled reference PNG as factual evidence

## Output

Generate the final poster image directly. Keep accompanying prose minimal unless the user asks for explanation or iteration notes.
