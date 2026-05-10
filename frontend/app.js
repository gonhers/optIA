import React, { useEffect, useRef, useState } from "https://esm.sh/react@18.3.1";
import { createRoot } from "https://esm.sh/react-dom@18.3.1/client";
import htm from "https://esm.sh/htm@3.1.1";
import {
  DEFAULT_CANDIDATE_COUNT,
  MAX_CANDIDATE_COUNT,
  MIN_CANDIDATE_COUNT,
  clampCandidateCount,
  dashboardAudienceViews,
  formatCandidateCount,
  getDashboardContent,
  getLanguageOption,
  languageOptions,
  loadingMessageKeys,
  samplePrompt,
  workspaceViews,
  workflowSteps,
} from "./config.js?v=20260504-subscriber-dashboard";
import {
  getLanguageDisplayLabel,
  getUiText,
  translateDynamicText,
} from "./pageTranslation.js?v=20260504-subscriber-dashboard";

const html = htm.bind(React.createElement);

const featureCards = [
  ["fastDemoLoop", "fastDemoLoopCopy"],
  ["teamFriendlyReview", "teamFriendlyReviewCopy"],
];

const DEFAULT_PAGE_LANGUAGE = "es";

/**
 * @typedef {Object} Candidate
 * @property {string} text
 * @property {number} score
 */

/**
 * @typedef {Object} OptimizeResult
 * @property {string} best_response
 * @property {Candidate[]} candidates
 */

/**
 * @typedef {Object} ApiErrorResponse
 * @property {string | string[]=} detail
 */

function CandidateCard({ candidate, index, bestScore, t, translateContent }) {
  const isBest = candidate.score === bestScore && index === 0;

  return html`
    <article
      className=${`glass-card rounded-[1.75rem] border p-5 shadow-neon transition duration-300 ${
        isBest
          ? "border-cyan/45 bg-gradient-to-br from-cyan/16 via-panelSoft to-panel ring-1 ring-cyan/40"
          : "border-line bg-panelSoft/90"
      }`}
    >
      <div className="mb-4 flex items-center justify-between gap-3">
        <span className="text-xs font-bold uppercase tracking-[0.28em] text-mist">
          ${isBest ? t("topCandidate") : t("candidateWithNumber", { number: index + 1 })}
        </span>
        <span
          className=${`glass-chip rounded-full px-3 py-1 text-sm font-bold ${
            isBest ? "bg-cyan text-abyss" : "bg-snow/10 text-snow"
          }`}
        >
          ${candidate.score.toFixed(1)}
        </span>
      </div>
      <p className="text-sm leading-7 text-snow/78">${translateContent(candidate.text)}</p>
    </article>
  `;
}

function LoadingCard({ title }) {
  return html`
    <div className="glass-card rounded-[1.75rem] border border-line bg-panelSoft/80 p-5 shadow-glow">
      <div className="flex items-center gap-3">
        <span className="h-2.5 w-2.5 rounded-full bg-cyan animate-pulse"></span>
        <p className="text-sm font-semibold text-snow/90">${title}</p>
      </div>
      <div className="mt-4 space-y-3">
        <div className="h-3 w-full rounded-full bg-snow/8"></div>
        <div className="h-3 w-11/12 rounded-full bg-snow/8"></div>
        <div className="h-3 w-8/12 rounded-full bg-snow/8"></div>
      </div>
    </div>
  `;
}

/**
 * @param {Response} response
 * @returns {Promise<string>}
 */
async function getApiErrorMessage(response) {
  const fallbackMessage = "No se pudo procesar esa solicitud.";

  try {
    /** @type {ApiErrorResponse} */
    const payload = await response.json();

    if (typeof payload.detail === "string") {
      return payload.detail;
    }

    if (Array.isArray(payload.detail) && payload.detail.length > 0) {
      return payload.detail.join(" ");
    }
  } catch {
    return fallbackMessage;
  }

  return fallbackMessage;
}

/**
 * @param {string | undefined} code
 * @returns {string}
 */
function getLanguageBadge(code) {
  return (code ?? DEFAULT_PAGE_LANGUAGE).toUpperCase();
}

