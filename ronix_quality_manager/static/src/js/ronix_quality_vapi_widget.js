/** @odoo-module **/

const LOG_PREFIX = "[ronix_quality_manager.vapi]";
const WIDGET_SCRIPT_URL = "https://unpkg.com/@vapi-ai/client-sdk-react/dist/embed/widget.umd.js";
const WIDGET_ID = "ronix-quality-vapi-widget";
const WIDGET_FALLBACK_ID = "ronix-quality-vapi-fallback";

function logDebug(config) {
    window.ronixQualityVapiDebug = config;
    console.groupCollapsed(`${LOG_PREFIX} debug`);
    console.log("page", window.location.href);
    console.log("requestPath", config.requestPath);
    console.log("routeCandidates", config.routeCandidates);
    console.log("matchedButtonId", config.matchedButtonId);
    console.log("matchedButtonName", config.matchedButtonName);
    console.log("matchedButtonRoute", config.matchedButtonRoute);
    console.log("locationId", config.locationId);
    console.log("locationName", config.locationName);
    console.log("mode", config.mode);
    console.log("vapiEnabled", config.vapiEnabled);
    console.log("hasPublicKey", config.hasPublicKey);
    console.log("hasAssistantId", config.hasAssistantId);
    console.groupEnd();
}

function ensureErrorHooks() {
    if (window.__ronixQualityVapiErrorHookInstalled) {
        return;
    }
    window.__ronixQualityVapiErrorHookInstalled = true;

    window.addEventListener("error", (event) => {
        const filename = event.filename || "";
        if (filename.includes("vapi") || String(event.message || "").includes("Cache")) {
            console.error(LOG_PREFIX, "window.error", {
                message: event.message,
                filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error,
            });
        }
    });

    window.addEventListener("unhandledrejection", (event) => {
        const reason = event.reason;
        const reasonText = String(reason?.message || reason || "");
        if (reasonText.includes("Cache") || reasonText.includes("vapi")) {
            console.error(LOG_PREFIX, "unhandledrejection", reason);
        }
    });

    if ("serviceWorker" in navigator) {
        navigator.serviceWorker.getRegistrations().then((registrations) => {
            console.log(
                LOG_PREFIX,
                "serviceWorkers",
                registrations.map((registration) => {
                    const worker = registration.active || registration.installing || registration.waiting;
                    return worker ? worker.scriptURL : null;
                })
            );
        }).catch((error) => {
            console.warn(LOG_PREFIX, "serviceWorker inspection failed", error);
        });
    }
}

function applyWidgetAttributes(widget, config) {
    const attributes = {
        "public-key": config.apiKey,
        "assistant-id": config.assistantId,
        "mode": config.mode,
        "theme": "light",
        "position": "bottom-right",
        "size": "compact",
        "radius": "large",
        "base-color": "#F8FAFC",
        "accent-color": "#0F766E",
        "button-base-color": "#0F172A",
        "button-accent-color": "#F8FAFC",
        "main-label": config.ctaTitle || "Call AI",
        "start-button-text": "Start Voice",
        "end-button-text": "End",
        "empty-chat-message": config.ctaSubtitle || "Send a message to start",
        "empty-voice-message": "Start a voice conversation",
        "voice-show-transcript": "true",
    };

    Object.entries(attributes).forEach(([name, value]) => {
        if (value) {
            widget.setAttribute(name, value);
        }
    });
}

function bindWidgetEvents(widget) {
    widget.addEventListener("call-start", (event) => {
        console.log(LOG_PREFIX, "call-start", event.detail);
    });
    widget.addEventListener("call-end", (event) => {
        console.log(LOG_PREFIX, "call-end", event.detail);
    });
    widget.addEventListener("message", (event) => {
        console.log(LOG_PREFIX, "message", event.detail);
    });
    widget.addEventListener("error", (event) => {
        console.error(LOG_PREFIX, "widget.error", event.detail);
    });
}

function styleWidgetHost(widget) {
    Object.assign(widget.style, {
        position: "fixed",
        right: "24px",
        bottom: "24px",
        zIndex: "2147483000",
        display: "block",
        width: "72px",
        height: "72px",
        overflow: "visible",
        visibility: "visible",
        opacity: "1",
        pointerEvents: "auto",
    });
}

function removeFallbackButton() {
    const fallbackButton = document.getElementById(WIDGET_FALLBACK_ID);
    if (fallbackButton) {
        fallbackButton.remove();
    }
}

function cleanupMountedWidget() {
    const existingWidget = document.getElementById(WIDGET_ID);
    if (existingWidget) {
        existingWidget.remove();
        console.log(LOG_PREFIX, "Existing widget removed");
    }
    removeFallbackButton();
}

function findLauncherTrigger(widget) {
    const selectors = [
        "button",
        "[role='button']",
        "[part='button']",
        "[part='trigger']",
        "[aria-label*='chat' i]",
        "[aria-label*='call' i]",
        "[aria-label*='voice' i]",
    ];

    if (widget.shadowRoot) {
        for (const selector of selectors) {
            const element = widget.shadowRoot.querySelector(selector);
            if (element) {
                return element;
            }
        }
    }

    for (const selector of selectors) {
        const element = widget.querySelector(selector);
        if (element) {
            return element;
        }
    }
    return null;
}

