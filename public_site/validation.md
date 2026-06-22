# How reliable are these labels?

*(Validation against human experts and a 13-model benchmark. Readable companion to `validation.html`. Numbers are preliminary: a 20-letter expert set, 3 coders.)*

---

Throughout this site, a **label** means a **classification** the model assigns to a letter. Each letter gets three of them:

- its **stance**: whether the letter *opposes*, *supports*, or gives *conditional* backing to the proposal;
- its **entity**: who is writing, e.g. an individual, an accountant (CPA), an academic, an issuer, or a trade association;
- its **rationale**: which economic arguments the letter actually makes (investor protection, market function, fraud risk, compliance burden, and so on), drawn from a fixed list of codes.

Those three labels populate the charts and the table on the main page, and they are produced by a language model reading each letter.

**How far can we trust the ability of large language models to classify text like this?**

## How I assess it

Reliability is built into the pipeline first. Every label here is a **majority vote of a three-rater ensemble** (the primary / literalist / skeptic lenses described on the main methodology page), so a single erratic read cannot move the headline. Early on I also **cross-checked ~137 letters against a different model family** (ChatGPT-5.5) to see whether the calls held up outside one vendor, which is the cross-model section on the main methodology page.

Those are internal consistency checks. To go further, I ran a separate **validation study** that measures the classifier against two external standards: a human expert gold standard, and a broad benchmark of other models. The study is ongoing; what follows is a preliminary report on a small expert-coded set, and the numbers will firm up as the coded sample grows.

## A human expert gold standard

Three experts (myself and two colleagues with accounting and comment-letter experience) independently coded the same stratified sample of 20 letters under the full rubric. Expert-versus-expert agreement sets the realistic ceiling. Even trained readers disagree, especially on entity.

A word on how I measure agreement, since every number below uses it: a statistic called **kappa (κ)**. The intuition: picture two people independently sorting the same letters into bins. Some of their answers will line up purely by luck, especially when one bin ("Oppose") is very common to begin with. Kappa is the agreement that is *left over* after you subtract out that lucky overlap: **κ = 1** means they agree every time, **κ = 0** means they agree no more than two people labeling at random would, and the closer to 1, the more the agreement reflects genuine shared judgment rather than coincidence. By convention, above ~0.8 reads as "near-perfect" and 0.6–0.8 as "substantial." **Fleiss' κ** is the same idea applied to a whole panel of raters at once (three or more) instead of a single pair, and it summarizes how well the three experts agree together.

On **stance**, agreement among the three experts is **quite high (Fleiss' κ = 0.82)**: trained readers largely converge on whether a letter opposes, supports, or conditionally backs the proposal. On **entity** (who is writing) it is **noticeably lower, Fleiss' κ = 0.67**, because deciding whether a letter speaks "as a CPA" or "as an individual" is a genuine judgment call the experts themselves split on. That lower figure is the true ceiling for the harder task. We would not ordinarily expect a model to agree with the experts more closely than the experts agree among themselves, although that remains possible. Human agreement is the yardstick we benchmark the models against.

This human comparison is a development-stage validation on a small sample with three coders so far, and I am expanding both the coded set and the coder pool. Treat the human-anchored numbers as encouraging but preliminary.

## A 13-model benchmark on the same letters

Thirteen models classified those letters from the letter text alone. I deliberately spanned a range within each family rather than relying on a single model: three Claude tiers (Haiku, Sonnet, Opus); three GPT models reaching back across generations (the 2023-era GPT-3.5 up to today's GPT-5.5); three Gemini tiers (Pro, Flash, Flash-Lite); and four open-weight models. By **"frontier"** I mean the newest flagship in each family: Opus 4.8, GPT-5.5, Gemini Pro. Two findings:

- **Stance:** the strongest models agree with the human experts about as well as the experts agree with each other (Cohen's κ ≈ 0.85–0.92 against individual coders, versus the 0.82 three-rater ceiling). On stance, a frontier model is about as reliable a rater as adding another human expert.
- **Entity (who is writing):** every model falls below the human ceiling (κ ≈ 0.34–0.59), a harder call than stance for people and machines alike, since the experts themselves slip here (rationale, below, is harder still). The telling detail is that the models miss in the *same* places: open and frontier alike read a corporate writer as a private individual, or a student as an individual.

A note on coverage, and on the open models specifically. The agreement figures above come from the 20-letter expert set, the only letters with human labels, and that holds for every model open and closed. The open-weight models are not uniformly strong: against the human gold, phi-4 and Mistral reach Cohen's κ 0.85 on stance and gemma 0.84, all tying the commercial frontier and sitting at the 0.82 human ceiling, while Qwen, a 0.5-billion-parameter model included as a deliberate floor, reaches only κ 0.30. The four open models were additionally run over the full corpus of every letter on the site, so the stance result does not rest on the small sample alone.

## Rationale: the hardest dimension of all

Stance is one pick out of three and entity one out of ten, but rationale is a *set*: a single letter can invoke several economic arguments at once, chosen from a couple dozen codes. There is no one right answer to match against, so agreement here is measured as how much two readers' *sets* of codes overlap rather than by kappa, and it is the lowest-agreement dimension of the three, for humans and models alike.

**On the human side**, the experts overlap on rationale only about half the time, well below their stance agreement. Much of that reflects *coding depth*: readers differ in how many arguments they record per letter. One expert codes inclusively, around three per letter; another codes minimally, closer to one or two.

**On the cross-model side**, the models divide their emphasis differently from the people. They reach for specific economic-mechanism arguments (fraud and insider risk, market function, information asymmetry) two to three times as often as the human coders do, while leaning less on the single broad argument the humans use most, investor protection. The models and the humans read the same letters; they apportion the *why* differently.

The upshot: rationale is where I would trust the labels least, and where the method still needs the most work: fixing a consistent coding depth before these overlap numbers are fully comparable. Stance is solid, entity is harder, and rationale is the challenge.

## It is not a Claude-specific result

The finding does not depend on any one vendor. Measured against the human gold standard on the expert set, three open-weight models that anyone can download and run for free (a 14B, a 24B, and a 27B) reach Cohen's κ of 0.84 to 0.85 on stance: the same band as Opus 4.8, GPT-5.5, and Gemini Pro, and at the 0.82 three-rater human ceiling. On stance, a free model rates the letters about as reliably as the commercial frontier and about as well as adding another human expert. The strongest closed models also re-derive the stance labels published on this site almost perfectly; several agree on 100% of the validation letters. (Entity and rationale reproduce less well, as expected since they are the harder dimensions.)
