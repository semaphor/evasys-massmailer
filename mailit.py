#!/usr/bin/python
# -*- coding: UTF-8 -*-

# EvaSys Massmailer

# powering for uuulm and StuVe:
# simon.fuchs@uni-ulm.de, simon.lueke@uni-ulm.de


"""

 Dokumentation
 =============


Skizze Vorgehen
---------------

1. Verschickung:

 * StuVe erstellt Umfrage in Evasys.
 * StuVe holt OK für die Verschickung von Zentraler Evaluation und Rechtsabteilung ein.
 * StuVe übergibt kiz Mailtext, Skript, ... und Liste mit TANs.
 * kiz generiert Liste mit Mailadressen aller Studierender.
 * kiz versendet die Mails (mittels Skript, Mailtext und beiden Listen): mailit.py
 * kiz löscht die Liste mit Mailadressen nicht!

Abwarten, c.a. 2 Wochen.

2. Verschickung (Erinnerung):

 * StuVe übergibt kiz eine neue Liste mit noch nicht genutzten TANs und ein weiteres Skript zum abgleich.
 * kiz gleicht alte und neue TAN-Liste mit der Liste der Mailadressen ab, Adressen deren TAN schon verwendet werden gelöscht: reminderlist.py
 * kiz versendet mit abgeglichener Liste von Mailadressen und neuer TAN-Liste eine Erinnerung.
 * kiz löscht nach erfolgreicher 2. Verschickung alle angefallenen Dateien.


Informationen
-------------

 * Anzahl TANs (zeilenweise) in der TAN-Liste muss >= Anzahl der Emailadressen in der Adressliste (ebenfalls zeilenweise).
 * Dateien addresslist.txt und tanlist.txt am besten ohne Leerzeichen und Leerzeilen am Ende, sons wird mit der letzten Zeile noch ein Fehler erzeugt.



Written and tested with Python 2.7.2+ on Ubuntu 11.10


Dateiformate
------------

$ file --version
file-5.04
magic file from /etc/magic:/usr/share/misc/magic

$ file *
addresslist.txt:     ASCII text
mailit.py:           a /usr/bin/python script text executable
mail.txt:            UTF-8 Unicode text
tanlist.txt:         ASCII text


"""


# Konfiguration

# Liste der TANs, zeilenweise
tanFile = 'tanlist.txt'
# Liste der Mailempfaenger, zeilenweise
addressFile = 'addresslist.txt'
# Nachricht die gesendet werden soll, $TAN$ wird darin durch die TAN ersetzt
mailFile = 'mail.txt'
# Encoding für die Mails (Möglichkeiten: 'iso-8859-1', 'iso-8859-15', 'utf-8')
mailEncoding = 'iso-8859-15'


# los gehts
import smtplib
from email.message import Message                                       # eigentliche Klasse für Emails
from email.header import Header                                         # um Umlaute im Header richtig kodieren zu können
from email.parser import Parser                                         # um aus einer Datei die Email "parsen" zu können


# TANs aus tanFile lesen
tans = []
print ("(i) reading tans from " + tanFile + ".")
for line in open(tanFile, 'r'):
    tans.append(line)
print ("(i) got " + str(len(tans)) + " tans.\n")


# Email aus mailFile lesen, Zeichensätze auf ISO 8859-1 setzen
mail = Parser().parse(open(mailFile, 'rb'))

myHeader = mail['Subject']
del mail['Subject']
mail['Subject'] = Header(myHeader, mailEncoding)

assert(mail.is_multipart() == False)
unicodeBody = unicode(mail.get_payload(None, True), 'utf-8')
mail.set_payload(unicodeBody.encode(mailEncoding), mailEncoding)

print("(i) summarized header of mail:\n")
print (mail.items())
print("")


# Mailer initialisieren
print ("(i) loading mailer...\n")
s = smtplib.SMTP('smtp.uni-ulm.de')


# Mails an alle Adressen aus addressFile senden
print ("(i) sending mails, reading recipients from " + addressFile + ".\n")
# counter fuer die tan-nummern und erste TAN einfügen
tannr = 0
mail.set_payload(mail.get_payload().replace('$TAN$',tans[tannr]))

# Abarbeiten
for line in open(addressFile, "r"):

    # To-Feld in Mailheader einfügen
        mail.__delitem__('To')
        mail['To'] = line.rstrip()
        try:
                print "(i) sending mail to: " + mail['To']                                        #.items()
                s.sendmail(mail['From'], line, mail.as_string())

    # Fehlerbehandlung
        except smtplib.SMTPRecipientsRefused:
                print ("ERROR on sending mail to:" + line.rstrip())
                break

        # nächste TAN einfuegen
        tannr += 1
        mail.set_payload(mail.get_payload().replace(tans[tannr-1], tans[tannr]))

        print ("(i) sent mail number "+str(tannr))

# Ende
s.quit()
print ("\n done.\n")



"""

Für spätere Versionen
=====================

 *Encoding?
  * Quelldatei für Mails gleich in der Zielkodierung?
  * Welche Kodierung ist denn nun die am besten zu verwendende?
   * ISO 8859-1 hat z.B. kein €-Zeichen.
   * Alles in UTF-8? Dann ist's im Plaintext aber kaum lesbar.
  * Welches Encodung ist im From-Feld erlaubt? TB erzeugt bei Simon L. beim Uni-IMAP eine merkwürdige Darstellung.

 * Ersetzen der TANs könnte schöner gelöst werden.

 """
