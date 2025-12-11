crackme asm x86-64 linux

pour compiler:
apt install nasm binutils
nasm -f elf64 fichier.asm -o fichier.o
ld fichier.o -o fichier
strip fichier => supprime les symbols de debug #optionnel

apres tu lances ./fichier et tu rentres le password.

nul.asm - facile
xor avec une cle qui change a chaque caractere

moyen.asm - moyen
hash djb2 + verifications sur certains caracteres

dur.asm - difficile
hash custom + contraintes sur les positions + mini vm avec son propre bytecode + chiffrement final
faut reverser le tout pour trouver le serial

solutions (spoiler):

nul.asm -> nlakhdari.fr
moyen.asm -> naysense.fr
dur.asm -> nays3ns3-hr.o7
