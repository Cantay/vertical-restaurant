/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export const backendNewOrderAlertService = {
    dependencies: ["action", "ui"],
    start(env, { action, ui }) {
        let lastCheckTime = null;
        let pollInterval = null;

        let globalAudio = null;
        let globalStopTimeout = null;
        let audioUnlocked = false;

        const isDebug = () => {
            return window.location.search.includes('ronix_debug=1') || window.location.search.includes('debug=assets');
        };

        const debugLog = (...args) => {
            if (isDebug()) {
                console.log("%c[Ronix Debug]", "color: #dc3545; font-weight: bold;", ...args);
            }
        };

        const checkNewOrders = async () => {
            debugLog("Checking for new orders... Last check:", lastCheckTime);
            
            try {
                const result = await rpc("/ronix_food_delivery/check_new_orders", { last_check_time: lastCheckTime });
                debugLog("RPC result:", result);
                
                if (result && result.orders && result.orders.length > 0) {
                    debugLog(`Found ${result.orders.length} new orders.`);
                    lastCheckTime = result.orders[result.orders.length - 1].date_order;

                    // Refresh list if on order pages
                    const currentController = action.currentController;
                    if (currentController && currentController.action) {
                        const actionName = currentController.action.name;
                        const actionId = currentController.action.xml_id || "";
                        
                        const isOrderPage = actionId === "ronix_food_delivery.action_food_orders" || 
                                           ["Yemek Siparişleri", "Siparişler", "Food Orders"].includes(actionName);
                        
                        if (isOrderPage) {
                            debugLog("Refreshing list...");
                            try {
                                if (currentController.model?.load) await currentController.model.load();
                                else if (currentController.component?.model?.load) await currentController.component.model.load();
                                else if (currentController.reload) await currentController.reload();
                            } catch (e) { 
                                debugLog("Refresh failed:", e);
                            }
                        }
                    }

                    result.orders.forEach(order => {
                        debugLog("Displaying popup for order:", order.name);
                        showOrderPopup(order, action);
                    });
                } else if (result && result.orders) {
                    debugLog("No new orders found.");
                } else {
                    debugLog("Unexpected RPC result format.");
                }
            } catch (error) {
                debugLog("RPC Error:", error);
            }
        };

        const playGlobalAudio = () => {
            if (!globalAudio) {
                globalAudio = new Audio("/ronix_food_delivery/static/src/sound/ring_sound.mp3");
                globalAudio.loop = true;
            }

            debugLog("Attempting to play audio. Unlocked:", audioUnlocked);
            globalAudio.currentTime = 0;
            globalAudio.volume = 1;
            globalAudio.play().then(() => {
                debugLog("Audio playback STARTED successfully.");
                audioUnlocked = true;
                const unlockBanner = document.getElementById('ronix_audio_unlock_banner');
                if (unlockBanner) unlockBanner.remove();
            }).catch((error) => {
                debugLog("Audio playback BLOCKED:", error.name);
                showUnlockBanner();
            });

            if (globalStopTimeout) clearTimeout(globalStopTimeout);
            globalStopTimeout = setTimeout(() => {
                if (globalAudio) {
                    debugLog("Auto-stopping audio after 40s.");
                    globalAudio.pause();
                }
            }, 40000);
        };

        const showUnlockBanner = () => {
            if (document.getElementById('ronix_audio_unlock_banner')) return;
            debugLog("Showing unlock banner.");
            const banner = document.createElement('div');
            banner.id = 'ronix_audio_unlock_banner';
            banner.style.cssText = "position:fixed; bottom:20px; right:20px; z-index:2147483647; background:#dc3545; color:white; padding:15px 20px; border-radius:8px; box-shadow:0 4px 15px rgba(0,0,0,0.3); font-weight:bold; cursor:pointer; display:flex; align-items:center; gap:10px; animation: bounceIn 0.5s ease; border: 2px solid rgba(255,255,255,0.5); pointer-events: auto !important; transition: opacity 0.3s ease, transform 0.3s ease;";
            banner.innerHTML = '<i class="fa fa-volume-up fa-2x"></i> <div>SİPARİŞ SESİNİ AKTİF ETMEK İÇİN TIKLAYIN<br><small style="font-size:0.7rem;opacity:0.8;">Tarayıcı güvenliği için ilk tıklama gereklidir.</small></div>';
            
            const handleInteraction = (e) => {
                if (e) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                debugLog("Banner clicked, priming audio...");
                primeAudioInternal();
                banner.style.opacity = '0';
                banner.style.transform = 'translateY(10px)';
                setTimeout(() => banner.remove(), 300);
            };

            banner.addEventListener('click', handleInteraction, true);
            banner.addEventListener('touchstart', handleInteraction, true);
            banner.addEventListener('mousedown', handleInteraction, true);
            
            document.body.appendChild(banner);
        };

        const primeAudioInternal = () => {
            if (audioUnlocked) {
                debugLog("Audio already unlocked, skipping prime.");
                return;
            }
            if (!globalAudio) {
                globalAudio = new Audio("/ronix_food_delivery/static/src/sound/ring_sound.mp3");
                globalAudio.loop = true;
            }
            debugLog("Priming audio system...");
            globalAudio.volume = 0;
            globalAudio.play().then(() => {
                debugLog("Audio system PRIMED successfully.");
                globalAudio.pause();
                globalAudio.volume = 1;
                audioUnlocked = true;
                const banner = document.getElementById('ronix_audio_unlock_banner');
                if (banner) {
                    banner.style.opacity = '0';
                    setTimeout(() => banner.remove(), 300);
                }
            }).catch((e) => {
                debugLog("Audio priming FAILED:", e);
            });
        };

        const showOrderPopup = (order, actionService) => {
            let container = document.getElementById("ronix_food_order_alerts_container");
            if (!container) {
                container = document.createElement("div");
                container.id = "ronix_food_order_alerts_container";
                container.style.cssText = "position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:999999; display:flex; flex-direction:column; align-items:center; gap:15px; width:95%; max-width:550px;";
                document.body.appendChild(container);
            }

            playGlobalAudio();

            const popup = document.createElement("div");
            popup.className = "bg-white border rounded shadow-lg overflow-hidden w-100 ronix-order-popup";
            popup.style.animation = "popupEnterLean 0.4s ease-out";

            if (!document.getElementById("ronix_food_alert_styles_v6")) {
                const style = document.createElement("style");
                style.id = "ronix_food_alert_styles_v6";
                style.innerHTML = `
                    @keyframes popupEnterLean { from { transform: translateY(-30px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
                    @keyframes bounceIn { 0% { opacity: 0; transform: scale(0.3); } 50% { opacity: 1; transform: scale(1.05); } 70% { transform: scale(0.9); } 100% { transform: scale(1); } }
                    .food-alert-line-item { padding: 10px 0; }
                    .food-addon-item { font-size: 0.85rem; color: #666; margin-left: 15px; }
                `;
                document.head.appendChild(style);
            }

            const formattedTotal = new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(order.amount_total);
            let linesHtml = order.lines.map(l => `
                <div class="food-alert-line-item border-bottom">
                    <div class="d-flex justify-content-between align-items-center">
                        <span><span class="fw-bold text-primary">${l.qty}x</span> ${l.name}</span>
                        <span class="fw-bold">${new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(l.price_total)}</span>
                    </div>
                    ${l.addons.length > 0 ? `<div class="mt-1">${l.addons.map(a => `<div class="food-addon-item"><i class="fa fa-plus me-1 opacity-50"></i>${a.qty}x ${a.name}</div>`).join('')}</div>` : ''}
                </div>
            `).join('');

            popup.innerHTML = `
                <div class="bg-warning text-dark px-4 py-3 d-flex align-items-center justify-content-between">
                    <div>
                        <h4 class="mb-0 fw-bold"><i class="fa fa-shopping-cart me-2"></i>YENİ SİPARİŞ!</h4>
                        <small class="fw-bold">No: #${order.name}</small>
                    </div>
                    <div class="h3 mb-0 fw-bold text-dark">${formattedTotal}</div>
                </div>
                <div class="p-4">
                    <div class="row mb-3">
                        <div class="col-6">
                            <div class="text-dark fw-bolder">Müşteri</div>
                            <div class="fw-bold text-muted">${order.customer_name}</div>
                        </div>
                        <div class="col-6 text-end">
                            <div class="text-dark fw-bolder">Telefon</div>
                            <div class="fw-bold text-muted">${order.customer_phone || '-'}</div>
                        </div>
                    </div>
                    <div class="mb-3">
                        <div class="text-dark fw-bolder mb-1">Teslimat Adresi</div>
                        <div class="border p-2 rounded bg-light small fw-bold text-muted">${order.address || 'Adres bilgisi yok'}</div>
                    </div>
                    ${order.notes ? `<div class="mb-3 border-start border-danger border-4 ps-2 py-1" style="background: #fff8f8;"><div class="text-danger fw-bolder">Not</div><div class="fw-bold small text-muted">${order.notes}</div></div>` : ''}
                    <div class="mb-4">
                        <div class="text-dark fw-bolder mb-2">Sipariş İçeriği</div>
                        <div style="max-height: 250px; overflow-y: auto;" class="px-1 text-muted">${linesHtml}</div>
                    </div>
                    <div class="d-flex gap-3">
                        <button class="btn btn-lg btn-primary flex-grow-1 btn-open-order fw-bold">SİPARİŞE GİT</button>
                        <button class="btn btn-lg btn-success flex-grow-1 btn-dismiss fw-bold text-white">TAMAM</button>
                    </div>
                </div>
            `;

            container.appendChild(popup);

            const dismissPopup = async () => {
                debugLog("Dismissing popup for order:", order.name);
                rpc("/ronix_food_delivery/acknowledge_order_alert", { order_id: order.id }).catch((e) => {
                    debugLog("Acknowledge failed:", e);
                });
                if (container.childNodes.length <= 1 && globalAudio) {
                    globalAudio.pause();
                }
                popup.style.cssText += "transition: opacity 0.3s, transform 0.3s; opacity: 0; transform: translateY(-20px);";
                setTimeout(() => {
                    popup.remove();
                    if (container.childNodes.length === 0) container.remove();
                }, 300);
            };

            popup.querySelector('.btn-dismiss').addEventListener('click', dismissPopup);
            popup.querySelector('.btn-open-order').addEventListener('click', () => {
                dismissPopup();
                actionService.doAction({ type: 'ir.actions.act_window', res_model: 'sale.order', res_id: order.id, views: [[false, 'form']], target: 'current' });
            });
        };

        const init = () => {
            debugLog("Initializing Backend New Order Alert service...");
            // Start null to catch all unacknowledged orders at start
            lastCheckTime = null; 
            pollInterval = setInterval(checkNewOrders, 15000);

            // Silent test
            const test = new Audio("data:audio/wav;base64,UklGRigAAABXQVZFRm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAP8A/wD/");
            test.play().then(() => {
                debugLog("Initial autoplay test: PASSED");
                audioUnlocked = true;
            }).catch(() => {
                debugLog("Initial autoplay test: BLOCKED. Showing banner.");
                showUnlockBanner();
            });

            const primeOnAny = (event) => {
                if (audioUnlocked) {
                    ['mousedown', 'keydown', 'touchstart'].forEach(e => document.removeEventListener(e, primeOnAny));
                    return;
                }
                if (event.target && event.target.closest && event.target.closest('#ronix_audio_unlock_banner')) {
                    return;
                }
                debugLog("Global interaction detected, priming audio...");
                primeAudioInternal();
            };
            ['mousedown', 'keydown', 'touchstart'].forEach(e => document.addEventListener(e, primeOnAny));
            
            // Initial check
            checkNewOrders();
        };

        init();

        return {
            destroy() {
                if (pollInterval) clearInterval(pollInterval);
            }
        };
    }
};

registry.category("services").add("backendNewOrderAlertService", backendNewOrderAlertService);
