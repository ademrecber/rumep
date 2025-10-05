#!/usr/bin/env python3
"""
Static dosyaları optimize etmek için script
"""
import os
import gzip
import shutil
from pathlib import Path

def minify_css(css_content):
    """Basit CSS minification"""
    # Yorumları kaldır
    import re
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    # Fazla boşlukları kaldır
    css_content = re.sub(r'\s+', ' ', css_content)
    css_content = re.sub(r';\s*}', '}', css_content)
    css_content = re.sub(r'{\s*', '{', css_content)
    css_content = re.sub(r';\s*', ';', css_content)
    return css_content.strip()

def minify_js(js_content):
    """Basit JS minification"""
    import re
    # Tek satır yorumları kaldır
    js_content = re.sub(r'//.*$', '', js_content, flags=re.MULTILINE)
    # Çok satır yorumları kaldır
    js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
    # Fazla boşlukları kaldır
    js_content = re.sub(r'\s+', ' ', js_content)
    return js_content.strip()

def optimize_static_files():
    """Static dosyaları optimize et"""
    static_dir = Path('main/static/main')
    
    if not static_dir.exists():
        print("Static dizin bulunamadı")
        return
    
    # CSS dosyalarını optimize et
    css_dir = static_dir / 'css'
    if css_dir.exists():
        for css_file in css_dir.glob('**/*.css'):
            if css_file.name.endswith('.min.css'):
                continue
                
            print(f"CSS optimize ediliyor: {css_file}")
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            minified = minify_css(content)
            
            # .min.css olarak kaydet
            min_file = css_file.parent / f"{css_file.stem}.min.css"
            with open(min_file, 'w', encoding='utf-8') as f:
                f.write(minified)
            
            # Gzip versiyonu oluştur
            with open(min_file, 'rb') as f_in:
                with gzip.open(f"{min_file}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
    
    # JS dosyalarını optimize et
    js_dir = static_dir / 'js'
    if js_dir.exists():
        for js_file in js_dir.glob('**/*.js'):
            if js_file.name.endswith('.min.js'):
                continue
                
            print(f"JS optimize ediliyor: {js_file}")
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            minified = minify_js(content)
            
            # .min.js olarak kaydet
            min_file = js_file.parent / f"{js_file.stem}.min.js"
            with open(min_file, 'w', encoding='utf-8') as f:
                f.write(minified)
            
            # Gzip versiyonu oluştur
            with open(min_file, 'rb') as f_in:
                with gzip.open(f"{min_file}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

if __name__ == '__main__':
    optimize_static_files()
    print("Static dosya optimizasyonu tamamlandı!")