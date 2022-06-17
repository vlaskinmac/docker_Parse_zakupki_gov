#!bin/bash

# must be installed postfix

#==========================================================
# install OpenDKIM
apt-get install -y opendkim opendkim-tools

# create new config
mv /etc/opendkim.conf /etc/backup.opendkim.conf

cat << EOF > /etc/opendkim.conf
AutoRestart             Yes
AutoRestartRate         10/1h
Umask                   002
Syslog                  yes
SyslogSuccess           Yes
LogWhy                  Yes
Canonicalization        relaxed/simple
ExternalIgnoreList      refile:/etc/opendkim/TrustedHosts
InternalHosts           refile:/etc/opendkim/TrustedHosts
KeyTable                refile:/etc/opendkim/KeyTable
SigningTable            refile:/etc/opendkim/SigningTable
Mode                    sv
PidFile                 /var/run/opendkim/opendkim.pid
SignatureAlgorithm      rsa-sha256
UserID                  opendkim:opendkim
Socket                  inet:12301@localhost
EOF

mkdir /etc/opendkim
cat << EOF > /etc/opendkim/TrustedHosts
127.0.0.1
localhost
194.67.92.2
offenbach-debussy.ru
EOF

touch /etc/opendkim/{KeyTable,SigningTable}
echo "SOCKET=inet:12301@localhost" >> /etc/default/opendkim


service opendkim restart

cat << EOF >> /etc/postfix/main.cf
milter_protocol = 2
milter_default_action = accept
smtpd_milters = inet:localhost:12301
non_smtpd_milters = inet:localhost:12301
EOF

service postfix restart

# create DKIM tokens
mkdir -p /etc/opendkim/offenbach-debussy.ru
opendkim-genkey -D /etc/opendkim/offenbach-debussy.ru/ --domain offenbach-debussy.ru --selector relay

useradd opendkim -m -s /sbin/nologin
chown :opendkim /etc/opendkim/offenbach-debussy.ru/*
chmod g+rw /etc/opendkim/offenbach-debussy.ru/*
echo "*.offenbach-debussy.ru" >> /etc/opendkim/TrustedHosts
cat << EOF > /etc/opendkim/KeyTable
relay._domainkey.offenbach-debussy.ru offenbach-debussy.ru:relay:/etc/opendkim/offenbach-debussy.ru/relay.private
EOF

echo "*@offenbach-debussy.ru relay._domainkey.offenbach-debussy.ru" > /etc/opendkim/SigningTable

service opendkim restart

echo 'DKIM token:'
echo '/etc/opendkim/offenbach-debussy.ru/relay.txt'
echo '========================================'
cat /etc/opendkim/offenbach-debussy.ru/relay.txt
echo '========================================'

