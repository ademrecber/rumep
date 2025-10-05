export function initKisiAra() {
    const form = document.getElementById('kisi-ara-form');
    const input = document.getElementById('kisi-ara-input');
    const sonucDiv = document.getElementById('kisi-ara-sonuc');
    if (!form || !input || !sonucDiv) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = input.value.trim();
        if (!query) return;

        try {
            const response = await fetch(`/sarki/kisi-ara/?q=${encodeURIComponent(query)}`, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (!response.ok) throw new Error(`Ağ hatası: ${response.status}`);
            const data = await response.json();
            sonucDiv.innerHTML = '';
            if (data.kisiler && data.kisiler.length > 0) {
                const ul = document.createElement('ul');
                ul.className = 'list-unstyled';
                data.kisiler.forEach(kisi => {
                    const li = document.createElement('li');
                    li.className = 'kisi-item mb-2';
                    li.innerHTML = `
                        <a href="/sarki/ekle/?kisi_id=${kisi.id}" class="text-decoration-none">
                            <strong>${kisi.ad}</strong>
                            <p class="text-muted small">${kisi.biyografi}</p>
                        </a>
                    `;
                    ul.appendChild(li);
                });
                sonucDiv.appendChild(ul);
            } else {
                sonucDiv.innerHTML = '<p class="text-muted">Kes nehat dîtin.</p>';
            }
        } catch (error) {
            console.error('Kişi arama hatası:', error);
            sonucDiv.innerHTML = '<p class="text-muted">Di dema lêgerînê de çewtîyek çêbû.</p>';
        }
    });
}

export function initAlbumEkle() {
    const form = document.getElementById('album-ekle-form');
    const errorDiv = document.getElementById('album-form-errors');
    if (!form || !errorDiv) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorDiv.classList.add('d-none');
        errorDiv.innerHTML = '';

        const formData = new FormData(form);
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: formData
            });
            const data = await response.json();
            if (data.success) {
                form.reset();
                alert(window.i18n?.t('sarki.album_added_success') || 'Albüm başarıyla eklendi!');
                window.location.reload();
            } else {
                errorDiv.classList.remove('d-none');
                errorDiv.innerHTML = '<p>Albûm nehat zêdekirin. Ji kerema xwe çewtiyan kontrol bikin.</p>';
            }
        } catch (error) {
            console.error('Albüm ekleme hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.innerHTML = '<p>Çewtîyek çêbû, ji kerema xwe dîsa biceribîne.</p>';
        }
    });
}

export function initSarkiEkle() {
    const form = document.getElementById('sarki-ekle-form');
    const errorDiv = document.getElementById('sarki-form-errors');
    if (!form || !errorDiv) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        errorDiv.classList.add('d-none');
        errorDiv.innerHTML = '';

        const album = form.querySelector('#album').value;
        if (!album) {
            errorDiv.classList.remove('d-none');
            errorDiv.innerHTML = '<p>Ji kerema xwe albûmekê hilbijêre.</p>';
            return;
        }

        const formData = new FormData(form);
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: formData
            });
            const data = await response.json();
            if (data.success) {
                form.reset();
                alert(window.i18n?.t('sarki.song_added_success') || 'Şarkı başarıyla eklendi!');
                window.location.reload();
            } else {
                errorDiv.classList.remove('d-none');
                let errorMessage = '<p>Stran nehat zêdekirin. Ji kerema xwe çewtiyan kontrol bikin:</p><ul>';
                const errors = JSON.parse(data.errors);
                for (const field in errors) {
                    errors[field].forEach(error => {
                        errorMessage += `<li>${field}: ${error.message}</li>`;
                    });
                }
                errorMessage += '</ul>';
                errorDiv.innerHTML = errorMessage;
            }
        } catch (error) {
            console.error('Şarkı ekleme hatası:', error);
            errorDiv.classList.remove('d-none');
            errorDiv.innerHTML = '<p>Çewtîyek çêbû, ji kerema xwe dîsa biceribîne.</p>';
        }
    });
}
