console.log('yer-adi-ekle.js yüklendi'); // Hata ayıklama

function toggleParentField() {
    const kategori = document.getElementById('id_kategori');
    const parentField = document.getElementById('parent-field');
    if (kategori && parentField) {
        if (kategori.value === 'il') {
            parentField.style.display = 'none';
            const parentSelect = document.getElementById('id_parent');
            if (parentSelect) {
                parentSelect.value = '';
            }
        } else {
            parentField.style.display = 'block';
        }
    } else {
        console.error('Kategori veya parentField elementi bulunamadı');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded tetiklendi'); // Hata ayıklama
    const parentSelect = document.getElementById('id_parent');
    if (!parentSelect) {
        console.error('id_parent elementi bulunamadı');
        return;
    }

    const yerAdlariData = document.getElementById('yer-adlari-data');
    let yerAdlari = [];
    if (yerAdlariData) {
        try {
            yerAdlari = JSON.parse(yerAdlariData.textContent || '[]');
            console.log('yerAdlari:', yerAdlari); // Hata ayıklama
        } catch (e) {
            console.error('yerAdlari JSON parse hatası:', e);
        }
    } else {
        console.error('yer-adlari-data elementi bulunamadı');
    }

    function buildParentOptions() {
        parentSelect.innerHTML = '<option value="">Hilbijêre</option>';
        const iller = yerAdlari.filter(yer => yer.kategori === 'il').sort((a, b) => a.ad.localeCompare(b.ad));
        iller.forEach(il => {
            const option = document.createElement('option');
            option.value = il.id;
            option.text = il.ad;
            parentSelect.appendChild(option);

            const ilceler = yerAdlari.filter(yer => yer.kategori === 'ilce' && yer.parent_id === il.id).sort((a, b) => a.ad.localeCompare(b.ad));
            ilceler.forEach(ilce => {
                const option = document.createElement('option');
                option.value = ilce.id;
                option.text = `└ ${ilce.ad} (${window.i18n?.t('yer_adlari.district') || 'İlçe'})`;
                parentSelect.appendChild(option);

                const altYerler = yerAdlari.filter(yer => ['kasaba', 'belde', 'koy'].indexOf(yer.kategori) !== -1 && yer.parent_id === ilce.id).sort((a, b) => a.ad.localeCompare(b.ad));
                altYerler.forEach(yer => {
                    const option = document.createElement('option');
                    option.value = yer.id;
                    option.text = `  └ ${yer.ad} (${yer.kategori.charAt(0).toUpperCase() + yer.kategori.slice(1)})`;
                    parentSelect.appendChild(option);
                });
            });
        });
    }

    try {
        buildParentOptions();
        toggleParentField();
        const kategoriSelect = document.getElementById('id_kategori');
        if (kategoriSelect) {
            kategoriSelect.addEventListener('change', buildParentOptions);
        } else {
            console.error('id_kategori elementi bulunamadı');
        }
    } catch (error) {
        console.error('buildParentOptions hatası:', error);
    }
});