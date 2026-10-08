"""Distinct art direction; reference conditioning preserves the child's features."""

STYLES = {
    "Watercolor": "children's watercolor picture-book painting, transparent pigment washes, textured cotton paper, soft wet edges, restrained pastel palette, simple natural child proportions",
    "Paper collage": "hand-cut paper children's illustration, layered coloured paper shapes, visible paper fibres, soft cast shadows, tactile cutout edges, playful simple shapes",
    "Colored pencil": "hand-drawn children's picture book, coloured pencil strokes on cream paper, cross-hatched shading, warm subtle colours, carefully drawn natural face proportions",
    "Storybook 3D": "stylized three-dimensional storybook diorama, handcrafted clay and felt materials, rounded forms, miniature set, soft global illumination, natural child face proportions",
    "Classic ink": "classic illustrated children's book, fine pen-and-ink contours, delicate cross-hatching, translucent wash colours, warm ivory paper, expressive natural faces",
    "Classic Animation": "traditional hand-drawn two-dimensional fairytale animation, graceful curved silhouettes, expressive hand-drawn face, clean ink contours, painted storybook scenery, luminous jewel colours, warm theatrical lighting, original child hero",
    "3D Animation": "cinematic three-dimensional family animation, appealing rounded original child character, expressive facial acting, sculpted hair, tactile clothing, soft subsurface lighting, richly rendered environment, warm depth of field",
    "Disney": "traditional hand-drawn two-dimensional fairytale animation, graceful curved silhouettes, expressive hand-drawn face, clean ink contours, painted storybook scenery, luminous jewel colours, warm theatrical lighting, original child hero",
    "Pixar": "cinematic three-dimensional family animation, appealing rounded original child character, expressive facial acting, sculpted hair, tactile clothing, soft subsurface lighting, richly rendered environment, warm depth of field",
    "Anime": "gentle Japanese anime storybook, clean two-dimensional line art, soft cel shading, hand-painted nature backgrounds, warm slice-of-life atmosphere, preserve the reference child's actual face proportions",
    "Manga": "child-friendly manga illustration, expressive fine ink contours, delicate screen tones, selective soft colour, clear scene staging, preserve reference facial features, no lettering or speech bubbles",
    "Ukiyo-e": "child-friendly Japanese woodblock illustration, flowing carved outlines, flat layered indigo and warm ochre inks, patterned nature, handmade paper grain, stylized but recognizable child features",
}

NEGATIVES = {
    "Classic Animation": "3d render, clay, plastic, photorealism, anime, manga",
    "3D Animation": "flat cel shading, manga, anime, pencil sketch, watercolour wash",
    "Disney": "3d render, clay, plastic, photorealism, anime, manga",
    "Pixar": "flat cel shading, manga, anime, pencil sketch, watercolour wash",
    "Storybook 3D": "flat cel shading, photorealistic portrait, anime, glossy plastic",
    "Watercolor": "3d render, hard cel shading, glossy plastic, photograph",
    "Paper collage": "photograph, 3d plastic render, oil painting",
    "Colored pencil": "3d render, glossy plastic, photograph",
    "Classic ink": "3d render, glossy plastic, photograph",
    "Anime": "3d render, photorealism, caricature",
    "Manga": "3d render, photorealism, speech bubbles, lettering",
    "Ukiyo-e": "3d render, photograph, glossy plastic",
}
