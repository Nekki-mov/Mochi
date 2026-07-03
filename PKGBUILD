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
sha256sums=('SKIP' 'SKIP' 'SKIP')

package() {
    install -Dm755 "$srcdir/mochi.py" "$pkgdir/usr/local/lib/mochi/mochi.py"
    install -Dm644 "$srcdir/mochi.svg" "$pkgdir/usr/share/icons/hicolor/scalable/apps/mochi.svg"
    install -Dm644 "$srcdir/mochi.desktop" "$pkgdir/usr/share/applications/mochi.desktop"
    cat > "$pkgdir/usr/local/bin/mochi" << 'WRAPPER'
#!/bin/bash
exec python3 /usr/local/lib/mochi/mochi.py "$@"
WRAPPER
    chmod 755 "$pkgdir/usr/local/bin/mochi"
}