function PromptComposer({ t, candidateCount, loading, error, onCandidateCountChange, onOptimize, onClearError }) {
  const [prompt, setPrompt] = useState(() => samplePrompt);

  const handleInput = (event) => {
    setPrompt(event.target.value);
    if (error) {
      onClearError();
    }
  };

  return html`
    <div className="glass-panel rounded-[2rem] border border-snow/10 p-6 shadow-glow sm:p-8">
      <div className="flex flex-col gap-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.24em] text-cyan/80">${t("promptStudio")}</p>
            <h2 className="mt-2 font-display text-3xl text-snow">${t("shapeRequestBeforeScoring")}</h2>
          </div>
          <button
            className="glass-chip rounded-full border border-cyan/20 bg-cyan/8 px-4 py-2 text-sm font-semibold text-cyan transition hover:border-cyan/40 hover:bg-cyan/14 hover:text-snow"
            onClick=${() => setPrompt(samplePrompt)}
          >
            ${t("useSamplePrompt")}
          </button>
        </div>

        <div className="glass-card rounded-[1.75rem] border border-snow/10 bg-panel p-5 shadow-neon">
          <label className="mb-3 block text-sm font-medium uppercase tracking-[0.24em] text-mist" htmlFor="prompt">
            ${t("inputPrompt")}
          </label>
          <textarea
            id="prompt"
            value=${prompt}
            onInput=${handleInput}
            rows="9"
            className="min-h-[220px] w-full rounded-[1.5rem] border border-snow/10 bg-abyss/80 p-5 text-sm leading-7 text-snow shadow-[inset_0_1px_0_rgba(255,255,255,0.04),0_10px_28px_rgba(4,12,24,0.16)] placeholder:text-mist/50 focus:border-cyan/50 focus:outline-none focus:ring-2 focus:ring-cyan/20"
            placeholder=${t("promptPlaceholder")}
          />

          <div className="mt-5 flex flex-col gap-4 rounded-[1.5rem] border border-snow/10 bg-snow/[0.03] p-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-snow">${t("candidateCount")}</p>
              <p className="mt-1 text-sm text-mist">${t("candidateCountHelper", { max: MAX_CANDIDATE_COUNT })}</p>
            </div>

            <div className="glass-chip inline-flex items-center gap-2 rounded-full border border-snow/10 bg-snow/[0.04] px-2 py-2">
              <button
                className="flex h-9 w-9 items-center justify-center rounded-full border border-snow/10 bg-snow/[0.04] text-lg font-bold text-snow transition hover:border-cyan/40 hover:text-cyan disabled:cursor-not-allowed disabled:opacity-35"
                onClick=${() => onCandidateCountChange(candidateCount - 1)}
                disabled=${loading || candidateCount <= MIN_CANDIDATE_COUNT}
                aria-label=${t("decreaseCandidateCount")}
              >
                -
              </button>
              <span className="min-w-[5.5rem] px-3 text-center text-sm font-bold text-snow">
                ${candidateCount}
              </span>
              <button
                className="flex h-9 w-9 items-center justify-center rounded-full border border-snow/10 bg-snow/[0.04] text-lg font-bold text-snow transition hover:border-cyan/40 hover:text-cyan disabled:cursor-not-allowed disabled:opacity-35"
                onClick=${() => onCandidateCountChange(candidateCount + 1)}
                disabled=${loading || candidateCount >= MAX_CANDIDATE_COUNT}
                aria-label=${t("increaseCandidateCount")}
              >
                +
              </button>
            </div>
          </div>

          <div className="mt-5 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex flex-wrap items-center gap-3">
              <button
                className="inline-flex items-center justify-center gap-3 rounded-full bg-gradient-to-r from-cyan via-aqua to-teal px-6 py-3 text-sm font-bold text-abyss transition hover:translate-y-[-1px] hover:shadow-neon disabled:cursor-not-allowed disabled:opacity-75"
                onClick=${() => onOptimize(prompt)}
                disabled=${loading || !prompt.trim()}
              >
                ${
                  loading
                    ? html`
                        <span className="h-4 w-4 rounded-full border-2 border-abyss/20 border-t-abyss animate-spin"></span>
                        ${t("optimizing")}
                      `
                    : t("optimize")
                }
              </button>
              <span className="glass-chip rounded-full border border-snow/10 bg-snow/[0.05] px-4 py-2 text-sm text-mist">
                ${t("returnsBestResponsePlusAllCandidates")}
              </span>
            </div>
            <p className="text-sm text-mist">${t("responsiveSimulationApi")}</p>
          </div>

          ${
            loading
              ? html`
                  <div className="glass-card mt-5 rounded-[1.5rem] border border-cyan/15 bg-cyan/[0.06] p-4">
                    <div className="mb-3 flex items-center gap-3">
                      <span className="h-2.5 w-2.5 rounded-full bg-cyan animate-pulse"></span>
                      <p className="text-sm font-semibold text-snow">${t("optimizerWorking")}</p>
                    </div>
                    <div className="grid gap-3 sm:grid-cols-3">
                      ${loadingMessageKeys.map(
                        (key) => html`
                          <div className="glass-card rounded-2xl border border-snow/8 bg-snow/[0.03] p-4">
                            <div className="mb-3 h-1.5 w-full overflow-hidden rounded-full bg-snow/10">
                              <div className="h-full w-2/3 rounded-full bg-gradient-to-r from-cyan to-teal animate-pulse"></div>
                            </div>
                            <p className="text-sm leading-6 text-mist">${t(key)}</p>
                          </div>
                        `
                      )}
                    </div>
                  </div>
                `
              : null
          }

          ${
            error
              ? html`<p className="glass-card mt-4 rounded-[1.25rem] border border-coral/30 bg-coral/10 px-4 py-3 text-sm text-snow">${error}</p>`
              : null
          }
        </div>
      </div>
    </div>
  `;
}

