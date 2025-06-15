import { initTextarea } from './textarea.js';
import { initLikes } from './like.js';
import { initShowMore } from './showMore.js';
import { initReplies } from './reply.js';
import { initComments } from './comments.js';
import { initPostDetail } from './modules/post/post_detail.js';
import { initCritiqueLoader } from './modules/critique/critique_loader.js';
import { initVoteHandler } from './modules/vote/vote_handler.js';
import { initProfile } from './modules/profile/profile.js';
import { loadMorePosts } from './load-more.js';
import { loadMorePopularPosts } from './load-more-popular.js';
import { initEmojiPicker } from './emoji.js';
import { initGoogleSignIn, initProfileCompletion } from './auth.js';
import { initKatkiLoader } from './modules/katki/katki_loader.js';

document.addEventListener('DOMContentLoaded', function() {
    console.log("scripts.js yüklendi");
    try {
        console.log("Modüller başlatılıyor...");
        
        // Auth modüllerini başlat
        if (window.location.pathname.includes('/login/')) {
            initGoogleSignIn();
            console.log("initGoogleSignIn tamamlandı");
        }
        
        if (window.location.pathname.includes('/complete-profile/')) {
            initProfileCompletion();
            console.log("initProfileCompletion tamamlandı");
        }
        
        initTextarea();
        console.log("initTextarea tamamlandı");
        initLikes();
        console.log("initLikes tamamlandı");
        initShowMore();
        console.log("initShowMore tamamlandı");

        // Yalnızca post detay sayfasında initReplies ve initComments başlat
        if (document.querySelector('.comments-section')) {
            initReplies();
            console.log("initReplies tamamlandı");
            initComments();
            console.log("initComments tamamlandı");
        }

        // Yalnızca post detay sayfasında initPostDetail başlat
        if (document.querySelector('.tweet-card') && window.location.pathname.includes('/post/')) {
            initPostDetail();
            console.log("initPostDetail tamamlandı");
        }

        // Yalnızca eleştiri URL'si varsa initCritiqueLoader başlat
        const critiqueUrlElement = document.querySelector('meta[name="critique-url"]');
        const critiqueUrl = critiqueUrlElement ? critiqueUrlElement.content : '';
        if (critiqueUrl) {
            initCritiqueLoader(critiqueUrl);
            console.log("initCritiqueLoader tamamlandı");
        } else {
            console.warn('Critique URL bulunamadı');
        }

        // Katkılar modülünü başlat
        if ((window.location.pathname === '/' && window.location.search.includes('sekme=katkilar')) || 
            document.getElementById('katki-list')) {
            initKatkiLoader();
            console.log("initKatkiLoader tamamlandı");
        }

        initVoteHandler();
        console.log("initVoteHandler tamamlandı");

        // Popüler sayfada ilk yüklemede postları yeniden yükle
        if (document.getElementById('post-list') && window.location.pathname.includes('/popular')) {
            document.querySelector('.post-container').innerHTML = '';
            window.offset = 0;
            loadMorePopularPosts();
            console.log("loadMorePopularPosts tamamlandı");
        } else if (document.getElementById('post-list')) {
            loadMorePosts();
            console.log("loadMorePosts tamamlandı");
        }

        console.log("initProfile yükleniyor...");
        if (typeof initProfile === 'function') {
            if (window.location.pathname.includes('/profile/')) {
                initProfile();
                console.log("initProfile tamamlandı");
            }
        } else {
            throw new Error("initProfile fonksiyonu tanımlı değil, modül yüklenemedi");
        }

        console.log("initEmojiPicker yükleniyor...");
        if (document.getElementById('emojiButton')) {
            initEmojiPicker();
            console.log("initEmojiPicker tamamlandı");
        } else {
            console.warn("Emoji picker için gerekli elementler bulunamadı");
        }
    } catch (e) {
        console.error("scripts.js genel hatası:", e.message, e.stack);
    }

    // URL'deki hash'e göre kaydırma
    const hash = window.location.hash;
    if (hash) {
        const postElement = document.querySelector(hash);
        if (postElement) {
            postElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
});