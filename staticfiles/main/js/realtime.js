// Real-time bildirimler ve canlı güncellemeler
class RealTimeUpdates {
    constructor() {
        this.lastCheck = Date.now();
        this.checkInterval = 30000; // 30 saniye
        this.init();
    }

    init() {
        this.startPolling();
        this.setupVisibilityChange();
        this.setupNotificationPermission();
    }

    async checkForUpdates() {
        try {
            const response = await fetch('/api/check-updates/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.handleUpdates(data);
            }
        } catch (error) {
            console.log('Update check failed:', error);
        }
    }

    handleUpdates(data) {
        // Yeni bildirimler
        if (data.new_notifications > 0) {
            this.updateNotificationBadge(data.new_notifications);
            this.showDesktopNotification('Yeni bildiriminiz var!');
        }

        // Yeni entry'ler
        if (data.new_entries && data.new_entries.length > 0) {
            this.showNewEntriesAlert(data.new_entries.length);
        }

        // Online kullanıcı sayısı
        if (data.online_users) {
            this.updateOnlineUsers(data.online_users);
        }
    }

    updateNotificationBadge(count) {
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline' : 'none';
        }
    }

    showDesktopNotification(message) {
        if (Notification.permission === 'granted') {
            new Notification('Rumep', {
                body: message,
                icon: '/static/main/favicon.ico',
                tag: 'rumep-notification'
            });
        }
    }

    showNewEntriesAlert(count) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-info alert-dismissible fade show position-fixed';
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
        alertDiv.innerHTML = `
            <strong>${count} yeni entry!</strong> Sayfayı yenileyin.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);
        
        setTimeout(() => alertDiv.remove(), 5000);
    }

    updateOnlineUsers(count) {
        const onlineElement = document.querySelector('.online-users-count');
        if (onlineElement) {
            onlineElement.textContent = count;
        }
    }

    setupNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    setupVisibilityChange() {
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.checkForUpdates();
            }
        });
    }

    startPolling() {
        setInterval(() => {
            if (!document.hidden) {
                this.checkForUpdates();
            }
        }, this.checkInterval);
    }
}

// Sayfa yüklendiğinde başlat
document.addEventListener('DOMContentLoaded', () => {
    new RealTimeUpdates();
});

// Typing indicator
class TypingIndicator {
    constructor() {
        this.typingUsers = new Set();
        this.setupTypingEvents();
    }

    setupTypingEvents() {
        const textareas = document.querySelectorAll('textarea[name="content"]');
        textareas.forEach(textarea => {
            let typingTimer;
            
            textarea.addEventListener('input', () => {
                this.showTyping();
                clearTimeout(typingTimer);
                typingTimer = setTimeout(() => this.hideTyping(), 2000);
            });
        });
    }

    showTyping() {
        // Typing göstergesi göster
        const indicator = document.querySelector('.typing-indicator');
        if (indicator) {
            indicator.style.display = 'block';
        }
    }

    hideTyping() {
        // Typing göstergesi gizle
        const indicator = document.querySelector('.typing-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }
}

new TypingIndicator();