function clickWidgetLauncher(widget) {
    const trigger = findLauncherTrigger(widget);
    if (trigger) {
        trigger.click();
        console.log(LOG_PREFIX, "Fallback button clicked widget trigger");
        return true;
    }
    console.warn(LOG_PREFIX, "Widget trigger not found");
    return false;
}

function ensureFallbackButton(widget, config) {
    if (document.getElementById(WIDGET_FALLBACK_ID)) {
        return;
    }

    const fallbackButton = document.createElement("button");
    fallbackButton.id = WIDGET_FALLBACK_ID;
    fallbackButton.type = "button";
    fallbackButton.className = "ham-vapi-fallback-button";
    fallbackButton.innerHTML = `
        <span class="ham-vapi-fallback-badge">AI</span>
        <span class="ham-vapi-fallback-copy">${config.ctaTitle || "Call AI"}</span>
    `;
    fallbackButton.addEventListener("click", () => {
        if (!clickWidgetLauncher(widget)) {
            console.log(LOG_PREFIX, "Retrying widget mount via fallback");
            widget.remove();
            mountWidget(config);
        }
    });
    document.body.appendChild(fallbackButton);
    console.warn(LOG_PREFIX, "Fallback launcher rendered");
}

function inspectWidgetVisibility(widget, config) {
    window.setTimeout(() => {
        const rect = widget.getBoundingClientRect();
        const shadowChildCount = widget.shadowRoot ? widget.shadowRoot.childElementCount : 0;
        const trigger = findLauncherTrigger(widget);
        const debugPayload = {
            rect: {
                width: rect.width,
                height: rect.height,
                top: rect.top,
                left: rect.left,
            },
            hasShadowRoot: Boolean(widget.shadowRoot),
            shadowChildCount,
            hasTrigger: Boolean(trigger),
            computed: {
                display: window.getComputedStyle(widget).display,
                visibility: window.getComputedStyle(widget).visibility,
                opacity: window.getComputedStyle(widget).opacity,
                zIndex: window.getComputedStyle(widget).zIndex,
            },
        };
        console.log(LOG_PREFIX, "Widget visibility inspection", debugPayload);
        if (!trigger || !shadowChildCount || rect.width === 0 || rect.height === 0) {
            ensureFallbackButton(widget, config);
        } else {
            removeFallbackButton();
        }
    }, 1200);
}

function mountWidget(config) {
    cleanupMountedWidget();

    const widget = document.createElement("vapi-widget");
    widget.id = WIDGET_ID;
    applyWidgetAttributes(widget, config);
    bindWidgetEvents(widget);
    styleWidgetHost(widget);
    document.body.appendChild(widget);
    console.log(LOG_PREFIX, "Widget mounted", {
        mode: config.mode,
        ctaTitle: config.ctaTitle,
        ctaSubtitle: config.ctaSubtitle,
    });
    inspectWidgetVisibility(widget, config);
}

function ensureWidgetScript(config) {
    if (customElements.get("vapi-widget")) {
        console.log(LOG_PREFIX, "Vapi widget custom element already available");
        mountWidget(config);
        return;
    }

    const existingScript = document.querySelector('script[data-ronix-quality-vapi-widget="1"]');
    if (existingScript) {
        console.log(LOG_PREFIX, "Vapi widget script already requested", existingScript.src);
        existingScript.addEventListener("load", () => mountWidget(config), { once: true });
        existingScript.addEventListener("error", (event) => {
            console.error(LOG_PREFIX, "Existing Vapi widget script failed to load", event);
        }, { once: true });
        return;
    }

    const sdkScript = document.createElement("script");
    sdkScript.src = WIDGET_SCRIPT_URL;
    sdkScript.async = true;
    sdkScript.type = "text/javascript";
    sdkScript.dataset.ronixQualityVapiWidget = "1";
    sdkScript.addEventListener("load", () => {
        console.log(LOG_PREFIX, "Vapi widget script loaded", WIDGET_SCRIPT_URL);
        mountWidget(config);
    }, { once: true });
    sdkScript.addEventListener("error", (event) => {
        console.error(LOG_PREFIX, "Vapi widget script failed to load", {
            src: WIDGET_SCRIPT_URL,
            event,
        });
    }, { once: true });
    console.log(LOG_PREFIX, "Requesting Vapi widget script", WIDGET_SCRIPT_URL);
    document.head.appendChild(sdkScript);
}

function startRonixQualityVapiWidget() {
    const config = window.ronixQualityVapiWidgetConfig;
    if (!config) {
        return;
    }

    ensureErrorHooks();
    logDebug(config);

    if (!config.matchedButtonId) {
        console.warn(LOG_PREFIX, "No Ronix Quality button matched this page. Vapi widget will not load.");
        return;
    }
    if (!config.vapiEnabled) {
        console.warn(LOG_PREFIX, "Matched location has Vapi disabled. Widget will not load.");
        return;
    }
    if (!config.hasPublicKey || !config.hasAssistantId) {
        console.warn(LOG_PREFIX, "Matched location is missing Vapi credentials.", {
            hasPublicKey: config.hasPublicKey,
            hasAssistantId: config.hasAssistantId,
        });
        return;
    }

    ensureWidgetScript(config);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startRonixQualityVapiWidget, { once: true });
} else {
    startRonixQualityVapiWidget();
}
