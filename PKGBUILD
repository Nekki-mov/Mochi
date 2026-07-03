# Maintainer: Nekki <nborrego2002@gmail.com>
pkgname=mochi
pkgver=0.1.0
pkgrel=1
pkgdesc="Graphical package manager for Wagashi Linux"
arch=('x86_64')
url="https://github.com/Nekki-mov/Mochi"
license=('GPL3')
depends=('python' 'python-pyqt6' 'yay')
source=("mochi.py::https://raw.githubusercontent.com/Nekki-mov/Mochi/main/src/mochi.py"
        "mochi.svg::https://raw.githubusercontent.com/Nekki-mov/Mochi/main/assets/mochi.svg"
        "mochi.desktop::https://raw.githubusercontent.com/Nekki-mov/Mochi/main/assets/mochi.desktop")
sha256sums=('b268d2330ff7c2d354308183276ad5109f13b2b29546c88249560b13edfda42c'
            '93c8591ffda5dbd3520479203e538f4cce118863f77aec54eefdd5603ddc3b4b'
            '1203fdc525c143ebbd1020ffd5d4cda5db6242b44dff7910edf2e0c7a8f9e0b0')

package() {
    install -Dm755 "$srcdir/mochi.py" "$pkgdir/usr/local/lib/mochi/mochi.py"
    install -Dm644 "$srcdir/mochi.svg" "$pkgdir/usr/share/icons/hicolor/scalable/apps/mochi.svg"
    install -Dm644 "$srcdir/mochi.desktop" "$pkgdir/usr/share/applications/mochi.desktop"
    install -dm755 "$pkgdir/usr/local/bin"
    cat > "$pkgdir/usr/local/bin/mochi" << 'WRAPPER'
#!/bin/bash
exec python3 /usr/local/lib/mochi/mochi.py "$@"
WRAPPER
    chmod 755 "$pkgdir/usr/local/bin/mochi"
}
