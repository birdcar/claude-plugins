# Writing Style Frameworks

A writing style framework provides the foundational philosophy for how the user writes. It sits at the bottom of the voice stack — registers and channels layer on top of it.

## How Style Frameworks Apply

The `style.md` file in the user's config directory specifies their chosen framework (or a custom blend). When assembling a voice profile, the config-resolver reads this file first, and register/channel rules override or extend it.

A style framework typically defines:

- Sentence structure preferences (short vs complex, active vs passive)
- Word choice principles (concrete vs abstract, plain vs elevated)
- Rhythm and cadence rules
- Clarity vs style trade-offs

## Known Frameworks

### Strunk & White (The Elements of Style)

- **Core principle**: Omit needless words. Vigorous writing is concise.
- **Sentence structure**: Prefer short, declarative sentences. Use the active voice.
- **Word choice**: Use definite, specific, concrete language. Avoid qualifiers ("rather", "very", "little", "pretty").
- **Paragraphs**: Begin each paragraph with a topic sentence. End with a sentence of consequence.
- **Rhythm**: Vary sentence length for interest, but default to brevity.
- **Best for**: Technical writing, business communication, documentation.

### Stanley Fish (How to Write a Sentence)

- **Core principle**: The sentence is the basic unit of meaning. Master the sentence form before the paragraph.
- **Sentence structure**: Each sentence earns its length through propulsive structure. Subordination creates momentum.
- **Word choice**: Precision matters, but rhythm and surprise matter more. Choose words that advance the sentence's energy.
- **Forms**: Three master sentence types:
  - Additive: layers detail (`The dog ran, its ears flapping, its tongue trailing, its joy uncontainable.`)
  - Subordinating: builds hierarchy (`Although the evidence suggested otherwise, the committee, swayed by precedent, voted to proceed.`)
  - Satiric: undercuts expectation (setup, setup, reversal)
- **Best for**: Personal writing, essays, social media where voice matters.

### George Orwell (Politics and the English Language)

- **Core principle**: Good prose is like a window pane — clear, transparent, honest.
- **Rules**:
  1. Never use a metaphor you are used to seeing in print
  2. Never use a long word where a short one will do
  3. If it is possible to cut a word out, cut it out
  4. Never use the passive where you can use the active
  5. Never use a foreign phrase, scientific word, or jargon word if you can think of an everyday equivalent
  6. Break any of these rules sooner than say anything outright barbarous
- **Best for**: Persuasive writing, public communication, social commentary.

### Plain Language (Federal Plain Language Guidelines)

- **Core principle**: Write for your reader, not for yourself. The reader should understand your point on first reading.
- **Sentence structure**: Average sentence length under 20 words. One idea per sentence.
- **Word choice**: Common words over technical jargon. Define terms when unavoidable.
- **Organization**: Most important information first. Use headers, lists, and tables.
- **Best for**: Documentation, instructions, broad-audience communication.

### Custom Framework

Users can define their own framework in `style.md` by describing their writing philosophy, preferred sentence patterns, and word choice principles in natural language. The voice trainer helps capture this during the training flow.

## Style Framework in `style.md`

Example `style.md` content:

```markdown
# Writing Style

## Framework

Based on Orwell's rules with Fish's sentence energy.

## Principles

- Cut ruthlessly — every word earns its place
- Active voice by default, passive only for emphasis
- Vary sentence length: short sentences for impact, longer ones for flow
- Concrete over abstract — show, don't tell
- No cliches, no buzzwords, no filler

## Sentence Patterns

- Open with the subject when making a claim
- Use subordinate clauses to build momentum, not to delay the point
- End sentences with the strongest word
```

The voice trainer generates this file during the training interview based on the user's preferences and writing samples.
