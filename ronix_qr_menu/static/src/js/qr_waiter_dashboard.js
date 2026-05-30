/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

const POLL_INTERVAL = 10000; // 10 seconds

export const qrWaiterDashboardService = {
    dependencies: ["action"],

    start(env, { action }) {
        let lastKnownIds = new Set();
        let pollTimer = null;
        let isPolling = false;

        let globalAudio = null;
        let globalStopTimeout = null;
        let audioUnlocked = false;

        // Only poll when we're on the waiter call list view
        function shouldPoll() {
            const currentController = action.currentController;
            if (!currentController || !currentController.action) return false;
            
            // Poll if the current view's model is waiter call
            return currentController.action.res_model === "qr.menu.waiter.call";
        }

        async function poll() {
            if (!shouldPoll()) {
                return;
            }

            console.log("[QR Menu] Yeni garson çağrıları kontrol ediliyor... (10sn)");

            try {
                const calls = await rpc('/qr_menu/check_calls', {});

                if (Array.isArray(calls)) {
                    console.log(`[QR Menu] Sunucudan ${calls.length} adet bekleyen çağrı alındı.`);
                    if (calls.length > 0) {
                        console.log(`[QR Menu] Bekleyen Çağrılar Detayı:`, calls);
                    }
                    const currentIds = new Set(calls.map(c => c.id));

                    // Find new calls
                    for (const call of calls) {
                        if (!lastKnownIds.has(call.id)) {
                            console.log(`[QR Menu] Çağrı ekrana yansıtılıyor: Masa ${call.table_name}`);
                            showCallPopup(call, action);
                        }
                    }

                    lastKnownIds = currentIds;
                }
            } catch (e) {
                // Silently ignore polling errors
            }
        }

        const showCallPopup = (call, actionService) => {
            let container = document.getElementById("qr_menu_waiter_alerts_container");
            if (!container) {
                container = document.createElement("div");
                container.id = "qr_menu_waiter_alerts_container";
                container.style.cssText = "position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:999999; display:flex; flex-direction:column; align-items:center; gap:15px; width:95%; max-width:550px;";
                document.body.appendChild(container);
            }

            playGlobalAudio();

            const popup = document.createElement("div");
            popup.className = "bg-white border rounded shadow-lg overflow-hidden w-100 qr-call-popup";
            popup.style.animation = "popupEnterLean 0.4s ease-out";

            if (!document.getElementById("qr_menu_alert_styles")) {
                const style = document.createElement("style");
                style.id = "qr_menu_alert_styles";
                style.innerHTML = `
                    @keyframes popupEnterLean { from { transform: translateY(-30px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
                    @keyframes bounceIn { 0% { opacity: 0; transform: scale(0.3); } 50% { opacity: 1; transform: scale(1.05); } 70% { transform: scale(0.9); } 100% { transform: scale(1); } }
                `;
                document.head.appendChild(style);
            }

            const typeLabels = {
                'waiter': 'Garson Çağrısı',
                'bill': 'Hesap İsteği',
                'water': 'Su İsteği',
                'custom': 'Özel İstek',
            };

            const callTypeIcon = {
                'waiter': 'fa-user',
                'bill': 'fa-money',
                'water': 'fa-tint',
                'custom': 'fa-comment',
            };

            const typeName = typeLabels[call.call_type] || call.call_type;
            const typeIcon = callTypeIcon[call.call_type] || 'fa-bell';

            popup.innerHTML = `
                <div class="bg-warning text-dark px-4 py-3 d-flex align-items-center justify-content-between">
                    <div>
                        <h4 class="mb-0 fw-bold"><i class="fa ${typeIcon} me-2"></i>${typeName.toUpperCase()}</h4>
                        <small class="fw-bold">${call.restaurant_name}</small>
                    </div>
                </div>
                <div class="p-4">
                    <div class="mb-3">
                        <div class="text-dark fw-bolder mb-1">Masa</div>
                        <div class="h4 mb-0 fw-bold text-primary">${call.table_name}</div>
                    </div>
                    ${call.custom_message ? `
                    <div class="mb-4 border-start border-danger border-4 ps-2 py-1" style="background: #fff8f8;">
                        <div class="text-danger fw-bolder">Not / Özel İstek</div>
                        <div class="fw-bold small text-muted">${call.custom_message}</div>
                    </div>` : ''}
                    <div class="d-flex gap-3 mt-4">
                        <button class="btn btn-lg btn-success flex-grow-1 btn-dismiss fw-bold text-white"><i class="fa fa-check me-2"></i>GÖRDÜM / TAMAM</button>
                    </div>
                </div>
            `;

            container.appendChild(popup);

            const dismissPopup = async () => {
                rpc("/qr_menu/complete_call", { call_id: call.id }).catch(() => { });
                if (container.childNodes.length <= 1 && globalAudio) {
                    globalAudio.pause();
                }
                popup.style.cssText += "transition: opacity 0.3s, transform 0.3s; opacity: 0; transform: translateY(-20px);";
                
                // Refresh list view to immediately show state change
                const controller = actionService.currentController;
                if (controller) {
                    try {
                        if (controller.model && controller.model.load) await controller.model.load();
                        else if (controller.component && controller.component.model && controller.component.model.load) await controller.component.model.load();
                        else if (controller.reload) await controller.reload();
                    } catch (e) { }
                }

                setTimeout(() => {
                    popup.remove();
                    if (container.childNodes.length === 0) container.remove();
                }, 300);
            };

            popup.querySelector('.btn-dismiss').addEventListener('click', dismissPopup);
        };

        function playGlobalAudio() {
            if (!globalAudio) {
                globalAudio = new Audio("/ronix_qr_menu/static/src/sound/ring_sound.mp3");
                globalAudio.loop = true;
            }

            console.log("[QR Menu Audio] Attempting to play...");
            globalAudio.currentTime = 0;
            globalAudio.play().then(() => {
                console.log("[QR Menu Audio] Playback SUCCESS");
                audioUnlocked = true;
                const unlockBanner = document.getElementById('qr_menu_audio_unlock_banner');
                if (unlockBanner) unlockBanner.classList.add('d-none');
            }).catch((error) => {
                console.warn("[QR Menu Audio] Playback BLOCKED", error.name);
                showUnlockBanner();
            });

            if (globalStopTimeout) clearTimeout(globalStopTimeout);
            // Play for 20 seconds as requested
            globalStopTimeout = setTimeout(() => {
                if (globalAudio) globalAudio.pause();
            }, 20000);
        }

        function showUnlockBanner() {
            if (document.getElementById('qr_menu_audio_unlock_banner')) return;
            const banner = document.createElement('div');
            banner.id = 'qr_menu_audio_unlock_banner';
            banner.style.cssText = "display:none;";
            banner.innerHTML = '<i class="fa fa-volume-up fa-2x"></i> <div>GARSON ÇAĞRISI SESİNİ AKTİF ETMEK İÇİN TIKLAYIN<br><small style="font-size:0.7rem;opacity:0.8;">Tarayıcı güvenliği için ilk tıklama gereklidir.</small></div>';
            banner.onclick = () => {
                primeAudioInternal();
                banner.remove();
            };
            document.body.appendChild(banner);
        }

        function primeAudioInternal() {
            if (!globalAudio) {
                globalAudio = new Audio("/ronix_qr_menu/static/src/sound/ring_sound.mp3");
                globalAudio.loop = true;
            }
            globalAudio.volume = 0;
            globalAudio.play().then(() => {
                console.log("[QR Menu Audio] System Unlocked via manual click");
                globalAudio.pause();
                globalAudio.volume = 1;
                audioUnlocked = true;
            }).catch(e => console.error("[QR Menu Audio] Failed to unlock:", e));
        }

        function initAudio() {
            // Check if blocked on load (silent test)
            const test = new Audio("data:audio/wav;base64,UklGRigAAABXQVZFRm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAP8A/wD/");
            test.play().then(() => {
                audioUnlocked = true;
                console.log("[QR Menu Audio] Autoplay is already allowed.");
            }).catch(() => {
                console.warn("[QR Menu Audio] Autoplay blocked. Waiting for interaction.");
            });

            const primeOnAny = (event) => {
                if (audioUnlocked) return;
                primeAudioInternal();
                if (audioUnlocked) {
                    const banner = document.getElementById('qr_menu_audio_unlock_banner');
                    if (banner) banner.remove();
                    ['mousedown', 'keydown', 'touchstart'].forEach(e => document.removeEventListener(e, primeOnAny));
                }
            };
            ['mousedown', 'keydown', 'touchstart'].forEach(e => document.addEventListener(e, primeOnAny));
        }

        // Initialize audio mechanisms
        initAudio();

        // Start polling unconditionally (poll function will check if it should run)
        pollTimer = setInterval(poll, POLL_INTERVAL);
        poll(); // Initial check
    },
};

registry.category("services").add("qrWaiterDashboard", qrWaiterDashboardService);
