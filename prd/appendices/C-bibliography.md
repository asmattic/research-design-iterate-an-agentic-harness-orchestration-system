# Appendix C · Annotated Bibliography

Each entry: full citation, one-line summary, and the specific architectural decision in this PRD it justifies. Entries are organized by pillar (§04).

---

## Pillar 1 — Multi-agent orchestration

**Anthropic Engineering (2025).** *How we built our multi-agent research system.* Anthropic blog.
- **Summary:** Production retrospective of a multi-agent research system that beats single-agent Opus 4 by +90.2% at ~15× cost.
- **Justifies:** The orchestrator-subagent pattern (§§05, 06); the 15–20× cost ceiling in §02 hard constraints; explicit complexity-aware scaling (§08).

**Cognition AI (2025).** *Don't Build Multi-Agents.* Cognition blog.
- **Summary:** Contrarian case against multi-agent designs on the grounds that context-splitting loses shared grounding.
- **Justifies:** §03's discussion of when multi-agent is not the right answer; §08 decision tree including "single agent" as a first-class option.

**Wu, Q., Bansal, G., Zhang, J., et al. (2023).** *AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation.* Microsoft Research.
- **Summary:** Conversable agents framework with orchestrator patterns (GroupChatManager, sequential, nested).
- **Justifies:** §06 orchestrator-worker pattern; §16.8 as a candidate future adapter.

**Hong, S., Zheng, X., Chen, J., et al. (2024).** *MetaGPT: Meta Programming for Multi-Agent Collaborative Framework.* ICLR.
- **Summary:** Agents simulate roles in a software SOP, communicating via structured documents instead of free-form dialog.
- **Justifies:** §15 Agent Contract + Consensus Packet pattern (structured inter-agent communication); §18 worked example critique.

**Qian, C., Cong, X., Liu, W., et al. (2023).** *Communicative Agents for Software Development.* (ChatDev.)
- **Summary:** Simulated software company with role-playing agents. Instructive failure modes.
- **Justifies:** §07's case against free-form peer chat; §18 critique.

---

## Pillar 2 — Mixture of Experts / Agents

**Shazeer, N., Mirhoseini, A., Maziarz, K., et al. (2017).** *Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer.* ICLR.
- **Summary:** Sparse MoE routing — specialists beat monolithic capacity-per-FLOP.
- **Justifies:** The principle of specialist routing that §6.6 extends to the agent level.

**Fedus, W., Zoph, B., Shazeer, N. (2022).** *Switch Transformer: Scaling to Trillion Parameter Models.* JMLR.
- **Summary:** Simplified MoE routing; confirms MoE as a production-viable pattern.
- **Justifies:** Same as above.

**Wang, J., Wang, J., Athiwaratkun, B., et al. (2024).** *Mixture-of-Agents Enhances Large Language Model Capabilities.* Together AI.
- **Summary:** Multiple LLMs propose, an aggregator combines. MoA-Lite with 7B open-source models beats GPT-4o on AlpacaEval-2.
- **Justifies:** §6.6 cohort-scoped swarms; §9 consensus aggregation; dissent preservation.

---

## Pillar 3 — Self-consistency and deliberation

**Wang, X., Wei, J., Schuurmans, D., et al. (2023).** *Self-Consistency Improves Chain of Thought Reasoning in Language Models.* ICLR.
- **Summary:** Sampling the same query N times and taking majority beats greedy CoT by ~17pts on GSM8K.
- **Justifies:** §9 per-swarm sampling with n ≥ 3.

**Yao, S., Yu, D., Zhao, J., et al. (2023).** *Tree of Thoughts: Deliberate Problem Solving with Large Language Models.* NeurIPS.
- **Summary:** Branch-and-evaluate reasoning trees. Game of 24: 4% → 74%.
- **Justifies:** §8 decision tree; per-expert exploration.

**Irving, G., Christiano, P., Amodei, D. (2018).** *AI Safety via Debate.* OpenAI.
- **Summary:** Two adversarial agents + a judge; truthful answers easier to recognize than to generate.
- **Justifies:** §07 caucus pattern with judge arbitrator; §6.6 adversary role.

---

## Pillar 4 — Reflection and iterative refinement

**Shinn, N., Cassano, F., Labash, B., et al. (2023).** *Reflexion: Language Agents with Verbal Reinforcement Learning.* NeurIPS.
- **Summary:** Verbal self-critique stored in episodic memory; HumanEval pass@1 ~80% → ~91%.
- **Justifies:** §13.1 per-turn Reflexion cadence.

**Madaan, A., Tandon, N., Gupta, P., et al. (2023).** *Self-Refine: Iterative Refinement with Self-Feedback.* NeurIPS.
- **Summary:** Same-LLM generate / critique / revise loop with consistent uplift.
- **Justifies:** §13.1 Reflexion pattern; same-model critique baseline.

---

## Pillar 5 — Process supervision