function getToneClasses(tone) {
  switch (tone) {
    case "teal":
      return {
        chip: "border border-teal/20 bg-teal/10 text-teal",
        dot: "bg-teal",
      };
    case "amber":
      return {
        chip: "border border-coral/20 bg-coral/10 text-coral",
        dot: "bg-coral",
      };
    case "sky":
      return {
        chip: "border border-aqua/20 bg-aqua/10 text-aqua",
        dot: "bg-aqua",
      };
    case "coral":
      return {
        chip: "border border-coral/20 bg-coral/10 text-coral",
        dot: "bg-coral",
      };
    case "cyan":
    default:
      return {
        chip: "border border-cyan/20 bg-cyan/10 text-cyan",
        dot: "bg-cyan",
      };
  }
}

function WorkspaceSwitch({ t, activeWorkspace, onSelectWorkspace }) {
  return html`
    <div className="mt-6 flex flex-wrap gap-3">
      ${workspaceViews.map((workspace) => {
        const isActive = workspace.id === activeWorkspace;
        return html`
          <button
            key=${workspace.id}
            className=${`glass-chip rounded-full px-4 py-2 text-sm font-semibold transition ${
              isActive
                ? "border border-cyan/25 bg-cyan/12 text-cyan"
                : "border border-snow/10 bg-snow/[0.04] text-mist hover:border-cyan/30 hover:text-snow"
            }`}
            onClick=${() => onSelectWorkspace(workspace.id)}
          >
            ${t(workspace.labelKey)}
          </button>
        `;
      })}
    </div>
  `;
}

function DashboardStatCard({ stat }) {
  const toneClasses = getToneClasses(stat.tone);

  return html`
    <article className="glass-card rounded-[1.5rem] border border-snow/10 bg-snow/[0.04] p-5 shadow-glow">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.22em] text-mist">${stat.label}</p>
          <p className="mt-3 font-display text-3xl text-snow">${stat.value}</p>
        </div>
        <span className=${`rounded-full px-3 py-1 text-xs font-bold ${toneClasses.chip}`}>${stat.delta}</span>
      </div>
      <p className="mt-3 text-sm text-mist">${stat.meta}</p>
    </article>
  `;
}

function DashboardBoard({ board }) {
  return html`
    <div className="glass-panel rounded-[2rem] border border-snow/10 p-6 shadow-glow sm:p-8">
      <div>
        <p className="text-sm font-bold uppercase tracking-[0.24em] text-cyan/80">${board.eyebrow}</p>
        <h2 className="mt-2 font-display text-3xl text-snow">${board.title}</h2>
      </div>

      <div className="mt-6 space-y-4">
        ${board.items.map((item) => {
          const toneClasses = getToneClasses(item.tone);

          return html`
            <div className="glass-card rounded-[1.5rem] border border-snow/10 bg-snow/[0.04] p-4">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className=${`h-2.5 w-2.5 rounded-full ${toneClasses.dot}`}></span>
                  <p className="text-sm font-semibold text-snow">${item.title}</p>
                </div>
                <span className=${`rounded-full px-3 py-1 text-[11px] font-bold uppercase tracking-[0.18em] ${toneClasses.chip}`}>
                  ${item.status}
                </span>
              </div>
              <p className="mt-3 text-sm text-mist">${item.meta}</p>
            </div>
          `;
        })}
      </div>
    </div>
  `;
}

