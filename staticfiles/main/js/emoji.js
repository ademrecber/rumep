export function initEmojiPicker() {
    const emojiButtons = document.querySelectorAll('#emojiButton');
    const emojiModal = document.getElementById('emojiModal');
    const emojiKeyboard = document.getElementById('emojiKeyboard');

    if (!emojiButtons.length || !emojiModal || !emojiKeyboard) {
        console.warn('Emoji picker için gerekli elementler bulunamadı.');
        return;
    }

    // Aktif textarea'yı saklamak için
    let activeTextarea = null;

    // Modal açma ve aktif textarea'yı ayarlama
    emojiButtons.forEach(button => {
        button.addEventListener('click', () => {
            // home.html, post_detail.html, profile.html ve profile_detail.html için uyumlu
            activeTextarea = button.closest('.input-group, .form-group')?.querySelector('textarea');
            if (activeTextarea) {
                bootstrap.Modal.getOrCreateInstance(emojiModal).show();
            } else {
                console.warn('Emoji butonuna bağlı textarea bulunamadı.');
            }
        });
    });

    // Emojileri yükle ve önbelleğe al
    let cachedEmojis = null;
    function loadEmojis() {
        if (cachedEmojis) {
            renderEmojis(cachedEmojis);
            return;
        }
        fetch('/emojis/')
            .then(response => {
                if (!response.ok) throw new Error(`Emoji yükleme hatası: ${response.status}`);
                return response.json();
            })
            .then(data => {
                cachedEmojis = data.emojis;
                renderEmojis(cachedEmojis);
            })
            .catch(error => console.error('Emojiler yüklenirken hata:', error));
    }

    function renderEmojis(emojis) {
        emojiKeyboard.innerHTML = '';
        emojis.forEach(emoji => {
            // Güvenlik: src yalnızca /static/emojis/ ile başlıyorsa kabul et
            if (!emoji.src.startsWith('/static/emojis/')) return;
            const img = document.createElement('img');
            img.src = emoji.src;
            img.alt = emoji.name;
            img.className = 'emoji';
            img.style.width = '30px';
            img.style.height = '30px';
            img.style.margin = '5px';
            img.style.cursor = 'pointer';
            img.title = emoji.shortcode;
            img.addEventListener('click', () => {
                if (activeTextarea) {
                    // Güvenlik: Textarea uzunluğu kontrolü
                    const shortcodeWithSpace = `${emoji.shortcode} `;
                    if (activeTextarea.value.length + shortcodeWithSpace.length <= activeTextarea.maxLength) {
                        activeTextarea.value += shortcodeWithSpace;
                        activeTextarea.dispatchEvent(new Event('input'));
                        bootstrap.Modal.getInstance(emojiModal).hide();
                    } else {
                        console.warn('Textarea maksimum uzunluğa ulaşıldı.');
                    }
                } else {
                    console.warn('Aktif textarea bulunamadı.');
                }
            });
            emojiKeyboard.appendChild(img);
        });
    }

    // Emojileri yükle
    loadEmojis();
}