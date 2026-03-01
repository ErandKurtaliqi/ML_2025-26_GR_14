<div align="center">

<img src="dataset/assets/logo_up.png" alt="University of Prishtina" width="150"/>

# University of Prishtina

## Faculty of Electrical and Computer Engineering

**Study Program:** Computer and Software Engineering – Master  
**Course:** Machine Learning  
**Group:** 14  

# Tema

## Trajnimi dhe aplikimi i modelit YOLO për detektimin dhe vlerësimin automatik të testeve pranuese në FIEK

Ky projekt ka për qëllim zhvillimin e një sistemi inteligjent për **detektimin dhe vlerësimin automatik të testeve pranuese në Fakultetin e Inxhinierisë Elektrike dhe Kompjuterike (FIEK)** duke përdorur modelin **YOLO (You Only Look Once)** nga fusha e **Computer Vision dhe Machine Learning**.

Sistemi synon të analizojë imazhe të testeve të plotësuara nga kandidatët dhe të identifikojë në mënyrë automatike:

- Kodin e kandidatit
- Pozicionin e përgjigjeve në test
- Përgjigjet e shënuara nga kandidati
- Përgjigjet e sakta dhe numrin total të pikëve

Pas procesit të detektimit, sistemi analizon përgjigjet e identifikuara dhe llogarit **numrin e përgjigjeve të sakta**, duke mundësuar një proces të **automatizuar, të shpejtë dhe më të saktë të korrigjimit të testeve pranuese**.

Ky projekt synon të reduktojë:

- gabimet njerëzore gjatë korrigjimit
- kohën e nevojshme për analizimin e testeve
- ndërhyrjen manuale në procesin e vlerësimit

dhe të ofrojë një **zgjidhje të automatizuar të bazuar në inteligjencë artificiale për korrigjimin e testeve pranuese**.

---

# Dataset Creation

Për të trajnuar modelin YOLO është krijuar një **dataset i dedikuar**, i përbërë nga rreth **100 mostra (test sheets)** të ndryshme.

Këto mostra janë shpërndarë tek **persona të ndryshëm në mënyrë të rastësishme**, me qëllim që të krijohen **të dhëna sa më reale dhe të larmishme**. Personat që kanë plotësuar testet kanë përdorur stile të ndryshme të plotësimit, duke reflektuar mënyrat reale se si kandidatët mund të plotësojnë një test.

Dataset-i përfshin raste të ndryshme reale si:

- përgjigje të plota dhe të sakta
- përgjigje të gabuara
- pyetje të lëna pa përgjigje
- raste ku kandidati ka shënuar disa përgjigje për të njëjtën pyetje
- devijime në mënyrën e plotësimit të rrethit të përgjigjes
- mbushje jo të plotë të rrethit të përgjigjes
- shenja të pjesshme ose të paqarta
- shënime të bëra jashtë zonës së përgjigjes

Në disa raste janë përfshirë edhe situata ku:

- vijat e plotësimit janë devijuar
- përgjigjet janë shënuar pjesërisht
- kandidati ka ndryshuar përgjigjen
- përgjigjet janë bërë me intensitet të ndryshëm të stilolapsit ose lapsit

Këto variacione janë përfshirë që modeli të mësojë të trajtojë **situata reale dhe jo vetëm raste ideale**.

---

# Data Collection and Validation

Të gjitha testet janë **skanuar ose fotografuar në format imazhi**, pasi modeli YOLO trajnohet mbi **të dhëna vizuale (images)**.

Çdo imazh është kontrolluar manualisht përpara se të futet në dataset për të siguruar që:

- imazhi është i qartë dhe i lexueshëm
- nuk ka deformime të mëdha të dokumentit
- pozicioni i testit është i identifikueshëm
- të gjitha elementet e rëndësishme janë të dukshme

Pas këtij procesi është bërë një **kontroll i dytë manual i të dhënave**, ku janë verifikuar:

- integriteti i imazheve
- korrektësia e anotimeve
- mungesa e gabimeve në etiketim

Kjo është bërë për të siguruar një **dataset sa më cilësor dhe të pastër**, i cili është shumë i rëndësishëm për performancën e modelit.

---

# Data Annotation

Pas mbledhjes së të dhënave është realizuar procesi i **annotimit (etiketimit)** të imazheve.

Në këtë proces janë identifikuar dhe shënuar:

- zona e kodit të kandidatit
- zonat e përgjigjeve
- kutitë ose rrethet e përgjigjeve
- elementet e tjera relevante në test

Këto etiketime janë përdorur për të trajnuar modelin YOLO që të mësojë të identifikojë dhe klasifikojë objektet në mënyrë automatike.

---

# Model Training

Modeli YOLO trajnohet mbi dataset-in e krijuar duke përdorur **imazhe të testit dhe anotimet përkatëse**.

Procesi i trajnimit përfshin:

- përgatitjen e dataset-it
- ndarjen e dataset-it në **training set dhe validation set**
- konfigurimin e modelit YOLO
- trajnimin e modelit mbi imazhet e dataset-it
- evaluimin e performancës së modelit

Gjatë trajnimit modeli mëson të:

- detektojë pozicionin e përgjigjeve
- identifikojë përgjigjet e shënuara
- dallojë përgjigjet e sakta nga ato të gabuara
- analizojë strukturën e testit

---

# Expected Results

Pas përfundimit të trajnimit, sistemi pritet të jetë në gjendje që nga një **imazh i një testi të plotësuar** të gjenerojë automatikisht rezultatet në formën:
