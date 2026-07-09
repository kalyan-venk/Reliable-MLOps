# MLOps Project Brief — "PredictOps": End-to-End ML Serving Pipeline with Production Ops

## How to use this brief
Paste this whole file as the opening message of a Claude Code (or Cowork) session.
This is a LEARNING build, not a ship-fast build. I am building this RIGHT NOW and learning
along the way — I have not finished the underlying roadmap days yet, and that's fine. Teach
me as we go. The non-negotiable rule below is what separates this from vibe coding. Do not
drop it to save time.

### THE ONE RULE THAT MAKES THIS DEFENSIBLE
After each phase, before moving to the next, Claude Code must:
1. Explain WHY each non-obvious decision was made (why this structure, why this library,
   why this config value, why this and not the obvious alternative).
2. Ask me 3 "interviewer questions" about what we just built and wait for my answers.
3. Only proceed once I've answered. If I answer wrong, correct me, don't move on.
This is how I build interview answers while the code gets built. Enforce it even though
I'm building fast — the interviewer-Q gate is the thing that makes speed safe here.

---

## What we are building
A production ML serving pipeline with the full ops loop around it: containerization,
serving, CI/CD with an eval gate, model registry with promotion, and drift detection.
The model itself is deliberately simple (tabular binary classification). The POINT is
everything around the model. The domain is boring on purpose so the MLOps is the star.

Project name (repo): predictops

### RESUME FRAMING — READ THIS, IT DRIVES NAMING
The word for the boring domain (customer retention / churn) must NEVER appear in the
project title or tagline. Everyone has a churn model; the domain is not the differentiator.
The OPS DEPTH is. So:
- Resume title: "PredictOps: Production MLOps Pipeline — CI Eval Gate, Model Registry,
  Drift Detection"
- The domain gets ONE passing mention inside a single bullet, never the headline.
- Every lead bullet sells a system property (a bad model can't merge, models get promoted
  through stages, drift is caught automatically), not a model accuracy number.
Name variables/modules generically (data, model, target) so the code reads as a template,
not a churn tutorial.

## Why this project
This is my breadth/infra artifact to sit alongside two LLM projects (Master's Research
multi-agent system, Inference-Lens). Every ML Eng JD lists Docker, FastAPI, CI/CD, MLflow.
Almost none list a novel domain. The differentiation is the ops loop that ~everyone else's
portfolio project skips, because they stop at the trained model. I don't stop there.

## Dataset
Use the Telco Customer Churn dataset (public, ~7K rows, tabular, binary target) OR a small
self-contained synthetic generator. Decide in Phase 0 and tell me the tradeoff (real data =
credible README story, synthetic = fully reproducible CI with no external pull). I'll pick.
Either way, refer to it in code as the generic "dataset" and the label as "target".

---

## SCOPE FENCE — where this project STARTS and STOPS
We go just deep enough to own the end-to-end loop. We do NOT rabbit-hole. Explicit lines:

IN SCOPE (this is the whole project, nothing more):
- One simple, well-evaluated model (LogReg baseline + XGBoost, pick winner).
- FastAPI serving with validation and health/predict/info/reload.
- Multi-stage Docker + docker-compose.
- GitHub Actions CI: lint, test, and a MODEL EVAL GATE that blocks a bad model.
- MLflow tracking + registry + staging->production promotion.
- Evidently drift detection with a threshold warning.
- One entry script/Makefile chaining the full loop, plus a clean README.

OUT OF SCOPE (do not start these, even if they seem cool):
- No hyperparameter-tuning marathons. One sensible grid search, move on.
- No feature-engineering rabbit holes. Basic preprocessing pipeline, done.
- No cloud deploy (no live SageMaker endpoint, no paid infra). Local + CI only.
- No Prometheus/Grafana observability stack. (Nice later, not now.)
- No frontend/UI. Swagger UI is the interface.
- Kubernetes is OPTIONAL and minimal — see Phase 7. Do not expand it.
- No auth, no database, no message queue. This is a serving pipeline, not a platform.
If Claude Code proposes anything in the OUT list, it must stop and ask me first.

## DEFINITION OF DONE (the project is finished when ALL of these are true)
1. `docker-compose up` starts the service; /predict returns a valid prediction from outside
   the container.
2. Pushing a deliberately-degraded model makes CI FAIL on the eval gate; fixing it makes CI
   pass. (I have demonstrated this at least once and understand the mechanism.)
3. A model is registered in MLflow and promoted staging->production.
4. An Evidently drift report generates, logs a drift score, and trips a threshold warning
   on shifted data.
5. One command runs the full loop: load -> train -> eval -> drift check -> log -> serve.
6. README has: architecture diagram, setup steps, example API call, CI badge, "what I'd do
   with more time".
7. I can answer the interviewer questions from every phase out loud without notes.
When 1-7 are true, we STOP. No gold-plating. Any further idea goes in the README's "future
work" section, not the codebase.

---

## PHASE MAP (each maps to roadmap days 16-22; I'm learning these as we build)

### Phase 0 — Repo scaffold + decisions (~30 min)
- Repo structure: src/, tests/, .github/workflows/, Dockerfile, docker-compose.yml,
  requirements.txt, README.md, .dockerignore, .gitignore.
