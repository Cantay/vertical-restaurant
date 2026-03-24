/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

const POLL_INTERVAL = 10000; // 10 seconds

export const qrWaiterDashboardService = {
    dependencies: ["action", "notification"],

    start(env, { action, notification }) {
        let lastKnownIds = new Set();
        let pollTimer = null;
        let isPolling = false;

        // Only poll when we're on the waiter call list view
        function shouldPoll() {
            const actionManager = document.querySelector('.o_action_manager');
            return actionManager && actionManager.querySelector('[data-model="qr.menu.waiter.call"]');
        }

        async function poll() {
            if (!shouldPoll()) {
                isPolling = false;
                return;
            }

            try {
                const calls = await rpc('/qr_menu/check_calls', {});

                if (Array.isArray(calls)) {
                    const currentIds = new Set(calls.map(c => c.id));

                    // Find new calls
                    for (const call of calls) {
                        if (!lastKnownIds.has(call.id) && lastKnownIds.size > 0) {
                            // New call detected!
                            const typeLabels = {
                                'waiter': 'Garson Çağrısı',
                                'bill': 'Hesap İsteği',
                                'water': 'Su İsteği',
                                'custom': 'Özel İstek',
                            };

                            notification.add(
                                `${call.table_name} - ${typeLabels[call.call_type] || call.call_type}${call.custom_message ? ': ' + call.custom_message : ''}`,
                                {
                                    title: `Yeni Çağrı - ${call.restaurant_name}`,
                                    type: 'warning',
                                    sticky: true,
                                }
                            );

                            // Play notification sound
                            playNotificationSound();
                        }
                    }

                    lastKnownIds = currentIds;
                }
            } catch (e) {
                // Silently ignore polling errors
            }

            pollTimer = setTimeout(poll, POLL_INTERVAL);
        }

        function playNotificationSound() {
            try {
                const audio = new Audio('/ronix_qr_menu/static/src/sounds/notification.mp3');
                audio.volume = 0.5;
                audio.play().catch(() => {});
            } catch (e) {
                // Audio playback may be blocked by browser
            }
        }

        // Start polling when the action changes
        env.bus.addEventListener('ACTION_MANAGER:UPDATE', () => {
            if (shouldPoll() && !isPolling) {
                isPolling = true;
                lastKnownIds = new Set();
                poll();
            }
        });
    },
};

registry.category("services").add("qrWaiterDashboard", qrWaiterDashboardService);