function DashboardRecordsPanel({ panel }) {
  return html`
    <div className="glass-panel rounded-[2rem] border border-snow/10 p-6 shadow-glow sm:p-8">
      <div className="mb-6">
        <p className="text-sm font-bold uppercase tracking-[0.24em] text-cyan/80">${panel.eyebrow}</p>
        <h2 className="mt-2 font-display text-3xl text-snow">${panel.title}</h2>
      </div>

      <div className="space-y-4">
        ${panel.rows.map((row) => html`
          <div className="glass-card rounded-[1.5rem] border border-snow/10 bg-snow/[0.04] p-5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-base font-bold text-snow">${row.name}</p>
                <p className="mt-1 text-sm text-mist">${row.tier} · ${row.owner}</p>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <span className="glass-chip rounded-full border border-snow/10 bg-snow/[0.05] px-3 py-1 text-sm text-mist">
                  ${row.usage}
                </span>
                <span className="rounded-full border border-cyan/20 bg-cyan/10 px-3 py-1 text-[11px] font-bold uppercase tracking-[0.18em] text-cyan">
                  ${row.status}
                </span>
              </div>
            </div>
          </div>
        `)}
      </div>
    </div>
  `;
}

function DashboardActivityPanel({ panel }) {
  return html`
    <div className="glass-panel rounded-[2rem] border border-snow/10 p-6 shadow-glow sm:p-8">
      <div className="mb-6">
        <p className="text-sm font-bold uppercase tracking-[0.24em] text-cyan/80">${panel.eyebrow}</p>
        <h2 className="mt-2 font-display text-3xl text-snow">${panel.title}</h2>
      </div>

      <div className="space-y-4">
        ${panel.items.map((item) => html`
          <div className="glass-card rounded-[1.45rem] border border-snow/10 bg-snow/[0.04] p-4">
            <div className="flex items-start gap-3">
              <span className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full bg-cyan"></span>
              <div>
                <p className="text-sm font-semibold text-snow">${item.title}</p>
                <p className="mt-2 text-sm text-mist">${item.meta}</p>
              </div>
            </div>
          </div>
        `)}
      </div>
    </div>
  `;
}

function DashboardWorkspace({ t, activeAudience, onSelectAudience, dashboardContent, isRefreshing }) {
  const activeView = dashboardContent[activeAudience];

  return html`
    <section className="mt-6 grid gap-6 xl:grid-cols-[1.12fr,0.88fr]">
      <div className="glass-panel rounded-[2rem] border border-snow/10 p-6 shadow-glow sm:p-8">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.24em] text-cyan/80">${activeView.eyebrow}</p>
            <h2 className="mt-2 max-w-3xl font-display text-3xl text-snow">${activeView.title}</h2>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-mist">${activeView.description}</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <span className="glass-chip rounded-full border border-cyan/20 bg-cyan/10 px-4 py-2 text-sm font-semibold text-cyan">
              ${activeView.badge}
            </span>
            ${
              isRefreshing
                ? html`
                    <span className="glass-chip rounded-full border border-snow/10 bg-snow/[0.05] px-4 py-2 text-xs font-bold uppercase tracking-[0.22em] text-mist">
                      ${t("processing")}
                    </span>
                  `
                : null
            }
          </div>
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          ${dashboardAudienceViews.map((audience) => {
            const isActive = audience.id === activeAudience;
            return html`
              <button
                key=${audience.id}
                className=${`glass-chip rounded-full px-4 py-2 text-sm font-semibold transition ${
                  isActive
                    ? "border border-cyan/25 bg-cyan/12 text-cyan"
                    : "border border-snow/10 bg-snow/[0.04] text-mist hover:border-cyan/30 hover:text-snow"
                }`}
                onClick=${() => onSelectAudience(audience.id)}
              >
                ${t(audience.labelKey)}
              </button>
            `;
          })}
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          ${activeView.stats.map((stat) => html`<${DashboardStatCard} key=${stat.label} stat=${stat} />`)}
        </div>

        <div className="mt-6 glass-card rounded-[1.75rem] border border-snow/10 bg-panel p-6 shadow-neon">
          <p className="text-sm font-bold uppercase tracking-[0.24em] text-cyan/80">${activeView.spotlight.eyebrow}</p>
          <h3 className="mt-2 font-display text-2xl text-snow">${activeView.spotlight.title}</h3>
          <p className="mt-3 text-sm leading-7 text-mist">${activeView.spotlight.description}</p>
          <div className="mt-5 grid gap-3">
            ${activeView.spotlight.bullets.map((bullet) => html`
              <div className="glass-card rounded-[1.25rem] border border-snow/10 bg-snow/[0.03] px-4 py-3">
                <p className="text-sm text-snow/88">${bullet}</p>
              </div>
            `)}
          </div>
        </div>
      </div>

      <aside>
        <${DashboardBoard} board=${activeView.board} />
      </aside>
    </section>

    <section className="mt-6 grid gap-6 xl:grid-cols-[1.04fr,0.96fr]">
      <${DashboardRecordsPanel} panel=${activeView.records} />
      <${DashboardActivityPanel} panel=${activeView.activity} />
    </section>
  `;
}

