---
name: llm-council
description: "Run a high-stakes question, idea, or decision through a council of 5 AI advisors who analyze it from different angles, peer-review each other anonymously, and synthesize a final verdict. Based on Karpathy's LLM Council. MANDATORY TRIGGERS — always use when the user says 'council this', 'run the council', 'war room this', 'pressure-test this', 'stress-test this', or 'debate this'. STRONG TRIGGERS — use when paired with a real tradeoff: 'should I X or Y', 'which option', 'is this the right move', 'validate this', 'get multiple perspectives', 'I can't decide', 'I'm torn between'. DO trigger when the user presents a genuine decision with stakes and multiple options. Do NOT trigger on simple yes/no questions, factual lookups, or casual 'should I' without a meaningful tradeoff. Skip for trivial questions, pure creation tasks ('write me a tweet'), and pure processing tasks ('summarize this article')."
---

# LLM Council

You ask one AI a question, you get one answer. That answer might be great. It might be mid. You have no way to tell because you only saw one perspective.

The council fixes this. It runs the user's question through 5 independent advisors, each thinking from a fundamentally different angle. Then they review each other's work. Then a chairman synthesizes everything into a final recommendation that tells the user where the advisors agree, where they clash, and what they should actually do.

Adapted from Andrej Karpathy's LLM Council, which dispatches queries to multiple models, has them peer-review each other anonymously, and produces a synthesized final answer. We do the same thing with sub-agents (or sequential roleplay) using different *thinking lenses* instead of different models.

---

## When to run the council

The council is for questions where being wrong is expensive.

**Good council questions:**
- "Should I launch a $97 workshop or a $497 course?"
- "Which of these 3 positioning angles is strongest?"
- "I'm thinking of pivoting from X to Y. Am I crazy?"
- "Here's my landing page copy. What's weak?"
- "Should I hire a VA or build an automation first?"

**Bad council questions:**
- "What's the capital of France?" (one right answer)
- "Write me a tweet" (creation, not a decision)
- "Summarize this article" (processing, not judgment)

The council shines when there's genuine uncertainty and the cost of a bad call is high. If the user already knows the answer and just wants validation, the council will likely tell them things they don't want to hear. That's the point.

---

## The five advisors

Each advisor thinks from a different angle. They're not job titles or personas — they're thinking styles that naturally create tension with each other.

### 1. The Contrarian
Actively looks for what's wrong, what's missing, what will fail. Assumes the idea has a fatal flaw and tries to find it. Not a pessimist — the friend who saves you from a bad deal by asking the questions you're avoiding.

### 2. The First Principles Thinker
Ignores the surface-level question and asks "what are we actually trying to solve?" Strips away assumptions. Rebuilds the problem from the ground up. Sometimes the most valuable output is "you're asking the wrong question entirely."

### 3. The Expansionist
Looks for upside everyone else is missing. What could be bigger? What adjacent opportunity is hiding? What's being undervalued? Doesn't care about risk (that's the Contrarian's job) — cares about what happens if this works *better* than expected.

### 4. The Outsider
Has zero context about the user, their field, or their history. Responds purely to what's in front of them. The most underrated advisor: experts develop blind spots, and the Outsider catches the curse of knowledge — things obvious to the user but confusing to everyone else.

### 5. The Executor
Only cares whether this can actually be done and what the fastest path is. Ignores theory, strategy, and big-picture thinking. Looks at every idea through "OK but what do you do Monday morning?" If an idea sounds brilliant but has no clear first step, the Executor will say so.

**Why these five:** They create three natural tensions. Contrarian vs Expansionist (downside vs upside). First Principles vs Executor (rethink everything vs just do it). The Outsider sits in the middle keeping everyone honest by seeing what fresh eyes see.

---

## How a council session works

