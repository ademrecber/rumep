import { initCopyLink } from "../../copy-link.js";

export function initCritiqueLoader(url) {
    console.log('initCritiqueLoader başlatılıyor, URL:', url);
    const loadCritiques = () => {
        console.log('Eleştiri listesi yükleniyor:', url);
        fetch(url, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => {
            console.log('Liste yanıtı, durum:', response.status);
            if (!response.ok) throw new Error('Sunucu hatası: ' + response.status);
            return response.json();
        })
        .then(data => {
            console.log('Liste verisi:', data);
            const sidebar = document.querySelector('.right-sidebar');
            if (!sidebar) {
                console.error('right-sidebar bulunamadı');
                return;
            }
            let critiqueList = document.getElementById('critique-list');
            if (!critiqueList) {
                critiqueList = document.createElement('div');
                critiqueList.id = 'critique-list';
                critiqueList.className = 'mt-3';
                critiqueList.style.maxHeight = 'min(800px, 90vh)';
                critiqueList.style.overflowY = 'auto';
                critiqueList.innerHTML = `
                    <button class="btn btn-primary rounded-pill mb-3 d-none d-md-block" id="toggle-critique-btn">Vê nivîsê binirxîne</button>
                    <h5>Nirxandinên Dawî</h5>
                `;
                sidebar.appendChild(critiqueList);
            }
            const mobileCritiqueList = document.getElementById('mobile-critique-list');
            if (!mobileCritiqueList) {
                console.warn('mobile-critique-list bulunamadı');
                return;
            }
            if (data.critiques) {
                critiqueList.querySelectorAll('.critique-item').forEach(item => item.remove());
                mobileCritiqueList.querySelectorAll('.critique-item').forEach(item => item.remove());
                data.critiques.forEach(critique => {
                    const postId = url.split('=')[1]; // URL’den post_id alınıyor
                    const critiqueDiv = document.createElement('div');
                    critiqueDiv.className = 'critique-item card mb-2';
                    critiqueDiv.style.cursor = 'pointer';
                    critiqueDiv.innerHTML = `
                        <div class="card-body p-3">
                            <div class="d-flex justify-content-between align-items-start">
                                <p class="mb-1">
                                    <strong>${critique.nickname}</strong> 
                                    <span class="text-muted"><a href="/profile/${critique.username}/" class="text-muted text-decoration-none">@${critique.username}</a> · ${critique.short_id} · ${critique.created_at}</span>
                                </p>
                                <div class="d-flex align-items-center">
                                    <div class="dropdown me-2">
                                        <button class="btn btn-link text-muted p-0" type="button" data-bs-toggle="dropdown">
                                            <i class="bi bi-three-dots"></i>
                                        </button>
                                        <ul class="dropdown-menu">
                                            ${critique.is_owner ? `
                                                <li>
                                                    <button class="dropdown-item text-danger delete-critique-btn" data-critique-id="${critique.id}">Jêbirin</button>
                                                </li>
                                            ` : ''}
                                            <li>
                                                <button class="dropdown-item copy-critique-link-btn" data-critique-id="${critique.short_id}" data-post-id="${postId}">Girêdanê Kopî Bike</button>
                                            </li>
                                        </ul>
                                    </div>
                                    ${critique.is_owner ? '' : `
                                        ${critique.user_rating ? `
                                            <span class="text-muted me-2 user-rating" data-critique-id="${critique.id}" style="cursor: pointer;">Pûana We: ${critique.user_rating}</span>
                                        ` : `
                                            <button class="btn btn-primary btn-sm rounded-pill me-2 vote-critique-btn" data-critique-id="${critique.id}">Pûan Bide</button>
                                        `}
                                    `}
                                </div>
                            </div>
                            <div class="critique-text">
                                ${critique.text.length > 500 ? `
                                    <div class="text-preview"><p>${critique.text}</p></div>
                                    <button class="btn btn-link text-primary p-0 show-more-btn">Zêdetir bibîne</button>
                                    <div class="full-text d-none"><p>${critique.text}</p></div>
                                    <button class="btn btn-link text-primary p-0 show-less-btn d-none">Kêmtir bibîne</button>
                                ` : `<p>${critique.text}</p>`}
                            </div>
                            <p class="text-muted small">Pûana Navîn: ${critique.rating.toFixed(1)}</p>
                        </div>
                    `;

                    // Modal açma fonksiyonu
                    const openCritiqueModal = (e) => {
                        if (e.target.tagName !== 'BUTTON' && !e.target.closest('.dropdown') && !e.target.classList.contains('user-rating')) {
                            console.log('Modal açılıyor, eleştiri ID:', critique.id);
                            const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('critiqueModal'));
                            document.getElementById('modal-nickname').textContent = critique.nickname;
                            document.getElementById('modal-username').textContent = `@${critique.username}`;
                            document.getElementById('modal-short-id').textContent = critique.short_id;
                            document.getElementById('modal-date').textContent = critique.created_at;
                            document.getElementById('modal-text').innerHTML = critique.text; // render_emojis view'dan geliyor
                            document.getElementById('modal-rating-value').textContent = critique.rating.toFixed(1);
                            const userRatingSpan = document.getElementById('modal-user-rating-value');
                            userRatingSpan.textContent = critique.user_rating ? critique.user_rating : 'We hêj pûan nedaye';
                            const ratingButtons = document.getElementById('rating-buttons');
                            ratingButtons.innerHTML = critique.is_owner ? '<p class="text-muted small">Hûn nikarin nirxandina xwe pûan bikin.</p>' : '';
                            const deleteForm = document.getElementById('delete-critique-form');
                            deleteForm.style.display = critique.is_owner ? 'block' : 'none';
                            if (critique.is_owner) {
                                deleteForm.action = `/delete-critique/${critique.id}/`;
                                deleteForm.onsubmit = (e) => {
                                    e.preventDefault();
                                    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
                                    if (!csrfToken) {
                                        console.error('CSRF token bulunamadı');
                                        return;
                                    }
                                    fetch(`/delete-critique/${critique.id}/`, {
                                        method: 'POST',
                                        headers: {
                                            'X-CSRFToken': csrfToken,
                                            'X-Requested-With': 'XMLHttpRequest'
                                        }
                                    })
                                    .then(res => res.json())
                                    .then(data => {
                                        if (data.success) {
                                            alert('Nirxandin bi serkeftî hate jêbirin!');
                                            modal.hide();
                                            loadCritiques();
                                        } else {
                                            console.error('Silme hatası:', data.error);
                                        }
                                    })
                                    .catch(error => console.error('Silme hatası:', error));
                                };
                            }
                            modal.show();
                            console.log('Modal açıldı, eleştiri:', critique.text);
                        }
                    };

                    // Hem click hem touchstart için olay dinleyicisi
                    critiqueDiv.addEventListener('click', openCritiqueModal);
                    critiqueDiv.addEventListener('touchstart', openCritiqueModal);

                    critiqueList.appendChild(critiqueDiv);
                    if (mobileCritiqueList) {
                        const mobileCritiqueDiv = critiqueDiv.cloneNode(true);
                        mobileCritiqueDiv.querySelector('.critique-text').innerHTML = critique.text.length > 500 ? `
                            <div class="text-preview"><p>${critique.text}</p></div>
                            <button class="btn btn-link text-primary p-0 show-more-btn">Zêdetir bibîne</button>
                            <div class="full-text d-none"><p>${critique.text}</p></div>
                            <button class="btn btn-link text-primary p-0 show-less-btn d-none">Kêmtir bibîne</button>
                        ` : `<p>${critique.text}</p>`;
                        // Mobil için olay dinleyicisini tekrar bağla
                        mobileCritiqueDiv.addEventListener('click', openCritiqueModal);
                        mobileCritiqueDiv.addEventListener('touchstart', openCritiqueModal);
                        mobileCritiqueList.appendChild(mobileCritiqueDiv);
                    }
                });
                // Puanlama butonlarına olay dinleyici
                document.querySelectorAll('.vote-critique-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        const critiqueId = btn.dataset.critiqueId;
                        const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('voteCritiqueModal'));
                        document.getElementById('submit-vote-critique').dataset.critiqueId = critiqueId;
                        modal.show();
                    });
                });
                // Puan değiştirme için olay dinleyici
                document.querySelectorAll('.user-rating').forEach(span => {
                    span.addEventListener('click', (e) => {
                        e.preventDefault();
                        const critiqueId = span.dataset.critiqueId;
                        const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('voteCritiqueModal'));
                        document.getElementById('submit-vote-critique').dataset.critiqueId = critiqueId;
                        modal.show();
                    });
                });
                // Silme butonlarına olay dinleyici
                document.querySelectorAll('.delete-critique-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        const critiqueId = btn.dataset.critiqueId;
                        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
                        if (!csrfToken) {
                            console.error('CSRF token bulunamadı');
                            return;
                        }
                        fetch(`/delete-critique/${critiqueId}/`, {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': csrfToken,
                                'X-Requested-With': 'XMLHttpRequest'
                            }
                        })
                        .then(res => res.json())
                        .then(data => {
                            if (data.success) {
                                alert('Nirxandin bi serkeftî hate jêbirin!');
                                loadCritiques();
                            } else {
                                console.error('Silme hatası:', data.error);
                            }
                        })
                        .catch(error => console.error('Silme hatası:', error));
                    });
                });
                initCopyLink(); // Yeni yüklenen değerlendirmeler için kopyalama olayını bağla
            } else {
                console.log('Eleştiri bulunamadı');
            }
            // critiquesLoaded eventi tetikle
            document.dispatchEvent(new Event('critiquesLoaded'));
        })
        .catch(error => console.error('Liste yükleme hatası:', error));
    };

    // Eleştiri formu
    const critiqueForm = document.getElementById('critique-form');
    if (critiqueForm) {
        critiqueForm.onsubmit = (e) => e.preventDefault(); // Tarayıcı submit’ini tamamen engelle
        critiqueForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Eleştiri formu gönderiliyor, action:', this.dataset.action);
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true; // Çift gönderimi önlemek için butonu devre dışı bırak
            }
            const textArea = this.querySelector('textarea[name="text"]');
            const textValue = textArea ? textArea.value.trim() : '';
            console.log('Textarea içeriği:', textValue);
            if (!textValue) {
                console.error('Text alanı boş, gönderim iptal edildi');
                if (submitButton) submitButton.disabled = false;
                return;
            }
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
            if (!csrfToken) {
                console.error('CSRF token bulunamadı');
                if (submitButton) submitButton.disabled = false;
                return;
            }
            const formData = new FormData(this);
            console.log('Gönderilen form verisi:', Array.from(formData.entries()));
            fetch(this.dataset.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => {
                console.log('Yanıt alındı, durum:', response.status);
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(`Sunucu hatası: ${response.status}, Hatalar: ${JSON.stringify(data.errors || 'Bilinmeyen hata')}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('Yanıt verisi:', data);
                if (data.success) {
                    console.log('Eleştiri eklendi:', data);
                    this.reset(); // Formu sıfırla
                    // critique-section açık kalsın, ikinci değerlendirme için
                    loadCritiques();
                } else {
                    console.error('Eleştiri eklenemedi:', data.errors);
                }
            })
            .catch(error => console.error('Eleştiri gönderme hatası:', error.message))
            .finally(() => {
                if (submitButton) submitButton.disabled = false; // İşlem tamamlanınca butonu yeniden etkinleştir
            });
        }, { once: true }); // Submit olayını sadece bir kez bağla
    } else {
        console.warn('critique-form bulunamadı');
    }

    // Puanlama modalı için yıldız işlevselliği
    let selectedRating = 0;
    const stars = document.querySelectorAll('.star-rating-item');
    const submitVoteBtn = document.getElementById('submit-vote-critique');
    stars.forEach(star => {
        star.addEventListener('mouseover', () => {
            const value = parseInt(star.dataset.value);
            stars.forEach(s => {
                if (parseInt(s.dataset.value) <= value) {
                    s.classList.add('text-warning');
                    s.classList.remove('text-muted');
                } else {
                    s.classList.add('text-muted');
                    s.classList.remove('text-warning');
                }
            });
        });
        star.addEventListener('mouseout', () => {
            stars.forEach(s => {
                if (parseInt(s.dataset.value) <= selectedRating) {
                    s.classList.add('text-warning');
                    s.classList.remove('text-muted');
                } else {
                    s.classList.add('text-muted');
                    s.classList.remove('text-warning');
                }
            });
        });
        star.addEventListener('click', () => {
            selectedRating = parseInt(star.dataset.value);
            submitVoteBtn.disabled = false;
            stars.forEach(s => {
                if (parseInt(s.dataset.value) <= selectedRating) {
                    s.classList.add('text-warning');
                    s.classList.remove('text-muted');
                } else {
                    s.classList.add('text-muted');
                    s.classList.remove('text-warning');
                }
            });
        });
    });

    // Puanlama modalı gönderimi
    if (submitVoteBtn) {
        submitVoteBtn.addEventListener('click', () => {
            const critiqueId = submitVoteBtn.dataset.critiqueId;
            const formData = new FormData();
            formData.append('rating', selectedRating);
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
            if (!csrfToken) {
                console.error('CSRF token bulunamadı');
                return;
            }
            fetch(`/vote-critique/${critiqueId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    bootstrap.Modal.getInstance(document.getElementById('voteCritiqueModal')).hide();
                    selectedRating = 0;
                    submitVoteBtn.disabled = true;
                    stars.forEach(s => s.classList.add('text-muted'));
                    loadCritiques();
                } else {
                    console.error('Puanlama hatası:', data.errors);
                }
            })
            .catch(error => console.error('Puanlama hatası:', error));
        });
    } else {
        console.warn('submit-vote-critique butonu bulunamadı');
    }

    loadCritiques();
}