function OptimizerWorkspace({
  t,
  candidateCount,
  loading,
  error,
  onCandidateCountChange,
  onOptimize,
  onClearError,
  loadingMessages,
  result,
  topScore,
  pageTranslationLanguage,
  translateContent,
}) {
  return html`
    <section className="mt-6 grid gap-6 xl:grid-cols-[1.12fr,0.88fr]">
      <${PromptComposer}
        t=${t}
        candidateCount=${candidateCount}
        loading=${loading}
        error=${error}
        onCandidateCountChange=${onCandidateCountChange}
        onOptimize=${onOptimize}
        onClearError=${onClearError}
      />

      <aside className="glass-panel rounded-[2rem] border border-snow/10 p-6 shadow-glow sm:p-8">
        <div className="mb-6">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.24em] text-cyan/80">${t("workflow")}</p>
            <h2 className="mt-2 font-display text-3xl text-snow">${t("optimizationPipeline")}</h2>
          </div>
        </div>

        <div className="space-y-4">
          ${workflowSteps.map(
            ({ titleKey, copyKey }, index) => html`
              <div className="glass-card rounded-[1.6rem] border border-line bg-panelSoft/85 p-5">
                <div className="mb-2 flex items-center gap-3">
                  <span className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-cyan to-aqua text-sm font-bold text-abyss">
                    ${index + 1}
                  </span>
                  <h3 className="text-lg font-bold text-snow">${t(titleKey)}</h3>
                </div>
                <p className="text-sm leading-7 text-mist">${t(copyKey)}</p>
              </div>
            `
          )}
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          ${featureCards.map(
            ([titleKey, copyKey]) => html`
              <div className="glass-card rounded-[1.5rem] border border-snow/10 bg-snow/[0.04] p-5">
                <h3 className="text-base font-bold text-snow">${t(titleKey)}</h3>
                <p className="mt-2 text-sm leading-7 text-mist">${t(copyKey)}</p>
              </div>
            `
          )}
        </div>
      </aside>
    </section>

    <section className="mt-6 grid gap-6 xl:grid-cols-[1.04fr,0.96fr]">
      <div className="glass-panel rounded-[2rem] border border-snow/10 p-6 shadow-glow sm:p-8">
        <div className="mb-4 flex items-center justify-between gap-3">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.24em] text-cyan/80">${t("bestResponse")}</p>
            <h2 className="mt-2 font-display text-3xl text-snow">${t("highestScoringOutput")}</h2>
          </div>
          <span
            className=${`glass-chip rounded-full px-4 py-2 text-sm font-bold ${
              loading
                ? "border border-cyan/25 bg-cyan/10 text-cyan"
                : result
                  ? "border border-teal/25 bg-teal/10 text-teal"
                  : "border border-snow/10 bg-snow/[0.05] text-mist"
            }`}
          >
            ${loading ? t("processing") : result ? t("ready") : t("waiting")}
          </span>
        </div>

        <div className="glass-card min-h-[280px] rounded-[1.75rem] border border-snow/10 bg-panel p-6 shadow-neon">
          ${
            loading
              ? html`
                  <div className="space-y-4">
                    <div className="h-4 w-40 rounded-full bg-cyan/20"></div>
                    <div className="h-4 w-full rounded-full bg-snow/8"></div>
                    <div className="h-4 w-11/12 rounded-full bg-snow/8"></div>
                    <div className="h-4 w-10/12 rounded-full bg-snow/8"></div>
                    <div className="h-4 w-8/12 rounded-full bg-snow/8"></div>
                  </div>
                `
              : result
                ? html`
                    <div className="glass-chip mb-3 inline-flex items-center gap-2 rounded-full border border-cyan/20 bg-cyan/8 px-4 py-2 text-xs font-bold uppercase tracking-[0.26em] text-cyan">
                      ${t("bestCandidate")}${topScore ? ` · ${topScore.toFixed(1)}` : ""}
                    </div>
                    <p className="text-base leading-8 text-snow/88">
                      ${pageTranslationLanguage ? translateContent(result.best_response) : result.best_response}
                    </p>
                  `
                : html`<p className="text-base leading-8 text-mist">${t("runOptimizerToSeeStrongest")}</p>`
          }
        </div>
      </div>

      <div className="glass-panel rounded-[2rem] border border-snow/10 p-6 shadow-glow sm:p-8">
        <div className="mb-4">
          <p className="text-sm font-bold uppercase tracking-[0.24em] text-cyan/80">${t("candidates")}</p>
          <h2 className="mt-2 font-display text-3xl text-snow">${t("scoredAlternatives")}</h2>
          <p className="mt-2 text-sm leading-7 text-mist">${t("candidatesRemainOriginal")}</p>
        </div>

        <div className="space-y-4">
          ${
            loading
              ? loadingMessages.map(
                  (message) => html`<${LoadingCard} key=${message} title=${message} />`
                )
              : result
                ? result.candidates.map((candidate, index) =>
                    html`<${CandidateCard}
                      key=${`${candidate.score}-${index}`}
                      candidate=${candidate}
                      index=${index}
                      bestScore=${result.candidates[0].score}
                      t=${t}
                      translateContent=${pageTranslationLanguage ? translateContent : (text) => text}
                    />`
                  )
                : html`<div className="glass-card rounded-[1.75rem] border border-dashed border-snow/10 bg-panel p-6 text-sm leading-7 text-mist">
                    ${t("candidateScoresAppear")}
                  </div>`
          }
        </div>
      </div>
    </section>
  `;
}

