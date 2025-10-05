export function initVoteHandler() {
    const getCsrfToken = () => {
        const token = document.querySelector('meta[name="csrf-token"]')?.content;
        if (!token) {
            console.error('CSRF token bulunamadı');
            return null;
        }
        return token;
    };

    const voteForms = document.querySelectorAll('.vote-form');
    if (!voteForms.length) {
        console.warn('vote-form bulunamadı');
        return;
    }

    voteForms.forEach(form => {
        if (!form.dataset.listenerAdded) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault(); // Formun varsayılan davranışını engelle
                e.stopPropagation(); // Olayın yayılmasını durdur
                const postId = form.dataset.postId;
                const commentId = form.dataset.commentId;
                const id = postId || commentId;
                const voteType = form.querySelector('button[type="submit"]')?.dataset.voteType;
                const csrfToken = getCsrfToken();

                if (!csrfToken || !id || !voteType) {
                    console.error('Eksik veri:', { csrfToken, id, voteType, postId, commentId });
                    alert('Operasyona dengdanê bi ser neket: Daneyên kêm.');
                    return;
                }

                console.log('Oylama gönderiliyor, ID:', id, 'VoteType:', voteType);

                try {
                    const formData = new FormData(form);
                    const url = postId ? `/vote-post/${id}/` : `/vote-comment/${id}/`;
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: formData
                    });

                    const responseText = await response.text(); // Yanıtı önce metin olarak al
                    console.log('Sunucu yanıtı (ham):', responseText);

                    let data;
                    try {
                        data = JSON.parse(responseText); // JSON’a çevir
                    } catch (parseError) {
                        throw new Error(`JSON parse hatası: ${parseError.message}, Yanıt: ${responseText}`);
                    }

                    if (!response.ok) {
                        throw new Error(`Sunucu hatası: ${response.status}, Yanıt: ${responseText}`);
                    }

                    if (data.success !== undefined && !data.success) {
                        const errorMessage = data.errors || data.error || 'Peyama çewtiyê nehat dayîn';
                        console.error('Oylama hatası:', errorMessage, 'Tam yanıt:', data);
                        alert(`Operasyona dengdanê bi ser neket: ${errorMessage}`);
                        return;
                    }

                    // Butonları formun üst kapsayıcısından seç, voteType’a göre
                    const parentContainer = form.closest('.post-actions');
                    const upvoteBtn = parentContainer?.querySelector(`.upvote-btn[data-vote-type="up"]`);
                    const downvoteBtn = parentContainer?.querySelector(`.downvote-btn[data-vote-type="down"]`);

                    if (upvoteBtn) {
                        upvoteBtn.textContent = `${data.upvotes} ↑`;
                        console.log('Up butonu günソー: ', upvoteBtn.textContent);
                    } else {
                        console.error('Up butonu bulunamadı, container:', parentContainer);
                    }
                    if (downvoteBtn) {
                        downvoteBtn.textContent = `${data.downvotes} ↓`;
                        console.log('Down butonu güncellendi:', downvoteBtn.textContent);
                    } else {
                        console.error('Down butonu bulunamadı, container:', parentContainer);
                    }
                    console.log('Oylama başarılı:', data);
                } catch (error) {
                    console.error('Oylama gönderim hatası:', error.message, 'Tam hata:', error);
                    alert('Operasyona dengdanê bi ser neket: Çewtiya serverê.');
                }
            }, { capture: true }); // Olayı yakalama aşamasında dinle
            form.dataset.listenerAdded = 'true';
            console.log('Olay dinleyicisi eklendi, form ID:', form.dataset.postId || form.dataset.commentId || 'tanımsız');
        } else {
            console.log('Zaten dinleyici eklenmiş, form ID:', form.dataset.postId || form.dataset.commentId || 'tanımsız');
        }
    });
}