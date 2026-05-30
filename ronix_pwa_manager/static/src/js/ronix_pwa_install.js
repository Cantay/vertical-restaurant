/** @odoo-module **/

function isStandaloneMode() {
    return window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
}

function isIos() {
    return /iphone|ipad|ipod/i.test(window.navigator.userAgent || "");
}

function bindRonixPwaInstall() {
    const root = document.querySelector("[data-ronix-pwa-install-root]");
    if (!root || isStandaloneMode()) {
        if (root) {
            root.hidden = true;
        }
        return;
    }

    const button = root.querySelector("[data-ronix-pwa-install-button]");
    const status = root.querySelector("[data-ronix-pwa-install-status]");
    if (!button || !status) {
        return;
    }

    let deferredPrompt = null;

    const setStatus = (message) => {
        status.hidden = !message;
        status.textContent = message || "";
    };

    const registerServiceWorker = async () => {
        const serviceWorkerUrl = root.dataset.serviceWorkerUrl;
        const scope = root.dataset.scope || "/";
        if (!serviceWorkerUrl || !("serviceWorker" in navigator)) {
            return;
        }
        try {
            await navigator.serviceWorker.register(serviceWorkerUrl, { scope });
        } catch (error) {
            window.console.warn("Ronix PWA service worker registration failed.", error);
        }
    };

    registerServiceWorker();

    window.addEventListener("beforeinstallprompt", (event) => {
        event.preventDefault();
        deferredPrompt = event;
        setStatus("");
    });

    window.addEventListener("appinstalled", () => {
        deferredPrompt = null;
        root.hidden = true;
    });

    if (isIos()) {
        setStatus("Safari > Paylaş > Ana Ekrana Ekle yolunu kullan.");
    }

    button.addEventListener("click", async () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            const result = await deferredPrompt.userChoice.catch(() => null);
            deferredPrompt = null;
            if (result && result.outcome === "accepted") {
                setStatus("");
            } else if (result) {
                setStatus("Yükleme iptal edildi.");
            }
            return;
        }

        if (isIos()) {
            setStatus("Safari > Paylaş > Ana Ekrana Ekle yolunu kullan.");
            return;
        }

        setStatus("Tarayıcı menüsünden Uygulamayı Yükle seçeneğini kullan.");
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindRonixPwaInstall);
} else {
    bindRonixPwaInstall();
}
