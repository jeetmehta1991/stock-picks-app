---
name: llm-council
description: "Use when a decision is expensive to get wrong and there is genuine uncertainty - pricing, positioning, pivots, architecture bets, scope calls, 'am I crazy for doing X', or reviewing work where one perspective might miss the fatal flaw. Also use when Jeet says \"council this\", \"council it\", \"run the council\", \"convene the council\", \"LLM council\", or \"get me five perspectives\". Runs the question through 5 independent advisors (Contrarian, First Principles, Expansionist, Outsider, Executor), has them peer-review each other anonymously, then a chairman synthesizes agreement, clashes, blind spots, a real recommendation, and one first step. Do NOT use for factual lookups, creation tasks, or summarization."
---

# LLM Council

You ask one AI a question, you get one answer. That answer might be great. It might be mid. You have no way to tell because you only saw one perspective.

The council fixes this. It runs your question through 5 independent advisors, each thinking from a fundamentally different angle. Their answers are then cross-evaluated anonymously, and a chairman synthesis pulls everything into a final recommendation that tells you where the advisors agree, where they clash, and what you should actually do.

This is adapted from Andrej Karpathy's LLM Council. He dispatches queries to multiple models, has them peer-review each other anonymously, then a chairman produces the final answer. We do the same thing inside Claude using sub-agents with different thinking lenses instead of different models - with one deliberate departure: **only the five advisors are spawned.** The anonymized review and the chairman synthesis run inline, because independence is what the ADVISORS need, while review and synthesis are judgment over material already in hand.

## When to run the council

The council is for questions where being wrong is expensive.

**Good council questions:**

- "Should I launch a $97 workshop or a $497 course?"
- "Which of these 3 positioning angles is strongest?"
- "I'm thinking of pivoting from X to Y. Am I crazy?"
- "Here's my landing page copy. What's weak?"
- "Should I hire a VA or build an automation first?"

**Bad council questions:**

- "What's the capital of France?" (one right answer, no need for perspectives)
- "Write me a tweet" (creation task, not a decision)
- "Summarize this article" (processing task, not judgment)

The council shines when there's genuine uncertainty and the cost of a bad call is high. If you already know the answer and just want validation, the council will likely tell you things you don't want to hear. That's the point.

## The five advisors

Each advisor thinks from a different angle. They're not job titles or personas. They're thinking styles that naturally create tension with each other.

### 1. The Contrarian

Actively looks for what's wrong, what's missing, what will fail. Assumes the idea has a fatal flaw and tries to find it. If everything looks solid, digs deeper. The Contrarian is not a pessimist. They're the friend who saves you from a bad deal by asking the questions you're avoiding.

### 2. The First Principles Thinker

Ignores the surface-level question and asks "what are we actually trying to solve here?" Strips away assumptions. Rebuilds the problem from the ground up. Sometimes the most valuable council output is the First Principles Thinker saying "you're asking the wrong question entirely."

### 3. The Expansionist

Looks for upside everyone else is missing. What could be bigger? What adjacent opportunity is hiding? What's being undervalued? The Expansionist doesn't care about risk (that's the Contrarian's job). They care about what happens if this works even better than expected.

### 4. The Outsider

Has zero context about you, your field, or your history. Responds purely to what's in front of them. This is the most underrated advisor. Experts develop blind spots. The Outsider catches the curse of knowledge: things that are obvious to you but confusing to everyone else.

### 5. The Executor

Only cares about one thing: can this actually be done, and what's the fastest path to doing it? Ignores theory, strategy, and big-picture thinking. The Executor looks at every idea through the lens of "OK but what do you do Monday morning?" If an idea sounds brilliant but has no clear first step, the Executor will say so.

**Why these five:** They create three natural tensions. Contrarian vs Expansionist (downside vs upside). First Principles vs Executor (rethink everything vs just do it). The Outsider sits in the middle keeping everyone honest by seeing what fresh eyes see.

## How a council session works

### Step 1: Frame the question (with context enrichment)

When the user says "council this" (or any trigger phrase), do two things before framing:

**A. Scan the workspace for context.** The user's question is often just the tip of the iceberg. Their Claude setup likely contains files that would dramatically improve the council's output. Before framing, quickly scan for and read any relevant context files:

- `CLAUDE.md` or `claude.md` in the project root or workspace (business context, preferences, constraints)
- Any `memory/` folder (audience profiles, voice docs, business details, past decisions)
- Any files the user explicitly referenced or attached
- Recent council transcripts in this folder (to avoid re-counciling the same ground)
- Any other context files that seem relevant to the specific question (e.g., if they're asking about pricing, look for revenue data, past launch results, audience research)

Use Glob and quick Read calls to find these. Don't spend more than 30 seconds on this. You're looking for the 2-3 files that would give advisors the context they need to give specific, grounded advice instead of generic takes.

**B. Frame the question.** Take the user's raw question AND the enriched context and reframe it as a clear, neutral prompt that all five advisors will receive. The framed question should include:

- The core decision or question
- Key context from the user's message
- Key context from workspace files (business stage, audience, constraints, past results, relevant numbers)
- What's at stake (why this decision matters)

Don't add your own opinion. Don't steer it. But DO make sure each advisor has enough context to give a specific, grounded answer rather than generic advice.

If the question is too vague ("council this: my business"), ask one clarifying question. Just one. Then proceed.

Save the framed question for the transcript.

### Step 2: Convene the council (5 sub-agents in parallel - the only spawns)

Spawn all 5 advisors simultaneously as sub-agents. Each gets:

- Their advisor identity and thinking style (from the descriptions above)
- The framed question
- A clear instruction: respond independently. Do not hedge. Do not try to be balanced. Lean fully into your assigned perspective. If you see a fatal flaw, say it. If you see massive upside, say it. Your job is to represent your angle as strongly as possible. The synthesis comes later.

Each advisor should produce a response of 150-300 words. Long enough to be substantive, short enough to be scannable.

**Sub-agent prompt template:**

```
You are [Advisor Name] on an LLM Council.

Your thinking style: [advisor description from above]

A user has brought this question to the council:

---
[framed question]
---

Respond from your perspective. Be direct and specific. Don't hedge or try to be balanced. Lean fully into your assigned angle. The other advisors will cover the angles you're not covering.

Keep your response between 150-300 words. No preamble. Go straight into your analysis.
```

### Step 3: Peer review (inline, anonymized)

This is the step that makes the council more than just "ask 5 times." It's the core of Karpathy's insight.

Collect all 5 advisor responses. Anonymize them as Response A through E (randomize which advisor maps to which letter so there's no positional bias).

**Do this INLINE in the main thread - do not spawn reviewer sub-agents.** Working from the 5
anonymized responses, answer the three questions below yourself, once, across the whole set.

**Fidelity note, stated honestly:** Karpathy's original has each advisor review the others
independently, which surfaces disagreement *about the reviews themselves*. One inline pass loses
that. What it keeps is the mechanism that matters most - **anonymized cross-evaluation**, so a
response is judged on merit rather than on which lens produced it. Read all five before writing
anything, so the first response does not anchor the rest.

The three questions:

1. Which response is the strongest and why? (pick one)
2. Which response has the biggest blind spot and what is it?
3. What did ALL responses miss that the council should consider?

**Reviewer framing (apply to yourself, inline):**

```
Review the outputs of the council. Five advisors independently answered this question:

---
[framed question]
---

Here are their anonymized responses:

**Response A:**
[response]

**Response B:**
[response]

**Response C:**
[response]

**Response D:**
[response]

**Response E:**
[response]

Answer these three questions. Be specific. Reference responses by letter.

1. Which response is the strongest? Why?
2. Which response has the biggest blind spot? What is it missing?
3. What did ALL five responses miss that the council should consider?

Keep your review under 200 words. Be direct.
```

### Step 4: Chairman synthesis (inline)

**Also INLINE - do not spawn a chairman sub-agent.** You now hold everything: the original
question, all 5 advisor responses (de-anonymized, so you can see which advisor said what), and
the peer-review pass.

The chairman's job is to produce the final council output. It follows this structure:

**COUNCIL VERDICT**

- **Where the council agrees** — the points that multiple advisors converged on independently. These are high-confidence signals.
- **Where the council clashes** — the genuine disagreements. Don't smooth these over. Present both sides and explain why reasonable advisors disagree.
- **Blind spots the council caught** — things that only emerged through the peer review round. Things individual advisors missed that other advisors flagged.
- **The recommendation** — a clear, actionable recommendation. Not "it depends." Not "consider both sides." A real answer. The chairman can disagree with the majority if the reasoning supports it.
- **The one thing you should do first** — a single concrete next step. Not a list of 10 things. One thing.

**Chairman framing (apply to yourself, inline):**

```
Act as Chairman. Synthesize the work of 5 advisors and their peer reviews into a final verdict.

The question brought to the council:
---
[framed question]
---

ADVISOR RESPONSES:

**The Contrarian:**
[response]

**The First Principles Thinker:**
[response]

**The Expansionist:**
[response]

**The Outsider:**
[response]

**The Executor:**
[response]

PEER REVIEWS:
[all 5 peer reviews]

Produce the council verdict using this exact structure:

## Where the Council Agrees
[Points multiple advisors converged on independently. These are high-confidence signals.]

## Where the Council Clashes
[Genuine disagreements. Present both sides. Explain why reasonable advisors disagree.]

## Blind Spots the Council Caught
[Things that only emerged through peer review. Things individual advisors missed that others flagged.]

## The Recommendation
[A clear, direct recommendation. Not "it depends." A real answer with reasoning.]

## The One Thing to Do First
[A single concrete next step. Not a list. One thing.]

Be direct. Don't hedge. The whole point of the council is to give the user clarity they couldn't get from a single perspective.
```

### Step 5: Present the verdict in chat

After the chairman synthesis is complete, present the full verdict directly in chat using markdown. Do NOT generate an HTML report or any files. The user reads it in the conversation.

Format the output as:

```
## Council Verdict: {short topic}

### Where the Council Agrees
{content}

### Where the Council Clashes
{content}

### Blind Spots the Council Caught
{content}

### The Recommendation
{content}

### The One Thing to Do First
{content}
```

Keep it scannable. Use bullet points. Include the before/after examples where relevant.

### Step 6: Save the transcript (optional)

Only save a transcript if the user asks for it or if the question is significant enough to reference later. If saving, write to `council-transcript-[timestamp].md` in the project's `active/` directory.

## Example: counciling a product decision

**User:** "Council this: I'm thinking of building a $297 course on Claude Code for beginners. My audience is mostly non-technical solopreneurs. Is this the right move?"

**The Contrarian:** "The market is flooded with Claude courses right now. At $297, you're competing with free YouTube content. Your audience is non-technical, which means high support burden and refund risk. The people who would pay $297 are likely already past beginner level..."

**The First Principles Thinker:** "What are you actually trying to achieve? If it's revenue, a course is one of the slowest paths. If it's authority, a free resource might do more. If it's building a customer base for higher-ticket offers, the price point and audience might be mismatched..."

**The Expansionist:** "Beginner Claude for solopreneurs is a massive underserved market. Everyone's teaching advanced stuff. If you nail the beginner angle, you own the entry point to this entire space. The $297 might be low. What if this became a $997 program with community access..."

**The Outsider:** "I don't know what Claude Code is. If I saw '$297 course on Claude Code for beginners,' I wouldn't know if this is for me. The name means nothing to someone outside your world. Your landing page needs to sell the outcome, not the tool..."

**The Executor:** "A full course takes 4-8 weeks to produce properly. Before building anything, run a live workshop at $97 to 50 people. You validate demand, generate testimonials, and create the raw material for the course. If 50 people don't buy the workshop, 500 won't buy the course..."

**Chairman's Verdict:**

- **Where the council agrees:** The beginner solopreneur angle has real demand, but the current framing (Claude Code course) is too tool-specific and won't resonate with non-technical buyers.
- **Where the council clashes:** Price. The Contrarian says $297 is too high given competition. The Expansionist says it's too low for the value. The resolution likely depends on how much support and community access is bundled.
- **Blind spots caught:** The Outsider's point that "Claude Code" means nothing to the target buyer is the single most important insight. Every advisor except the Outsider assumed the audience already knows what this is.
- **Recommendation:** Don't build the course yet. Validate with a lower-commitment offer first. But reframe entirely: sell the outcome (automate your business, get 10 hours back per week), not the tool.
- **One thing to do first:** Run a $97 live workshop called "How to automate your first business task with AI" to 50 people. Don't mention Claude Code in the title.

## Important notes

- **Spawn exactly 5 sub-agents - the advisors - and spawn them in parallel.** Sequential spawning
  wastes time and lets earlier responses bleed into later ones. **The advisors are the only
  sub-agents this skill spawns.** Peer review (Step 3) and chairman synthesis (Step 4) run inline
  in the main thread, because independence is what the ADVISORS need - review and synthesis are
  judgment over material already in hand, and spawning eleven agents for one decision is
  disproportionate.
- **Always anonymize for peer review.** If reviewers know which advisor said what, they'll defer to certain thinking styles instead of evaluating on merit.
- **The chairman can disagree with the majority.** If 4 out of 5 advisors say "do it" but the reasoning of the 1 dissenter is strongest, the chairman should side with the dissenter and explain why.
- **Don't council trivial questions.** If the user asks something with one right answer, just answer it. The council is for genuine uncertainty where multiple perspectives add value.
- **Output goes in chat, not to a file.** Step 5 is authoritative: present the verdict as markdown in the conversation. Do not generate an HTML report. (The source material this skill was adapted from carried a leftover line about an HTML report mattering; that is superseded by Step 5.)

## Relationship to the repo's existing council pattern

This project already documents a 4-lens council in `docs/r6_workflow_reuse/COUNCIL_PATTERN_GUIDE.md` — Contrarian, Executor, First Principles, Outsider — used for batch/engineering decisions, with a hard anti-pattern rule: *"A council that doesn't have a Contrarian lens isn't a council."*

This skill is a superset: the same four lenses plus **The Expansionist**, and it adds the two mechanisms the repo guide lacks — **anonymized peer review** and a **chairman synthesis**. Use this skill when the decision is expensive and genuinely uncertain. The repo guide's lighter inline format remains fine for routine per-turn batch councils where spawning ten sub-agents is disproportionate.
