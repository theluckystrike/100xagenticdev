# ANDREJ KARPATHY: THE DEFINITIVE STUDY

**Compiled:** 2026-05-12 | **Sources:** 50+ primary sources, academic papers, talks, GitHub repos

---

## COMPLETE CAREER TIMELINE

### Early Life
- **Born:** October 23, 1986, Bratislava, Czechoslovakia (now Slovakia)
- Moved to Toronto, Canada at age 15

### University of Toronto (2005-2009)
- B.Sc. in Computer Science and Physics, minor in Mathematics
- First deep learning exposure: Geoffrey Hinton's Neural Nets class (~2007)

### UBC MSc (2009-2011)
- Thesis: "Learning Controllers for Physically-simulated Figures"
- Adviser: Michiel van de Panne
- Focus: ML for agile motor skills in physical simulation

### Stanford PhD (2011-2015)
- Thesis: "Connecting Images and Natural Language"
- Adviser: Fei-Fei Li
- **Created CS231n** — the first deep learning class at Stanford
  - Enrollment: 150 (2015) -> 330 (2016) -> 750 (2017)
  - Became one of Stanford's largest classes ever
  - Free lecture videos: 800K+ views
  - The de facto global entry point for learning deep learning
- **ImageNet "reference human"** — established 5.1% human baseline error rate
  - Had to learn hundreds of dog breeds and flower species by hand
- Key papers:
  - "Deep Visual-Semantic Alignments for Generating Image Descriptions" (CVPR 2015 Oral)
  - "DenseCap: Fully Convolutional Localization Networks" (CVPR 2016 Oral)
  - Co-authored ImageNet LSVRC paper

### OpenAI Founding Member (2015-2017)
- Research scientist from founding
- Generative models and RL research

### Tesla Director of AI (June 2017 - July 2022)
- Senior Director of AI / Director of Autopilot Vision
- Reported directly to Elon Musk
- **Key decisions:**
  - Championed **vision-only** approach: removed radar entirely
  - Built **HydraNet**: shared backbone with multiple prediction heads
  - Full stack: 48 networks, 1,000 predictions, 70,000 GPU hours per compile
  - Built Tesla's **data engine**: automated pipeline for edge case collection -> retraining -> deployment
  - Scaled to 3 GPU clusters, processing 1.5 petabytes from ~1.5M cars (8 cameras each)
- Presented at Tesla AI Day 2021, CVPR 2021
- Departed July 13, 2022

### Return to OpenAI (Feb 2023 - Feb 2024)
- Working on "kind of a J.A.R.V.I.S." — an AI assistant product
- Departed Feb 13, 2024: "Nothing 'happened' and it's not a result of any particular event"

### Eureka Labs & Independent Builder (2024-present)
- **July 2024:** Announced Eureka Labs — "AI Native School"
- **~$20M seed round** (Conviction/Sarah Guo, Sam Altman)
- First product: LLM101n course
- **November 2025:** Still 80% manual coding
- **December 2025:** Flipped to 80% agent-driven — the inflection point
- **March 2026:** Says he hasn't written a single line of code since December
- **May 2026:** Sequoia AI Ascent keynote

---

## GITHUB PROJECTS (github.com/karpathy — 183K followers)

| Repository | Stars | Description |
|---|---|---|
| **autoresearch** | 80,585 | AI agents running ML research experiments autonomously |
| **nanoGPT** | 57,916 | Simplest/fastest repo for training medium-sized GPTs |
| **nanochat** | 53,323 | Full-stack ChatGPT pipeline, $100 on single 8xH100 |
| **LLM101n** | 36,909 | "Let's build a Storyteller" (Eureka Labs course) |
| **llm.c** | 29,873 | LLM training in raw C/CUDA, no PyTorch |
| **minGPT** | 24,350 | Minimal PyTorch GPT implementation |
| **nn-zero-to-hero** | 21,775 | Zero to Hero video series code |
| **llama2.c** | 19,489 | Llama 2 inference in one file of pure C |
| **llm-council** | 18,643 | Multi-LLM deliberation with anonymized peer review |
| **micrograd** | 15,819 | Tiny autograd engine, ~100 lines of Python |
| **char-rnn** | 12,034 | Character-level RNN language models (2015) |
| **convnetjs** | 11,157 | Deep learning entirely in JavaScript |
| **minbpe** | 10,480 | Minimal BPE tokenization implementation |
| **reader3** | 3,610 | Reading books with LLMs |
| **rendergit** | 2,281 | Render git repos into single HTML for LLMs |

**Total public repos:** 63 | **Primary languages:** Python, C/CUDA, JavaScript, Rust

### Standout Projects

**microgpt (Feb 2026):** Single file, 200 lines, zero dependencies. Contains the ENTIRE algorithmic content of an LLM: dataset loader, tokenizer, autograd, GPT-2 architecture, Adam optimizer, training loop, inference. "The culmination of a decade-long obsession to simplify LLMs to their bare essentials."