function App() {
  const [activeWorkspace, setActiveWorkspace] = useState("dashboard");
  const [activeAudience, setActiveAudience] = useState("internal");
  const [candidateCount, setCandidateCount] = useState(DEFAULT_CANDIDATE_COUNT);
  const [dashboardContent, setDashboardContent] = useState(() => getDashboardContent(DEFAULT_PAGE_LANGUAGE));
  const [isDashboardRefreshing, setIsDashboardRefreshing] = useState(false);
  const [pageLanguageCode, setPageLanguageCode] = useState(DEFAULT_PAGE_LANGUAGE);
  const [isLanguageMenuOpen, setIsLanguageMenuOpen] = useState(false);
  const [runtimeMode, setRuntimeMode] = useState("simulation");
  /** @type {[OptimizeResult | null, Function]} */
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const languageMenuRef = useRef(null);

  const selectedPageLanguage = getLanguageOption(pageLanguageCode) ?? getLanguageOption(DEFAULT_PAGE_LANGUAGE);
  const pageTranslationLanguage =
    selectedPageLanguage?.code === DEFAULT_PAGE_LANGUAGE ? null : selectedPageLanguage;
  const uiLanguageCode = pageTranslationLanguage?.code ?? "es";
  const t = (key, params = {}) => getUiText(key, uiLanguageCode, params);
  const translateContent = (text) => translateDynamicText(text, pageTranslationLanguage);

  const currentPageLanguageCode = pageTranslationLanguage?.code ?? DEFAULT_PAGE_LANGUAGE;
  const selectedPageLanguageLabel = getLanguageDisplayLabel(currentPageLanguageCode, uiLanguageCode);
  const pageLanguageBadge = getLanguageBadge(currentPageLanguageCode);
  const loadingMessages = loadingMessageKeys.map((key) => t(key));
  const currentStatusLabel = loading
    ? t("optimizingNow")
    : result
      ? t("readyToReview")
      : t("waitingForPrompt");
  const isDashboardWorkspace = activeWorkspace === "dashboard";
  const heroTitle = isDashboardWorkspace ? t("dashboardTitle") : t("heroTitle");
  const heroDescription = isDashboardWorkspace ? t("dashboardDescription") : t("heroDescription");
  const heroStatusItems = isDashboardWorkspace
    ? [
        { label: t("mode"), value: runtimeMode === "live" ? t("liveApi") : t("simulationOnly") },
        { label: t("workspaceView"), value: activeAudience === "internal" ? t("internalView") : t("clientView") },
        { label: t("subscribersLabel"), value: t("subscribersValue") },
        { label: t("status"), value: t("dashboardStatus") },
      ]
    : [
        { label: t("mode"), value: runtimeMode === "live" ? t("liveApi") : t("simulationOnly") },
        { label: t("page"), value: selectedPageLanguageLabel },
        { label: t("output"), value: formatCandidateCount(candidateCount, uiLanguageCode) },
        { label: t("status"), value: currentStatusLabel },
      ];

  const topScore = result?.candidates?.[0]?.score ?? null;

  useEffect(() => {
    document.title = t("appTitle");
  }, [uiLanguageCode]);

  useEffect(() => {
    let isMounted = true;

    const loadRuntimeMode = async () => {
      try {
        const response = await fetch("/app-config");
        if (!response.ok) {
          return;
        }

        const data = await response.json();
        if (isMounted) {
          setRuntimeMode(data.mode === "live" ? "live" : "simulation");
        }
      } catch {
        // Ignore config fetch errors and keep the default mode label.
      }
    };

    loadRuntimeMode();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;
    setDashboardContent(getDashboardContent(uiLanguageCode));

    const loadDashboard = async () => {
      setIsDashboardRefreshing(true);

      try {
        const response = await fetch(`/dashboard?language=${encodeURIComponent(currentPageLanguageCode)}`);
        if (!response.ok) {
          return;
        }

        const data = await response.json();
        if (isMounted) {
          setDashboardContent(data);
        }
      } catch {
        // Keep the local fallback content if the dashboard endpoint is unavailable.
      } finally {
        if (isMounted) {
          setIsDashboardRefreshing(false);
        }
      }
    };

    loadDashboard();

    return () => {
      isMounted = false;
    };
  }, [currentPageLanguageCode, uiLanguageCode]);

  useEffect(() => {
    if (!isLanguageMenuOpen) {
      return undefined;
    }

    const handlePointerDown = (event) => {
      if (languageMenuRef.current && !languageMenuRef.current.contains(event.target)) {
        setIsLanguageMenuOpen(false);
      }
    };

    window.addEventListener("pointerdown", handlePointerDown);

    return () => {
      window.removeEventListener("pointerdown", handlePointerDown);
    };
  }, [isLanguageMenuOpen]);

  const handleOptimize = async (nextPrompt) => {
    if (!nextPrompt.trim()) {
      setError(t("addPromptBeforeRun"));
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("/optimize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: nextPrompt, candidate_count: candidateCount }),
      });

      if (!response.ok) {
        throw new Error(await getApiErrorMessage(response));
      }

      /** @type {OptimizeResult} */
      const data = await response.json();
      React.startTransition(() => {
        setResult(data);
      });
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "La solicitud del optimizador fallo.");
    } finally {
      setLoading(false);
    }
  };

  const handlePageLanguageSelect = (languageCode) => {
    setPageLanguageCode(languageCode);
    setIsLanguageMenuOpen(false);
    setError("");
  };

  const handleCandidateCountChange = (nextCandidateCount) => {
    const normalizedCandidateCount = clampCandidateCount(nextCandidateCount);
    if (normalizedCandidateCount === candidateCount) {
      return;
    }
    setCandidateCount(normalizedCandidateCount);
    setResult(null);
    setError("");
  };

  return html`
    <main className="relative overflow-hidden px-4 py-6 sm:px-6 lg:px-8">
      <div className="pointer-events-none absolute inset-x-0 top-0 mx-auto h-[460px] max-w-6xl rounded-full bg-cyan/6 blur-2xl"></div>
      <div className="pointer-events-none absolute right-0 top-24 h-[360px] w-[360px] rounded-full bg-snow/[0.02] blur-2xl"></div>
      <div className="pointer-events-none absolute bottom-10 left-10 h-[280px] w-[280px] rounded-full bg-teal/8 blur-2xl"></div>
      <div className="relative mx-auto max-w-7xl">
        <section className="hero-gradient rounded-[2rem] border border-snow/10 p-6 shadow-glow sm:p-8 lg:p-10">
          <div className="flex items-start justify-between gap-4">
            <div className="glass-chip inline-flex items-center gap-2 rounded-full border border-cyan/20 bg-cyan/8 px-4 py-2 text-xs font-bold uppercase tracking-[0.34em] text-cyan">
              ${t("appTitle")}
            </div>

            <div className="relative shrink-0" ref=${languageMenuRef}>
              <button
                className="glass-chip inline-flex items-center gap-2 rounded-full border border-snow/12 bg-snow/[0.05] px-3 py-2 text-xs font-black uppercase tracking-[0.24em] text-snow transition hover:border-cyan/40 hover:text-cyan"
                aria-haspopup="menu"
                aria-expanded=${isLanguageMenuOpen}
                onClick=${() => setIsLanguageMenuOpen((open) => !open)}
              >
                <span className="text-cyan">${pageLanguageBadge}</span>
                <svg
                  className=${`h-3.5 w-3.5 text-mist transition ${isLanguageMenuOpen ? "rotate-180" : ""}`}
                  viewBox="0 0 20 20"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  aria-hidden="true"
                >
                  <path d="M5 7.5 10 12.5 15 7.5" strokeLinecap="round" strokeLinejoin="round"></path>
                </svg>
              </button>

              ${
                isLanguageMenuOpen
                  ? html`
                      <div className="glass-menu absolute right-0 top-full z-20 mt-3 w-64 overflow-hidden rounded-[1.4rem] border border-snow/12 bg-panel/95 shadow-glow">
                        <div className="border-b border-snow/10 px-4 py-3">
                          <p className="text-[11px] font-bold uppercase tracking-[0.24em] text-cyan">
                            ${t("page")} · ${t("language")}
                          </p>
                          <p className="mt-1 text-sm font-semibold text-snow">${selectedPageLanguageLabel}</p>
                        </div>
                        <div className="p-2">
                          ${languageOptions.map((language) => {
                            const isActive = language.code === currentPageLanguageCode;

                            return html`
                              <button
                                key=${language.code}
                                className=${`glass-card flex w-full items-center justify-between rounded-[1rem] px-3 py-3 text-left transition ${
                                  isActive
                                    ? "bg-cyan/12 text-snow"
                                    : "text-snow/82 hover:bg-snow/[0.05] hover:text-snow"
                                }`}
                                onClick=${() => handlePageLanguageSelect(language.code)}
                              >
                                <div>
                                  <p className="text-sm font-semibold">
                                    ${getLanguageDisplayLabel(language.code, uiLanguageCode)}
                                  </p>
                                  <p className="mt-1 text-[11px] font-bold uppercase tracking-[0.2em] text-mist">
                                    ${language.code.toUpperCase()}
                                  </p>
                                </div>
                                <span className=${`text-xs font-bold uppercase tracking-[0.2em] ${
                                  isActive ? "text-cyan" : "text-transparent"
                                }`}>
                                  ${t("selected")}
                                </span>
                              </button>
                            `;
                          })}
                        </div>
                      </div>
                    `
                  : null
              }
            </div>
          </div>

          <div className="mt-6">
            <div className="max-w-4xl">
              <h1 className="max-w-3xl font-display text-4xl leading-tight text-snow sm:text-5xl xl:text-6xl">
                ${heroTitle}
              </h1>
              <p className="mt-5 max-w-2xl text-base leading-8 text-mist sm:text-lg">
                ${heroDescription}
              </p>
              <${WorkspaceSwitch}
                t=${t}
                activeWorkspace=${activeWorkspace}
                onSelectWorkspace=${setActiveWorkspace}
              />
              <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                ${heroStatusItems.map(
                  (item) => html`
                    <div className="glass-card rounded-[1.35rem] border border-snow/10 bg-snow/[0.04] px-4 py-4 shadow-glow">
                      <p className="text-[11px] font-bold uppercase tracking-[0.22em] text-cyan/80">${item.label}</p>
                      <p className="mt-2 text-sm font-semibold text-snow">${item.value}</p>
                    </div>
                  `
                )}
              </div>
            </div>
          </div>
        </section>

        ${
          isDashboardWorkspace
            ? html`
                <${DashboardWorkspace}
                  t=${t}
                  activeAudience=${activeAudience}
                  onSelectAudience=${setActiveAudience}
                  dashboardContent=${dashboardContent}
                  isRefreshing=${isDashboardRefreshing}
                />
              `
            : html`
                <${OptimizerWorkspace}
                  t=${t}
                  candidateCount=${candidateCount}
                  loading=${loading}
                  error=${pageTranslationLanguage ? translateContent(error) : error}
                  onCandidateCountChange=${handleCandidateCountChange}
                  onOptimize=${handleOptimize}
                  onClearError=${() => setError("")}
                  loadingMessages=${loadingMessages}
                  result=${result}
                  topScore=${topScore}
                  pageTranslationLanguage=${pageTranslationLanguage}
                  translateContent=${translateContent}
                />
              `
        }
      </div>
    </main>
  `;
}

createRoot(document.getElementById("root")).render(html`<${App} />`);
