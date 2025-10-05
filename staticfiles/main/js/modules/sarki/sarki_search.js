export function initSarkiSearch() {
    const form = document.getElementById('sarki-arama-form');
    const input = document.getElementById('sarki-arama-input');
    const turSelect = document.getElementById('tur-filtre');
    const sonucDiv = document.getElementById('sarki-arama-sonuc');
    if (!form || !input || !turSelect || !sonucDiv) return;

    const searchSarkilar = async () => {
        const query = input.value.trim();
        const tur = turSelect.value;
        let url = `/sarki/ara/?q=${encodeURIComponent(query)}`;
        if (tur) url += `&tur=${encodeURIComponent(tur)}`;

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (!response.ok) throw new Error(`Ağ hatası: ${response.status}`);
            const data = await response.json();
            sonucDiv.innerHTML = '';
            if (data.sarkilar && data.sarkilar.length > 0) {
                const ul = document.createElement('ul');
                ul.className = 'list-unstyled';
                data.sarkilar.forEach(sarki => {
                    const li = document.createElement('li');
                    li.className = 'sarki-item mb-2';
                    li.innerHTML = `
                        <a href="/sarki/detay/${sarki.id}" class="text-decoration-none">
                            <strong>${sarki.ad}</strong>
                            <p class="text-muted small">${sarki.album} - ${sarki.kisi}</p>
                            <p class="text-muted small">${sarki.sozler}</p>
                        </a>
                    `;
                    ul.appendChild(li);
                });
                sonucDiv.appendChild(ul);
            } else {
                sonucDiv.innerHTML = '<p class="text-muted">${window.i18n?.t('sarki.song_not_found') || 'Şarkı bulunamadı.'}</p>';
            }
        } catch (error) {
            console.error('Şarkı arama hatası:', error);
            sonucDiv.innerHTML = '<p class="text-muted">Di dema lêgerînê de çewtîyek çêbû.</p>';
        }
    };

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        searchSarkilar();
    });

    turSelect.addEventListener('change', searchSarkilar);
}