**autoresearch (Mar 2026):** 630-line script that lets AI autonomously: modify code -> train 5min -> check results -> keep or discard -> repeat. ~12 experiments/hour, ~100 overnight. Initial run: 700 experiments in 2 days, 20 optimizations discovered. Shopify CEO tried it: 37 experiments overnight, 19% performance gain. 80K+ stars.

**nanochat (Oct 2025):** Full-stack ChatGPT: tokenization (Rust BPE) -> pretraining (FineWeb-EDU) -> mid-training -> SFT -> optional GRPO -> inference -> chat UI. Single 8xH100, ~4 hours, ~$100.

---

## KEY IDEAS & FRAMEWORKS

### Software Evolution

| Era | What Humans Do | Unit of Work |
|-----|---------------|-------------|
| **1.0** (2017 essay) | Write explicit code | Functions |
| **2.0** (2017 essay) | Curate datasets for neural networks | Training examples |
| **3.0** (2025 talk) | Write prompts; context window IS the program | Paragraphs |

### "Vibe Coding" (Feb 2, 2025)
> "There's a new kind of coding I call 'vibe coding', where you fully give in to the vibes, embrace exponentials, and forget that the code even exists."

**Impact:** Collins English Dictionary named it **Word of the Year 2025**.

### "Context Engineering" (June 25, 2025)
> "+1 for 'context engineering' over 'prompt engineering'. In every industrial-strength LLM app, context engineering is the delicate art and science of filling the context window with just the right information for the next step."

### The Verifiability Thesis
> "Traditional software automates what you can specify. LLMs automate what you can verify."

AI peaks where training has clear reward signals (code, math, chess). Fails where verification is ambiguous.

### "Jagged Intelligence" (July 2024)
> "State of the art LLMs can both perform extremely impressive tasks while simultaneously struggle with very dumb problems."

LLMs spike near domains where RLVR training occurs. Performance is uneven, not smooth.

### The March of Nines
> "Every single nine is a constant amount of work. A demo that works 90% is just the first nine. Then you need the second nine, third nine..."

From 5 years leading Autopilot: Waymo had perfect demo rides in 2014. Still not fully deployed in 2025.

### The 100x Engineer
> "People who are very good at this can peak much higher than 10x. Vibe coding raises the floor. Agentic engineering is about extrapolating the ceiling."

### Core Philosophy
> "You can outsource your thinking, but you can't outsource your understanding."

> "You are not allowed to introduce vulnerabilities because of vibe coding. You are still responsible for your software."

> "Summoned ghosts, not building animals" — LLMs are statistical distillations of human text, not evolving organisms.

### Predictions
- AGI: ~a decade away (5-10x more pessimistic than peers)
- 2025-2035: "Decade of agents" — partial autonomy, not full
- 2026: the "slopacolypse" — flood of mediocre AI content
- Next infrastructure wave: agent-native, not user-native

---

## INFLUENCE METRICS

| Metric | Value |
|--------|-------|
| X/Twitter followers | ~2.4M |
| GitHub followers | 183K |
| YouTube subscribers | 1M+ |
| YouTube total views | 27.5M+ |
| Google Scholar citations | ~78,000+ |
| CLAUDE.md repo stars | ~117,700+ |
| autoresearch stars | 80,500+ |

---

## KEY TALKS

| Date | Venue | Topic |
|---|---|---|
| 2015-2017 | Stanford CS231n | Primary instructor |
| Nov 2017 | Medium | "Software 2.0" essay |
| Aug 2021 | Tesla AI Day | Autopilot architecture |
| Oct 2022 | Lex Fridman #333 | Tesla AI, AGI (3h34m) |
| May 2023 | Microsoft Build | "State of GPT" |
| Jun 2025 | YC AI Startup School | Software 3.0 |
| Oct 2025 | Dwarkesh Podcast | "AGI is still a decade away" |
| May 2026 | Sequoia AI Ascent | "From Vibe Coding to Agentic Engineering" |

---

## SOURCES

- [Wikipedia](https://en.wikipedia.org/wiki/Andrej_Karpathy) | [karpathy.ai](https://karpathy.ai/) | [GitHub](https://github.com/karpathy)
- [Sequoia Ascent 2026 Blog](https://karpathy.bearblog.dev/sequoia-ascent-2026/)
- [2025 Year in Review](https://karpathy.bearblog.dev/year-in-review-2025/)
- [Animals vs Ghosts](https://karpathy.bearblog.dev/animals-vs-ghosts/)
- [Software 2.0 (Medium)](https://karpathy.medium.com/software-2-0-a64152b37c35)
- [Vibe Coding Tweet](https://x.com/karpathy/status/1886192184808149383)
- [Context Engineering Tweet](https://x.com/karpathy/status/1937902205765607626)
- [LLM Wiki Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [Dwarkesh Podcast](https://www.dwarkesh.com/p/andrej-karpathy)
- [Karpathy-skills CLAUDE.md](https://github.com/forrestchang/andrej-karpathy-skills)
- [Google Scholar](https://scholar.google.com/citations?user=l8WuQJgAAAAJ)
