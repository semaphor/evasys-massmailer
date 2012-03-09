#!/usr/bin/python
# -*- coding: UTF-8 -*-

# EvaSys Massmailer

# powering for uuulm and StuVe:
# simon.fuchs@uni-ulm.de, simon.lueke@uni-ulm.de

# Written and tested for Python 2.7.2+ on Ubuntu 11.10

"""

 Dokumentation
 =============


Skizze Vorgehen
---------------

1. Verschickung:

 * StuVe erstellt Umfrage in Evasys.
 * StuVe holt OK für die Verschickung von Zentraler Evaluation und Rechtsabteilung ein.
 * StuVe übergibt kiz Mailtext (mail.txt), Skript (mailit.py), und Liste mit TANs
   (tanlist.txt).
 * kiz generiert Liste mit Mailadressen aller Studierender
   (addresslist.txt).
 * kiz versendet die Mails (mittels Skript, Mailtext und beiden Listen)
   (python mailit.py erstversand).
 * kiz behält die Liste mit den Mailadressen!

Abwarten, c.a. 2 Wochen.

2. Verschickung (Erinnerung):

 * StuVe übergibt kiz eine neue Liste mit noch nicht genutzten TANs und einen angepassten Mailtext
   (tanslist-reminder.txt, mail-reminder.txt).
 * kiz versendet Erinnerungen, das Skript versendet dazu durch Abgleich beiden TAN-Listen nur noch an Personen, die noch nicht teilgenommen haben
   (python mailit.py erinnerung).
 * kiz löscht nach erfolgreicher 2. Verschickung alle verwendeten Dateien.


Informationen
-------------

 * Anzahl TANs (zeilenweise) in der TAN-Liste muss >= Anzahl der Emailadressen in der Adressliste (ebenfalls zeilenweise).
 * Reihenfolge der TANs in den beiden Listen muss gleich sein, die Listen liefert EvaSys bereits in dieser Form.
 * Dateien addresslist.txt, tanlist.txt und tanlist-reminder.txt am besten ohne Leerzeichen und Leerzeilen am Ende.
   Es kommst sonst evtl. zur Ausgabe von unnötigen Fehlermeldungen, Versand sollte aber trotzdem klappen.


Dateiformate
------------

$ file --version
file-5.04
magic file from /etc/magic:/usr/share/misc/magic

$ file *
addresslist.txt:                ASCII text
mailit.py:                      a /usr/bin/python script text executable
mail.txt:                       UTF-8 Unicode text
mail-reminder.txt:              UTF-8 Unicode text
tanlist.txt:                    ASCII text
tanlist-reminder.txt:           ASCII text


"""


# Konfiguration

# Liste aller Mailempfaenger, zeilenweise
addressFile = 'addresslist.txt'
# Liste der TANs, zeilenweise; -reminder.txt für Erinnerungsmail, gleiche Reihenfolge der verbliebenen TANs
tanFile = 'tanlist.txt'
tanFileReminder = 'tanlist-reminder.txt'
# Nachricht die gesendet werden soll, $TAN$ wird darin durch die TAN ersetzt; ebenfassl -reminder.txt
mailFile = 'mail.txt'
mailFileReminder = 'mail-reminder.txt'
# Encoding für die Mails (Möglichkeiten: 'iso-8859-1', 'iso-8859-15', 'utf-8')
mailEncoding = 'iso-8859-15'
# Erstversand oder Erinnerung, erstes und einziges Kommandozeilenargumen; Default: Erstversand <-> False
reminder = False
# Sekunden um evtl. Abbruch durch Nutzer vor dem Versand abzuwarten
sleepTime = 1

# Bibliotheken

import smtplib
from email.message import Message                                       # eigentliche Klasse für Emails
from email.header import Header                                         # um Umlaute im Header richtig kodieren zu können
from email.parser import Parser                                         # um aus einer Datei die Email "parsen" zu können
import sys                                                              # für Kommandozeilenargumente
import time                                                             # Wartezeit


# los gehts


# Kommandozeilenargument überprüfen
try:
    if ((len(sys.argv) != 2) or (sys.argv[1] not in ['erstversand', 'erinnerung'])):
        raise NameError('Arguemntfehler')
except:
    print '\n  Usage:   ' + sys.argv[0] + ' <versandart>\n\n     <versandart> = erstversand | erinnerung\n\n'
    sys.exit(1)
else:
    if sys.argv[1] == 'erinnerung':
        reminder = True
        print '\n(i) Beginne mit Versand von ERINNERUNGEN in ' + str(sleepTime) + ' Sekunden. CTRL-C um abzubrechen.\n\n'
        time.sleep(sleepTime)
    else:
        print '\n(i) Beginne mit Versand an GESAMTE LISTE in ' + str(sleepTime) + ' Sekunden. CTRL-C um abzubrechen.\n\n'
        time.sleep(sleepTime)


# TANs aus Dateien lesen
tans = []
tansReminder = []
print '(i) reading tans from ' + tanFile + '.'
for line in open(tanFile, 'r'):
    tans.append(line)
print '(i) got ' + str(len(tans)) + ' tans.\n'
if reminder:
    print '(i) reading remaining tans from ' + tanFileReminder + '.'
    for line in open(tanFileReminder, 'r'):
        tansReminder.append(line)
    print '(i) got ' + str(len(tansReminder)) + ' tans.\n'


# Email aus mailFile lesen, Zeichensätze auf ISO 8859-1 setzen
if not reminder:
    mail = Parser().parse(open(mailFile, 'rb'))
else:
    mail = Parser().parse(open(mailFileReminder, 'rb'))


myHeader = mail['Subject']
del mail['Subject']
mail['Subject'] = Header(myHeader, mailEncoding)

assert(mail.is_multipart() == False)
unicodeBody = unicode(mail.get_payload(None, True), 'utf-8')
mail.set_payload(unicodeBody.encode(mailEncoding), mailEncoding)

print '(i) summarized header of mail:'
print mail.items()
print


# Mailer initialisieren
print '(i) loading mailer...\n'
s = smtplib.SMTP('smtp.uni-ulm.de')


# Mails an alle Adressen aus addressFile senden
print '(i) sending mails, reading recipients from ' + addressFile + '.\n'

# counter fuer die TAN-Nummern
tanNr = 0
tanNrReminder = 0
tansReminderLength = len(tansReminder)
mailCount = 0

# Erste Mail muss $TAN$ ersetzten, dazu
tanNrLastSent = -1
tans.append('$TAN$')

# Abarbeiten
for line in open(addressFile, "r"):

    if reminder:
        if tanNrReminder >= tansReminderLength:
            print '\n\n(i) sent mails for all entries in ' + tanFileReminder
            break
        print '(i) processing TAN ' + tans[tanNr].rstrip() + ', looking for ' + tansReminder[tanNrReminder].rstrip()
        if tans[tanNr] != tansReminder[tanNrReminder]:
            tanNr += 1
            continue

    # To-Feld in Mailheader einfügen
    mail.__delitem__('To')
    mail['To'] = line.rstrip()
    try:
        print '(i) preparing and sending mail to: ' + mail['To'] + ' with TAN ' + tans[tanNr].rstrip()
        mail.set_payload(mail.get_payload().replace(tans[tanNrLastSent], tans[tanNr]))
        tanNrLastSent = tanNr
        s.sendmail(mail['From'], line, mail.as_string())

    # Fehlerbehandlung
    except smtplib.SMTPRecipientsRefused:
        print '\nERROR on sending mail to:' + line.rstrip() +'\n'
        sys.exit(2)

    mailCount += 1
    print '(i)     ... sent! (line ' + str(tanNr+1) + ' in ' + addressFile + ')'

    # damit wurde eine Mail versendet, also Zähler erhöhen
    tanNr += 1
    tanNrReminder += 1

# Ende

print '\n\n(i) Assuming to be done, please check if numbers are plausible.\n\n    Number of sent mails: ' + str(mailCount)


s.quit()


print '\n\n done.\n'



"""

Für Weiterentwicklungen
=======================

 *Encoding?
  * Quelldatei für Mails gleich in der Zielkodierung?
  * Welche Kodierung ist denn nun die am besten zu verwendende?
   * ISO 8859-1 hat z.B. kein €-Zeichen.
   * Alles in UTF-8? Dann ist's im Plaintext aber kaum lesbar.
  * Welches Encodung ist im From-Feld erlaubt? TB erzeugt bei Simon L. beim Uni-IMAP eine merkwürdige Darstellung.

 * Ersetzen der TANs könnte schöner gelöst werden.

 * newline am Ende von tan[] entfernen

 """
