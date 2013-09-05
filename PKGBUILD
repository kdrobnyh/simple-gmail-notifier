# Based on the Gmail Notifier project: http://sourceforge.net/projects/gmail-notify/
# Maintainer: Klim Drobnyh <klim.drobnyh@gmail.com>

pkgname=simple-gmail-notifier
pkgver=1.2
pkgrel=0
pkgdesc="A Linux alternative for the notifier program released by Google, use libnotify for notifications"
arch=('any')
url="https://github.com/kdrobnyh/simple-gmail-notifier"
license=('GPL')
depends=('pygtk libnotify alsa-utils')
install=$pkgname.install
source=(http://downloads.sourceforge.net/$pkgname/$pkgname-$pkgver.tar.gz)
md5sums=('7d62330064b3cc70c674cb721f36975a')

build() {
  cd "$srcdir"/$pkgname
}

package() {
  install -dm755 "$pkgdir"/usr/bin
  install -dm755 "$pkgdir"/usr/share/simple-gmail-notifier

  cp -r "$srcdir"/$pkgname/*  "$pkgdir"/usr/share/simple-gmail-notifier/
  ln -s /usr/share/$pkgname/run.py "$pkgdir"/usr/bin/simple-gmail-notifier
}