- Decide dataset (real vs synthetic) with me — state the tradeoff, I pick.
- Explain: why src-layout, why tests separate, why pin deps.
- INTERVIEWER Qs: "Why pin dependency versions?" "What does .dockerignore save you?"
  "Why keep training and serving code separate?"

### Phase 1 — Model + training script (~45 min)
- train.py: load data, sklearn Pipeline (impute -> scale -> encode -> classifier).
  LogisticRegression baseline THEN XGBoost, compare, pick winner.
- Log to MLflow: params, metrics (accuracy, precision, recall, F1, ROC-AUC), model artifact.
- Save winning model with joblib.
- Explain: why a Pipeline and not manual preprocessing (leakage). Why StratifiedKFold.
  Why log to MLflow instead of print.
- INTERVIEWER Qs: "How does a Pipeline prevent leakage?" "Why is accuracy the wrong headline
  metric here?" "What's an MLflow run vs the registry?"

### Phase 2 — FastAPI serving (~45 min)
- app.py: /health, /predict (POST, Pydantic request+response), /info, /reload.
- joblib load on startup, Pydantic validation, try/except on /predict.
- Test with curl + Swagger UI.
- Explain: why Pydantic vs raw dict, why load-on-startup, what /health is for (LB/k8s probes),
  why /reload.
- INTERVIEWER Qs: "Walk me through a bad input." "Why separate /health from /predict?"
  "How would you version this API?"

### Phase 3 — Dockerize (~45 min)
- Multi-stage Dockerfile (builder installs deps, final copies only what's needed).
  .dockerignore, expose port, env vars for config. docker-compose.yml (one-command start).
- Build, run, hit /predict from outside. Report single-stage vs multi-stage image size.
- Explain: what a layer is, why multi-stage shrinks the image, why python:slim, RUN chaining,
  ENTRYPOINT vs CMD.
- INTERVIEWER Qs: "Why multi-stage?" "ENTRYPOINT vs CMD?" "How do layers affect rebuild speed?"

### Phase 4 — CI/CD with GitHub Actions (~60 min) [THE CENTERPIECE]
- .github/workflows/ci.yml: checkout -> install -> ruff lint -> pytest.
- test_model_quality.py: assert ROC-AUC >= threshold. THIS IS THE EVAL GATE.
- Deliberately degrade the model, watch CI fail, fix it. This is the money demo — make sure
  I run it myself and understand exactly why it failed.
- Extend: on pass, build Docker image (stop at build; only wire a real registry push if I
  say so).
- Explain: what an eval gate is and why it lives in CI, why lint AND test, what triggers the run.
- INTERVIEWER Qs: "How do you stop a bad model reaching prod?" "What's your CI trigger?"
  "Why assert a metric in CI instead of only unit tests?"

### Phase 5 — MLflow registry + promotion (~30 min)
- Nested runs, register the model, transition staging -> production.
- Explain: registry vs raw runs, what staging/production mean operationally.
- INTERVIEWER Qs: "How does a model get promoted on your team?" "Experiment run vs registered
  model?"

### Phase 6 — Drift detection with Evidently (~45 min)
- Reference vs current split (inject noise into current to simulate drift). Evidently
  data-drift report, log a drift score, threshold warning.
- INTERVIEW TIE-IN: at sensen.ai I detected ANPR model drift manually; this is the automated
  version. Make sure I can say that sentence and defend it.
- Explain: data drift vs target drift vs concept drift, how Evidently measures it, what action
  a tripped threshold triggers.
- INTERVIEWER Qs: "Data drift vs concept drift?" "How would you make this run automatically?"
  "What action follows a drift alert?"

### Phase 7 — Wire the loop + README + (optional minimal k8s) (~45 min)
- One entry script/Makefile: load -> train -> eval -> drift check -> log to MLflow -> serve.
- README: architecture diagram (ascii/mermaid fine), setup, example API call, CI badge,
  "what I'd do with more time". Type hints on every function, docstrings on public ones.
- Kubernetes OPTIONAL and I have Docker-only production experience. If we touch it: Deployment
  + Service, 2 replicas, scale to 3, and LABEL it "conversational, not deep." Do NOT oversell
  k8s on the resume. If time is tight, skip k8s entirely — it is not in the Definition of Done.
- INTERVIEWER Qs: "Walk the whole pipeline end to end." "Where does this break at 100x scale?"
  "Weakest part of the system and how you'd harden it?"

---

## Stack (only what's defendable and on my resume)
Python, scikit-learn, XGBoost, FastAPI, Pydantic, Docker (multi-stage), docker-compose,
GitHub Actions, MLflow, Evidently, pytest, ruff, joblib. Kubernetes only as a labeled
minimal optional add-on.

## What I already know vs am learning (calibrate explanations)
- Solid: Python, SQL, Linux, Docker (production, single-stage), FastAPI basics, MLflow basics.
- Learning here: multi-stage Docker, CI eval gates, MLflow registry/promotion, Evidently drift,
  tying it into one loop. Spend the explanation budget HERE.

## Output discipline
- Small commit per phase, clear messages. Git history should read like a story.
- After each phase: the WHY explanation + 3 interviewer Qs, then STOP and wait for me.
- Do not batch phases without my go-ahead. Do not skip the interviewer-Q gate to save time.
- Respect the SCOPE FENCE and stop at the DEFINITION OF DONE. No rabbit holes, no gold-plating.