**Lightman, H., Kosaraju, V., Burda, Y., et al. (2023).** *Let's Verify Step by Step.* OpenAI.
- **Summary:** Process reward models (PRMs) trained on step-correctness beat outcome reward models (ORMs). MATH: 78% vs 72%.
- **Justifies:** §14.3 deterministic gates vs rubric judges; §6.7 verifier at every hop; §02 precedence rule.

---

## Pillar 6 — Context engineering

**Liu, N. F., Lin, K., Hewitt, J., et al. (2023).** *Lost in the Middle: How Language Models Use Long Contexts.*
- **Summary:** Retrieval accuracy drops significantly in the middle of long contexts.
- **Justifies:** §6.3 clean-context primary orchestrator; §10 tiered memory with explicit loads.

**Anthropic Engineering (2025).** *Effective Context Engineering for AI Agents.* Anthropic blog.
- **Summary:** Context is a budget; curation discipline matters as much as model quality.
- **Justifies:** §6.4.1 Context Manager discipline; packet summarization.

---

## Pillar 7 — Constitutional AI

**Bai, Y., Kadavath, S., Kundu, S., et al. (2022).** *Constitutional AI: Harmlessness from AI Feedback.* Anthropic.
- **Summary:** A model critiques its own outputs against a written constitution; reduces harmful outputs without hand-labeled harm data.
- **Justifies:** §12 policy guardrails; constitutional judge LLM call.

---

## Pillar 8 — LLM-as-Judge and calibration

**Zheng, L., Chiang, W.-L., Sheng, Y., et al. (2024).** *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.* NeurIPS.
- **Summary:** GPT-4 as judge agrees with humans ~80%; comparable to inter-human agreement.
- **Justifies:** §9.2 semantic grouping via LLM-as-judge; §14 rubric judges with calibration.

**Brier, G. W. (1950).** *Verification of Forecasts Expressed in Terms of Probability.* Monthly Weather Review.
- **Summary:** Proper scoring rule rewarding accurate confidence.
- **Justifies:** §9.4 Brier score as calibration metric.

**Platt, J. (1999).** *Probabilistic Outputs for Support Vector Machines.*
- **Summary:** Calibration of probability outputs.
- **Justifies:** §6.4.4 Signal/Noise Attributor calibration approach.

**Kadavath, S., Conerly, T., Askell, A., et al. (2022).** *Language Models (Mostly) Know What They Know.* Anthropic.
- **Summary:** LLMs are partially calibrated about their own uncertainty.
- **Justifies:** §6.4.2 BS Detector uses self-reported confidence with skepticism; §6.4.5 Weight Tweaker adjustments.

---

## Secondary sources (cited in context)

**Minsky, M. (1986).** *The Society of Mind.*
- **Summary:** Specialist agents collaborating — the ancestor of all multi-agent design.
- **Justifies:** Philosophical grounding for §§05–06.

**Silver, D., Huang, A., Maddison, C.J., et al. (2016).** *Mastering the game of Go with deep neural networks and tree search.* Nature.
- **Summary:** MCTS + self-play; branch exploration at scale.
- **Justifies:** Background for §8 branching and swarm design.

**Greshake, K., Abdelnabi, S., Mishra, S., et al. (2023).** *Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection.*
- **Summary:** Document the prompt-injection attack surface.
- **Justifies:** §12 prompt-injection defenses.

**OWASP (2024).** *LLM Top 10.*
- **Summary:** Industry prioritization of LLM vulnerabilities.
- **Justifies:** §12 guardrail categories.

**NVIDIA (2023).** *NeMo Guardrails.*
- **Summary:** Programmable guardrails library.
- **Justifies:** §12 implementation option.

**Meta (2023/2024).** *Llama Guard* (v1 and v3).
- **Summary:** Classifier-based input/output safety.
- **Justifies:** §12 implementation option.

**Mialon, G., Fourrier, C., Swift, C., et al. (2023).** *GAIA: a benchmark for General AI Assistants.*
- **Summary:** Research-task benchmark with tool use.
- **Justifies:** §14 benchmark set.

**Jimenez, C. E., Yang, J., Wettig, A., et al. (2024).** *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* ICLR.
- **Summary:** Real GitHub issues paired with hidden tests as a rigorous coding benchmark.
- **Justifies:** §18 worked example benchmark.

**OpenAI (2025).** *BrowseComp.*
- **Summary:** Browse-and-synthesize benchmark.
- **Justifies:** §14 benchmark set.

**Wang, X., Li, B., Song, Y., et al. (2024).** *MINT: Evaluating LLMs in Multi-Turn Interaction with Tools and Language Feedback.*
- **Summary:** Multi-turn interactive benchmark.
- **Justifies:** §14 benchmark set.

---

## How to use this bibliography

1. If you disagree with a design decision in the PRD, find the chapter's citations.
2. Read the original paper.
3. If the paper supports a different conclusion, open an issue / PR against the relevant chapter with the alternative position.
4. If the paper has been superseded, add the successor to this appendix and cross-reference.

Citations earn their place by being load-bearing. An entry that no decision depends on should be removed.