There are six steps. The mechanics differ slightly between Claude Code (sub-agents available) and Claude.ai (no sub-agents). Both modes are described — pick the one that matches the environment. See the [Execution mode](#execution-mode-claude-code-vs-claudeai) section for details.

### Step 1: Frame the question (with context enrichment)

When the user invokes the council, do two things before framing.

**A. Scan the workspace for context.** The user's question is often just the tip of the iceberg. Their workspace likely contains files that would dramatically improve the council's output. Quickly scan for and read any relevant context files:

- `CLAUDE.md` or `claude.md` in the project root or workspace (business context, preferences, constraints)
- Any `memory/` folder (audience profiles, voice docs, business details, past decisions)
- Any files the user explicitly referenced or attached
- Recent council transcripts in this folder (to avoid re-counciling the same ground)
- Anything else that seems relevant to the specific question (e.g., for a pricing question, look for revenue data, past launch results, audience research)

In Claude Code, use `Glob` and quick `Read` calls. In Claude.ai, check uploaded files and any project knowledge. Don't spend more than 30 seconds — look for the 2-3 files that give advisors enough context to give *specific, grounded advice* instead of generic takes.

**B. Frame the question.** Take the user's raw question PLUS the enriched context and reframe it as a clear, neutral prompt that all five advisors will receive. The framed question should include:

1. The core decision or question
2. Key context from the user's message
3. Key context from workspace files (business stage, audience, constraints, past results, relevant numbers)
4. What's at stake (why this decision matters)

Don't add personal opinion. Don't steer the question. But DO make sure each advisor has enough context to give a specific, grounded answer rather than generic advice.

If the question is too vague ("council this: my business"), ask one clarifying question. Just one. Then proceed.

Save the framed question — it's reused in every later step and goes in the transcript.

### Step 2: Convene the council (5 advisors)

Each advisor receives:
1. Their advisor identity and thinking style (from above)
2. The framed question
3. A clear instruction: respond independently, don't hedge, don't try to be balanced, lean fully into the assigned angle

Each response should be 150-300 words. Long enough to be substantive, short enough to be scannable.

**Advisor prompt template:**

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

In **Claude Code**: spawn all 5 sub-agents in parallel using the Task tool. Parallel is important — sequential lets earlier responses bleed into later ones.

In **Claude.ai**: run all 5 in sequence within one turn. To prevent earlier advisors from coloring later ones, write each response in full before starting the next, and explicitly re-anchor on the new advisor's identity at the start of each section. Treat each as a clean slate.

### Step 3: Peer review

This is the step that makes the council more than "ask 5 times." It's the core of Karpathy's insight.

Collect all 5 advisor responses. **Anonymize them as Response A through E**, randomizing which advisor maps to which letter so there's no positional bias. (Save the mapping privately — it goes in the transcript later.)

Each reviewer sees all 5 anonymized responses and answers three questions:

1. Which response is the strongest and why? (pick one)
2. Which response has the biggest blind spot, and what is it?
3. What did ALL responses miss that the council should consider?

**Reviewer prompt template:**

```
You are reviewing the outputs of an LLM Council. Five advisors independently answered this question:

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

In **Claude Code**: spawn 5 reviewer sub-agents in parallel. Each reviewer is independent.

In **Claude.ai**: produce 5 reviews in sequence within one turn. As with advisors, re-anchor on each reviewer's blank-slate independence at the start of each review.

### Step 4: Chairman synthesis

One agent (or one synthesis pass in Claude.ai) gets everything: the original question, all 5 advisor responses (now de-anonymized so the chairman can see who said what), and all 5 peer reviews.

The chairman produces the final council output using this exact structure:

```
## Where the Council Agrees
[Points multiple advisors converged on independently. High-confidence signals.]

## Where the Council Clashes
[Genuine disagreements. Present both sides. Explain why reasonable advisors disagree.]

## Blind Spots the Council Caught
[Things that only emerged through peer review. Things individual advisors missed that others flagged.]

## The Recommendation
[A clear, direct recommendation. Not "it depends." A real answer with reasoning. The chairman can disagree with the majority if the reasoning supports it.]

## The One Thing to Do First
[A single concrete next step. Not a list. One thing.]
```

**Chairman prompt template:**

```
You are the Chairman of an LLM Council. Synthesize the work of 5 advisors and their peer reviews into a final verdict.

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
## Where the Council Clashes
## Blind Spots the Council Caught
## The Recommendation
## The One Thing to Do First

Be direct. Don't hedge. The whole point of the council is to give the user clarity they couldn't get from a single perspective.
```

### Step 5: Generate the council report

Generate a visual HTML report and save it to the user's workspace.

**File:** `council-report-[timestamp].html`

Single self-contained HTML file with inline CSS. The report should contain:

1. **The question** at the top
2. **The chairman's verdict** prominently displayed (this is what most people will read)
3. **An agreement/disagreement visual** — a simple grid, spectrum, or breakdown showing which advisors aligned and which diverged. Clean and scannable.
4. **Collapsible sections** for each advisor's full response (collapsed by default)
5. **Collapsible section** for the peer review highlights
6. **A footer** with the timestamp and the question that was counciled

Styling: white background, subtle borders, system font stack, soft accent colors to distinguish advisor sections. Nothing flashy — should look like a professional briefing document.

In **Claude Code**: write the HTML file directly to the workspace and (if the user is at a desktop) open it.

In **Claude.ai**: render the HTML report as an Artifact instead of writing a file. Same content, same structure — Artifacts are the native equivalent of "open the file so the user can see it."

### Step 6: Save the full transcript

Save the complete council transcript as `council-transcript-[timestamp].md` (in Claude Code) or as a second Artifact / a markdown response (in Claude.ai). The transcript includes:

- The original question
- The framed question
- All 5 advisor responses
- All 5 peer reviews (with the anonymization mapping revealed)
- The chairman's full synthesis

The transcript is the artifact of record. If the user wants to re-run the council on the same question after changes, the previous transcript lets them (or a future agent) see how the thinking evolved.

---

## Output format

Every council session produces two outputs:

```
council-report-[timestamp].html    # visual report for scanning
council-transcript-[timestamp].md  # full transcript for reference
```

The user reads the HTML report. The transcript is there for when they want to dig deeper or reference specific advisor arguments later.

---

## Execution mode: Claude Code vs Claude.ai

The council methodology is the same either way; the mechanics differ.

**Claude Code (preferred)**
- Sub-agents available → spawn 5 advisors in parallel (Step 2), 5 reviewers in parallel (Step 3), 1 chairman (Step 4).
- Use `Glob` and `Read` for context enrichment.
- Write the HTML report and markdown transcript as files in the workspace.

**Claude.ai (no sub-agents)**
- Run all 5 advisors in sequence within a single turn — write each in full, then move on. Re-anchor on each advisor's independent perspective at the start of each section.
- Run all 5 reviews in sequence the same way.
- Run the chairman synthesis as a final pass.
- Render the HTML report as an Artifact (HTML mode). The transcript can be a second Artifact (Markdown) or just inlined in the response.
- Skip the "open the file" step — Artifacts render automatically.

The output structure (advisor responses → anonymized peer reviews → chairman synthesis with the 5-section verdict → report + transcript) is identical in both modes. Only the parallelism and file-vs-Artifact rendering differ.

---

## Example: counciling a product decision

**User:** "Council this: I'm thinking of building a $297 course on Claude Code for beginners. My audience is mostly non-technical solopreneurs. Is this the right move?"

**The Contrarian:** "The market is flooded with Claude courses right now. At $297, you're competing with free YouTube content. Your audience is non-technical, which means high support burden and refund risk. The people who would pay $297 are likely already past beginner level..."

**The First Principles Thinker:** "What are you actually trying to achieve? If it's revenue, a course is one of the slowest paths. If it's authority, a free resource might do more. If it's building a customer base for higher-ticket offers, the price point and audience might be mismatched..."

**The Expansionist:** "Beginner Claude for solopreneurs is a massive underserved market. Everyone's teaching advanced stuff. If you nail the beginner angle, you own the entry point to this entire space. The $297 might be low. What if this became a $997 program with community access..."

**The Outsider:** "I don't know what Claude Code is. If I saw '$297 course on Claude Code for beginners,' I wouldn't know if this is for me. The name means nothing to someone outside your world. Your landing page needs to sell the outcome, not the tool..."

**The Executor:** "A full course takes 4-8 weeks to produce properly. Before building anything, run a live workshop at $97 to 50 people. You validate demand, generate testimonials, and create the raw material for the course. If 50 people don't buy the workshop, 500 won't buy the course..."

**Chairman's Verdict:**

*Where the council agrees:* The beginner solopreneur angle has real demand, but the current framing (Claude Code course) is too tool-specific and won't resonate with non-technical buyers.

*Where the council clashes:* Price. The Contrarian says $297 is too high given competition. The Expansionist says it's too low for the value. Resolution depends on how much support and community access is bundled.

*Blind spots caught:* The Outsider's point that "Claude Code" means nothing to the target buyer is the single most important insight. Every advisor except the Outsider assumed the audience already knows what this is.

*Recommendation:* Don't build the course yet. Validate with a lower-commitment offer first. But reframe entirely: sell the outcome (automate your business, get 10 hours back per week), not the tool.

*One thing to do first:* Run a $97 live workshop called "How to automate your first business task with AI" to 50 people. Don't mention Claude Code in the title.

---

## Important notes

- **Always run all 5 advisors before any peer review.** Don't peek at one advisor's output and let it shape another's. In Claude Code this means spawning in parallel; in Claude.ai it means committing to each response in full before starting the next.
- **Always anonymize for peer review.** If reviewers know which advisor said what, they'll defer to certain thinking styles instead of evaluating on merit. Randomize the A-E mapping each time.
- **The chairman can disagree with the majority.** If 4 of 5 advisors say "do it" but the dissenter's reasoning is strongest, side with the dissenter and explain why. Majority isn't truth.
- **Don't council trivial questions.** If the user asks something with one right answer, just answer it. The council is for genuine uncertainty where multiple perspectives add value.
- **The visual report matters.** Most users scan the report rather than reading the full transcript. Make the HTML output clean and scannable.
