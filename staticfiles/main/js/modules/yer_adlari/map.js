window.initMap = function() {
    const mapOptions = {
        center: { lat: 37.5, lng: 41.0 },
        zoom: 6,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    const map = new google.maps.Map(document.getElementById('map'), mapOptions);

    // Yer adları için işaretleyiciler
    const yerAdlari = JSON.parse(document.getElementById('yer-adlari-data').textContent || '[]');
    yerAdlari.forEach(yer => {
        if (yer.enlem && yer.boylam) {
            const markerOptions = {
                position: { lat: parseFloat(yer.enlem), lng: parseFloat(yer.boylam) },
                map: map,
                title: yer.ad,
                icon: {
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: yer.kategori === 'il' ? 10 : yer.kategori === 'ilce' ? 8 : yer.kategori === 'kasaba' ? 6 : yer.kategori === 'belde' ? 4 : 2,
                    fillColor: yer.kategori === 'il' ? '#FF0000' : yer.kategori === 'ilce' ? '#FFA500' : yer.kategori === 'kasaba' ? '#FFFF00' : yer.kategori === 'belde' ? '#00FF00' : '#0000FF',
                    fillOpacity: 0.8,
                    strokeWeight: 1,
                }
            };
            const marker = new google.maps.Marker(markerOptions);
            marker.addListener('click', () => {
                window.location.href = `/yer-adi/${yer.id}/`;
            });
        }
    });

    // Yer adı ekleme sayfasında koordinat seçimi
    if (document.getElementById('yer-adi-form')) {
        const enlemInput = document.getElementById('id_enlem');
        const boylamInput = document.getElementById('id_boylam');
        map.addListener('click', (event) => {
            const lat = event.latLng.lat();
            const lng = event.latLng.lng();
            enlemInput.value = lat.toFixed(6);
            boylamInput.value = lng.toFixed(6);
            new google.maps.Marker({
                position: { lat: lat, lng: lng },
                map: map
            });
        });
    }
};