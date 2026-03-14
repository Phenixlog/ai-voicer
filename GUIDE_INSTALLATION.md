# AI Voicer — Guide d'installation complet

> Outil personnel de dictee vocale pour Mac. Maintiens la touche Option, parle, relache — ton texte apparait automatiquement.

---

## Ce dont tu as besoin

- Un Mac (MacBook, iMac, Mac Mini, Mac Pro, Mac Studio... n'importe quel Mac)
- Une connexion internet (pour telecharger les fichiers et pour la transcription vocale)
- Une cle API Mistral (gratuite) — on va la creer ensemble juste en dessous
- Environ 10 minutes de ton temps

---

## Etape 1 : Obtenir ta cle API Mistral

La cle API est un mot de passe special qui permet a AI Voicer de communiquer avec le service de transcription vocale de Mistral. Sans cette cle, l'outil ne peut pas fonctionner.

### 1.1 Creer un compte Mistral

1. Ouvre ton navigateur internet (Safari, Chrome, Firefox... celui que tu preferes)
2. Va sur le site : **https://console.mistral.ai**
3. Tu arrives sur une page de connexion. Clique sur **"Sign up"** (s'inscrire) en bas du formulaire
4. Tu peux t'inscrire avec :
   - Ton adresse email (tu devras confirmer par email)
   - Ou directement avec ton compte Google ou GitHub si tu en as un
5. Remplis le formulaire et valide. Si tu as utilise ton email, va dans ta boite mail pour cliquer sur le lien de confirmation

### 1.2 Generer ta cle API

1. Une fois connecte sur **console.mistral.ai**, regarde le menu de gauche
2. Clique sur **"API Keys"** (cles API)
3. Clique sur le bouton **"Create new key"** (creer une nouvelle cle)
4. Donne un nom a ta cle, par exemple `ai-voicer` (c'est juste pour te souvenir a quoi elle sert)
5. Clique sur **"Create"**
6. **IMPORTANT** : ta cle apparait une seule fois. Elle ressemble a quelque chose comme `sk-aBcDeFgHiJkLmNoPqRsTuVwXyZ123456`. Copie-la immediatement :
   - Clique sur l'icone de copie a cote de la cle, ou
   - Selectionne tout le texte de la cle, puis fais **Cmd + C** pour copier
7. Colle-la quelque part en securite pour le moment (dans l'app Notes par exemple), tu en auras besoin dans quelques minutes

> **Note** : Mistral offre un credit gratuit pour commencer. La transcription vocale consomme tres peu de credits — pour un usage personnel quotidien, ca revient a quelques centimes par mois tout au plus.

---

## Etape 2 : Installer Python (si pas deja installe)

Python est le langage de programmation utilise par AI Voicer. Ton Mac en a peut-etre deja une version. On va verifier.

### 2.1 Ouvrir le Terminal

Le Terminal est une application deja presente sur ton Mac qui permet de taper des commandes textuelles. Pas de panique, on va te guider commande par commande.

**Pour ouvrir le Terminal :**
1. Appuie sur **Cmd + Espace** (la barre d'espace). Ca ouvre Spotlight, la barre de recherche de ton Mac
2. Tape le mot **Terminal**
3. L'application "Terminal" apparait dans les resultats. Appuie sur **Entree** pour l'ouvrir

Tu vois maintenant une fenetre avec du texte et un curseur qui clignote. C'est le Terminal. Chaque commande que tu taperas ici sera suivie d'un appui sur la touche **Entree** pour l'executer.

> **Astuce** : tu peux aussi trouver le Terminal dans le dossier **Applications > Utilitaires > Terminal**.

### 2.2 Verifier si Python est installe

Dans le Terminal, tape cette commande puis appuie sur **Entree** :

```
python3 --version
```

**Deux cas possibles :**

- **Si tu vois quelque chose comme** `Python 3.11.5` (ou n'importe quel numero commencant par 3.9 ou plus) : Python est deja installe. Passe directement a l'Etape 3.

- **Si tu vois un message d'erreur** comme `command not found` ou si macOS te propose d'installer les "command line tools" : continue ci-dessous.

### 2.3 Installer Homebrew (le gestionnaire de paquets)

Si Python n'est pas installe, on va d'abord installer Homebrew, un outil qui facilite l'installation de logiciels sur Mac.

Copie et colle cette commande dans le Terminal (tu peux la selectionner, faire Cmd + C pour copier, puis Cmd + V pour coller dans le Terminal), puis appuie sur **Entree** :

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Ce qui va se passer :
- Le Terminal te demande ton **mot de passe Mac** (celui que tu tapes pour deverrouiller ton Mac). Quand tu le tapes, rien ne s'affiche a l'ecran — c'est normal, c'est une mesure de securite. Tape-le a l'aveugle et appuie sur **Entree**.
- Le Terminal te demande de confirmer l'installation. Appuie sur **Entree** quand il te le demande.
- L'installation prend quelques minutes. Laisse-le travailler. Tu verras beaucoup de texte defiler — c'est normal.

**Important — si tu as un Mac avec puce Apple Silicon (M1, M2, M3, M4...) :** a la fin de l'installation, Homebrew affiche un message avec deux commandes a executer. Elles ressemblent a ceci :

```
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Copie et colle ces deux commandes une par une dans le Terminal et appuie sur **Entree** apres chacune. Si tu ne le fais pas, la commande `brew` ne sera pas reconnue.

### 2.4 Installer Python avec Homebrew

Maintenant, tape cette commande et appuie sur **Entree** :

```
brew install python@3.12
```

Attends que l'installation se termine (1 a 2 minutes en general).

Pour verifier que tout s'est bien passe, tape :

```
python3 --version
```

Tu devrais voir `Python 3.12.x`. Si oui, c'est parfait, tu peux passer a l'etape suivante.

---

## Etape 3 : Telecharger AI Voicer

Il y a deux facons de telecharger AI Voicer. Choisis celle qui te convient.

### Option A : Avec git (recommande)

Git est probablement deja installe sur ton Mac. Dans le Terminal, tape :

```
git --version
```

Si tu vois un numero de version (par exemple `git version 2.39.0`), git est installe. Tape alors :

```
cd ~/Documents && git clone https://github.com/Phenixlog/ai-voicer.git
```

> **Explication** : `cd ~/Documents` te deplace dans ton dossier Documents. `git clone` telecharge le projet depuis internet.

### Option B : Telecharger le ZIP (si git n'est pas installe)

1. Va sur **https://github.com/Phenixlog/ai-voicer** avec ton navigateur
2. Clique sur le bouton vert **"Code"** puis sur **"Download ZIP"**
3. Le fichier ZIP se telecharge dans ton dossier **Telechargements**
4. Double-clique sur le fichier ZIP pour le decompresser
5. Deplace le dossier decompresse dans ton dossier **Documents** :
   - Ouvre le Finder
   - Va dans Telechargements
   - Fais glisser le dossier `ai-voicer` (ou `ai-voicer-main`) dans **Documents**

Si tu as renomme le dossier ou s'il s'appelle `ai-voicer-main`, renomme-le en `ai-voicer` pour simplifier la suite.

---

## Etape 4 : Lancer l'installation

### 4.1 Se placer dans le bon dossier

Dans le Terminal, tape cette commande pour aller dans le dossier AI Voicer :

```
cd ~/Documents/ai-voicer
```

> **Explication** : `cd` signifie "change directory" — ca deplace le Terminal dans le dossier que tu indiques. Le `~` represente ton dossier personnel (par exemple `/Users/tonprenom`).

Pour verifier que tu es au bon endroit, tape :

```
ls
```

Tu devrais voir une liste de fichiers contenant notamment `install.sh`, `requirements.txt`, `src/`, etc. Si tu vois ces fichiers, tu es au bon endroit.

### 4.2 Rendre le script executable

Tape cette commande :

```
chmod +x install.sh
```

> **Explication** : cette commande donne la "permission d'execution" au fichier `install.sh`. Sans ca, ton Mac refuserait de le lancer.

### 4.3 Lancer l'installation

Tape cette commande :

```
./install.sh
```

Voici ce qui va se passer, etape par etape :

1. **Verification de Python** : le script verifie que Python 3 est installe. Si tu as fait l'etape 2, tout ira bien.

2. **Copie des fichiers** : le script copie les fichiers necessaires dans le dossier `~/.ai-voicer/` (c'est un dossier cache dans ton dossier personnel).

3. **Installation des dependances Python** : le script cree un environnement Python isole et installe les bibliotheques necessaires (traitement audio, communication avec Mistral, etc.). Ca peut prendre 1 a 2 minutes.

4. **Demande de ta cle API** : le script affiche :
   ```
   Enter your Mistral API key (get one at https://console.mistral.ai):
   ```
   C'est le moment de coller ta cle API Mistral que tu as copiee a l'Etape 1 :
   - Fais **Cmd + V** pour coller
   - Ta cle apparait dans le Terminal
   - Appuie sur **Entree**

5. **Configuration automatique** : le script cree le fichier de configuration avec ta cle et les reglages par defaut (langue francaise, touche Option comme declencheur, etc.).

6. **Demarrage automatique** : le script configure AI Voicer pour demarrer automatiquement a chaque connexion sur ton Mac, puis le lance immediatement.

Tu devrais voir le message :
```
=== Installation complete! ===
```

Suivi d'informations sur les fichiers de logs et de configuration.

---

## Etape 5 : Accorder les permissions macOS

C'est l'etape la plus importante. macOS protege ta vie privee en demandant explicitement la permission avant qu'un programme puisse utiliser ton microphone, simuler des frappes clavier, ou surveiller tes touches. AI Voicer a besoin de ces trois permissions pour fonctionner.

**Quand tu lances AI Voicer pour la premiere fois, macOS peut afficher des fenetres de dialogue te demandant d'autoriser l'acces. Clique toujours sur "Autoriser" ou "OK".**

Si les fenetres de dialogue n'apparaissent pas, ou si tu as clique sur "Ne pas autoriser" par erreur, voici comment accorder chaque permission manuellement.

### 5.1 Ouvrir les Reglages Systeme

- Clique sur le menu **Pomme** (en haut a gauche de l'ecran)
- Clique sur **Reglages Systeme** (ou "Preferences Systeme" sur les versions plus anciennes de macOS)

### 5.2 Microphone

AI Voicer a besoin d'acceder a ton microphone pour enregistrer ta voix.

1. Dans Reglages Systeme, clique sur **Confidentialite et securite** dans la barre laterale gauche
2. Clique sur **Microphone** dans la liste de droite
3. Cherche **Terminal** (ou **Python**) dans la liste des applications
4. Active l'interrupteur a cote (le curseur doit etre en position bleue/activee)
5. Si Terminal ou Python n'apparait pas dans la liste, c'est normal — l'application s'ajoutera automatiquement la premiere fois que tu utiliseras AI Voicer. Reviens ici apres ton premier test (Etape 6) si ca ne marche pas.

> **Note** : macOS peut te demander de fermer et rouvrir Terminal pour que le changement prenne effet. Fais-le si demande.

### 5.3 Accessibilite

Cette permission permet a AI Voicer de coller le texte transcrit dans n'importe quelle application (Notes, Word, Safari, etc.) en simulant un Cmd+V.

1. Dans **Confidentialite et securite**, clique sur **Accessibilite**
2. Cherche **Terminal** ou **Python** dans la liste
3. S'il apparait, active l'interrupteur
4. S'il n'apparait pas :
   - Clique sur le bouton **+** en bas de la liste
   - macOS te demande ton mot de passe — tape-le et valide
   - Une fenetre de selection de fichier s'ouvre
   - Navigue vers : `/Users/tonprenom/.ai-voicer/app/.venv/bin/` (pour y acceder, dans la fenetre de selection, appuie sur **Cmd + Shift + G** et colle ce chemin en remplacant `tonprenom` par ton nom d'utilisateur Mac)
   - Selectionne le fichier **python3** et clique sur **Ouvrir**
   - L'interrupteur doit etre active (bleu)

> **Astuce** : pour connaitre ton nom d'utilisateur Mac, tape `whoami` dans le Terminal.

### 5.4 Surveillance de l'entree (Input Monitoring)

Cette permission permet a AI Voicer de detecter quand tu appuies sur la touche Option pour commencer/arreter l'enregistrement.

1. Dans **Confidentialite et securite**, clique sur **Surveillance de l'entree**
2. Cherche **Terminal** ou **Python** dans la liste
3. Active l'interrupteur
4. Si l'application n'est pas dans la liste, suis la meme procedure que pour l'Accessibilite (bouton **+**, navigation vers python3)

### 5.5 Verification rapide

Apres avoir accorde les permissions, il est recommande de redemarrer AI Voicer pour etre sur que tout est pris en compte. Dans le Terminal, tape :

```
launchctl stop com.aivoicer.daemon && launchctl start com.aivoicer.daemon
```

---

## Etape 6 : Premier test

C'est le moment de verite !

### 6.1 Preparer une zone de texte

Ouvre n'importe quelle application ou tu peux taper du texte :
- **Notes** (l'app Notes de ton Mac — ouvre-la avec Cmd + Espace, tape "Notes", Entree)
- **TextEdit** (editeur de texte basique)
- Un email dans Mail
- La barre de recherche de Safari
- Un document Word ou Google Docs
- N'importe quel champ de texte

**Clique dans la zone de texte** pour t'assurer que le curseur est bien positionne la ou tu veux que le texte apparaisse.

### 6.2 Dicter

1. **Maintiens la touche Option enfoncee** — c'est la touche marquee **"Option"** ou **"Alt"** sur ton clavier, situee entre les touches Ctrl et Cmd en bas a gauche (et aussi en bas a droite)
2. **Parle clairement** dans le microphone de ton Mac. Dis par exemple : "Ceci est un test de dictee vocale"
3. **Relache la touche Option**
4. Attends une a deux secondes — AI Voicer envoie ton enregistrement a Mistral pour la transcription
5. Le texte transcrit apparait automatiquement la ou ton curseur etait positionne

> **Indicateur visuel** : par defaut, un petit indicateur (HUD) apparait sur ton ecran pour te montrer quand AI Voicer enregistre. Tu devrais voir un signal visuel quand tu maintiens Option.

Si le texte apparait, felicitations, tout fonctionne !

Si rien ne se passe, consulte la section Depannage plus bas.

---

## Utilisation quotidienne

### Demarrage automatique

AI Voicer est configure pour demarrer automatiquement chaque fois que tu te connectes a ton Mac. Tu n'as rien a faire — il tourne en arriere-plan silencieusement.

### Comment dicter

Le fonctionnement est simple et toujours le meme :

1. Clique dans un champ de texte (email, document, navigateur, notes...)
2. Maintiens la touche **Option** enfoncee
3. Parle
4. Relache **Option**
5. Le texte apparait

Par defaut, chaque enregistrement est limite a 2 minutes. Tu peux ajuster cette duree dans la configuration si besoin.

### Historique des transcriptions

Toutes tes transcriptions sont enregistrees dans un fichier de log. Pour les consulter :

```
cat ~/.ai-voicer/transcriptions.log
```

Ou ouvre le fichier avec TextEdit :

```
open -a TextEdit ~/.ai-voicer/transcriptions.log
```

### Demarrer / Arreter manuellement

Pour arreter AI Voicer :
```
launchctl stop com.aivoicer.daemon
```

Pour le redemarrer :
```
launchctl start com.aivoicer.daemon
```

Pour le lancer une seule fois sans le service automatique :
```
~/.ai-voicer/start.sh
```

---

## Configuration

AI Voicer se configure via un fichier texte simple. Voici comment le modifier.

### Ouvrir le fichier de configuration

Dans le Terminal, tape :

```
open -a TextEdit ~/.ai-voicer/.env
```

Ou si tu preferes le modifier dans le Terminal :

```
nano ~/.ai-voicer/.env
```

> **Note** : si tu utilises `nano`, tape tes modifications, puis appuie sur **Ctrl + O** pour sauvegarder (puis Entree pour confirmer), et **Ctrl + X** pour quitter.

### Options disponibles

Voici les options que tu peux modifier :

#### Cle API

```
MISTRAL_API_KEY=ta_cle_ici
```

Ta cle API Mistral. Ne la partage avec personne.

#### Touche de declenchement

```
AI_VOICER_HOTKEY=option
```

La touche que tu maintiens enfoncee pour dicter. Valeurs possibles :

| Valeur | Touche correspondante |
|--------|-----------------------|
| `option` | Option / Alt (par defaut) |
| `cmd` ou `command` | Cmd |
| `ctrl` | Controle |
| `shift` | Maj |
| `f5` | Touche F5 |
| `f6` | Touche F6 |
| `f7` | Touche F7 |
| `f8` | Touche F8 |
| `f9` | Touche F9 |
| `f10` | Touche F10 |
| `f11` | Touche F11 |
| `f12` | Touche F12 |

> **Conseil** : si tu utilises souvent la touche Option pour des raccourcis clavier (caracteres speciaux comme @, #, etc.), choisis une touche F a la place, par exemple `f8`.

#### Mode de declenchement

```
AI_VOICER_TRIGGER_MODE=hold
```

- `hold` (par defaut) : maintiens la touche enfoncee pour enregistrer, relache pour arreter
- `toggle` : appuie une fois pour commencer, une fois pour arreter

#### Langue

```
AI_VOICER_LANGUAGE=fr
```

La langue dans laquelle tu parles. Exemples :
- `fr` — francais
- `en` — anglais
- `es` — espagnol
- `de` — allemand
- `it` — italien
- Laisse vide pour la detection automatique

#### Structuration du texte

```
AI_VOICER_ENABLE_STRUCTURING=true
```

Quand cette option est activee (`true`), AI Voicer ameliore la mise en forme du texte transcrit (ponctuation, majuscules, paragraphes). Mets `false` pour obtenir la transcription brute.

#### Indicateur visuel (HUD)

```
AI_VOICER_HUD_ENABLED=true
```

Affiche un indicateur sur l'ecran quand l'enregistrement est en cours. Mets `false` pour le desactiver.

#### Reduction du volume systeme

```
AI_VOICER_DUCK_OUTPUT_AUDIO=true
```

Quand cette option est activee, le volume de la musique ou des sons systeme est automatiquement baisse pendant l'enregistrement, pour eviter que ces sons parasitent ta dictee. Mets `false` pour desactiver.

#### Niveau de log

```
AI_VOICER_LOG_LEVEL=INFO
```

Controle le detail des messages de log. Valeurs possibles :
- `DEBUG` — tres detaille (utile pour diagnostiquer un probleme)
- `INFO` — normal (par defaut)
- `WARNING` — peu de messages
- `ERROR` — uniquement les erreurs

#### Duree maximum d'enregistrement

```
AI_VOICER_MAX_RECORD_SECONDS=120
```

Duree maximale d'un seul enregistrement en secondes. Par defaut : 120 secondes (2 minutes). C'est une securite : si le relachement de la touche n'est pas detecte, l'enregistrement s'arrete automatiquement apres cette duree.

### Appliquer les modifications

Apres avoir modifie le fichier `.env`, redemarre AI Voicer pour que les changements prennent effet :

```
launchctl stop com.aivoicer.daemon && launchctl start com.aivoicer.daemon
```

---

## Depannage

### "Rien ne se passe quand j'appuie sur Option"

**Cause la plus frequente** : les permissions macOS ne sont pas accordees.

1. Verifie les trois permissions de l'Etape 5 (Microphone, Accessibilite, Surveillance de l'entree)
2. Verifie que le daemon tourne. Dans le Terminal, tape :
   ```
   ps aux | grep ai-voicer
   ```
   Tu devrais voir une ligne contenant `python3 run_daemon.py`. Si tu ne la vois pas (tu ne vois que la ligne `grep`), le daemon ne tourne pas.
3. Relance le daemon :
   ```
   launchctl stop com.aivoicer.daemon
   launchctl start com.aivoicer.daemon
   ```
4. Si ca ne marche toujours pas, lance AI Voicer manuellement pour voir les messages d'erreur :
   ```
   ~/.ai-voicer/start.sh
   ```
   Les erreurs s'afficheront directement dans le Terminal.

### "Le texte ne se colle pas"

Le microphone fonctionne, tu entends/vois l'enregistrement, mais le texte transcrit ne s'insere pas dans l'application.

1. Verifie que la permission **Accessibilite** est bien accordee (Etape 5.3)
2. Assure-toi d'avoir clique dans un champ de texte **avant** de commencer a dicter. Le curseur doit clignoter dans une zone de saisie
3. Essaie dans une autre application (Notes, TextEdit) pour isoler le probleme
4. Certaines applications bloquent le collage automatique — c'est rare mais ca existe

### "La transcription est mauvaise" ou "Il y a beaucoup d'erreurs"

1. **Parle clairement** et a un volume normal
2. **Rapproche-toi du microphone** de ton Mac (sur un MacBook, il est generalement pres de la camera)
3. **Reduis le bruit de fond** : eteins la musique, ferme la fenetre, eloigne-toi des sources de bruit
4. Verifie que la **langue** dans le fichier `.env` correspond a la langue dans laquelle tu parles. Si tu parles en anglais mais que la langue est `fr`, les resultats seront mauvais
5. Si tu utilises un casque avec microphone, assure-toi qu'il est selectionne comme source audio dans **Reglages Systeme > Son > Entree**

### "Erreur de cle API" ou "MISTRAL_API_KEY is missing"

1. Ouvre le fichier de configuration :
   ```
   open -a TextEdit ~/.ai-voicer/.env
   ```
2. Verifie que la ligne `MISTRAL_API_KEY=...` contient bien ta cle (pas d'espaces avant ou apres le `=`, pas de guillemets)
3. Verifie que ta cle est toujours valide sur **https://console.mistral.ai** dans la section API Keys
4. Apres correction, redemarre :
   ```
   launchctl stop com.aivoicer.daemon && launchctl start com.aivoicer.daemon
   ```

### "Comment voir les logs"

Les logs contiennent des informations detaillees sur ce que fait AI Voicer. Utiles pour diagnostiquer un probleme.

**Logs du daemon (fonctionnement general) :**
```
cat ~/.ai-voicer/daemon-stdout.log
cat ~/.ai-voicer/daemon-stderr.log
```

**Historique des transcriptions :**
```
cat ~/.ai-voicer/transcriptions.log
```

**Voir les logs en temps reel** (les messages s'affichent au fur et a mesure) :
```
tail -f ~/.ai-voicer/daemon-stderr.log
```

Pour arreter le suivi en temps reel, appuie sur **Ctrl + C**.

**Augmenter le detail des logs :**
Change `AI_VOICER_LOG_LEVEL=INFO` en `AI_VOICER_LOG_LEVEL=DEBUG` dans le fichier `.env` et redemarre.

### "Comment arreter AI Voicer"

Pour l'arreter temporairement (il redemarrera au prochain login) :
```
launchctl stop com.aivoicer.daemon
```

Pour le desactiver completement (il ne redemarrera plus au login) :
```
launchctl unload ~/Library/LaunchAgents/com.aivoicer.daemon.plist
```

Pour le reactiver apres un `unload` :
```
launchctl load ~/Library/LaunchAgents/com.aivoicer.daemon.plist
launchctl start com.aivoicer.daemon
```

### "Comment desinstaller completement"

Si tu veux supprimer AI Voicer de ton Mac :

1. Arrete et desactive le service :
   ```
   launchctl unload ~/Library/LaunchAgents/com.aivoicer.daemon.plist
   ```

2. Supprime le fichier de demarrage automatique :
   ```
   rm ~/Library/LaunchAgents/com.aivoicer.daemon.plist
   ```

3. Supprime les fichiers d'AI Voicer :
   ```
   rm -rf ~/.ai-voicer
   ```

4. Optionnel — supprime le dossier source telecharge :
   ```
   rm -rf ~/Documents/ai-voicer
   ```

C'est tout, AI Voicer est completement supprime.

### "Comment mettre a jour"

1. Va dans le dossier du projet :
   ```
   cd ~/Documents/ai-voicer
   ```

2. Si tu as utilise git pour telecharger, mets a jour les sources :
   ```
   git pull
   ```

3. Relance l'installation :
   ```
   ./install.sh
   ```

Le script conservera ta cle API et ta configuration existante (fichier `.env`). Il ne te redemandera pas ta cle.

---

## Raccourcis utiles

| Action | Comment |
|--------|---------|
| Dicter du texte | Maintenir **Option** + parler, puis relacher |
| Voir les transcriptions | `cat ~/.ai-voicer/transcriptions.log` |
| Redemarrer AI Voicer | `launchctl stop com.aivoicer.daemon && launchctl start com.aivoicer.daemon` |
| Voir les logs | `cat ~/.ai-voicer/daemon-stderr.log` |
| Voir les logs en direct | `tail -f ~/.ai-voicer/daemon-stderr.log` |
| Arreter AI Voicer | `launchctl stop com.aivoicer.daemon` |
| Modifier la configuration | `open -a TextEdit ~/.ai-voicer/.env` |
| Verifier que le daemon tourne | `ps aux \| grep ai-voicer` |

---

> Tu as suivi toutes les etapes et tout fonctionne ? Parfait. Tu peux maintenant fermer le Terminal, il n'est plus necessaire. AI Voicer tourne en arriere-plan et demarrera automatiquement a chaque ouverture de session sur ton Mac. Maintiens Option, parle, relache — c'est tout.
