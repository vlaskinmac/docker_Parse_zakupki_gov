#!bin/bash
# apt-get update -y
# apt-get upgrade -y

# apt install -y nginx
# echo "daemon off;" >> /etc/nginx/nginx.conf
#sed '2 a\194.67.92.2  prod.offenbach-debussy.ru prod' /etc/hosts

debconf-set-selections <<< "postfix postfix/mailname string offenbach-debussy.ru"
debconf-set-selections <<< "postfix postfix/main_mailer_type string 'Internet Site'"


apt-get install -y postfix
postconf -e 'home_mailbox = Maildir/'
postconf -e 'virtual_alias_maps = hash:/etc/postfix/virtual'
echo -e "contact@offenbach-debussy.ru root" >> /etc/postfix/virtual
postmap /etc/postfix/virtual

postconf -e 'mydomain = offenbach-debussy.ru'
postconf -e "mydestination = offenbach-debussy.ru, prod.offenbach-debussy.ru, localhost.offenbach-debussy.ru, localhost"
postconf -e "mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128 194.67.92.2"

# systemctl restart postfix
# service postfix restart

echo 'export MAIL=~/Maildir' | tee -a /etc/bash.bashrc | tee -a /etc/profile.d/mail.sh
source /etc/profile.d/mail.sh

apt install s-nail
echo -e "text text" > ~/test_message

echo -e "set emptystart\nset folder=Maildir\nset record=+sent" >> /etc/s-nail.rc
echo 'ok'

echo 'init' | s-nail -s 'init' -Snorecord root

# /bin/sh -c bash

ls -R ~/Maildir

echo 'ok'


