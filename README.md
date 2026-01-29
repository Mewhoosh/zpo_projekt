# Racing Game with Reinforcement Learning

## 1. Przeznaczenie Aplikacji

Aplikacja to gra wyścigowa 2D z możliwością trenowania agentów AI przy użyciu technik Reinforcement Learning. Projekt łączy klasyczną grę zręcznościową (sterowanie pojazdem na torze) z zaawansowanym uczeniem maszynowym, umożliwiając:

- **Grę manualną** - użytkownik steruje pojazdem za pomocą klawiatury
- **Trening AI** - możliwość uczenia agentów autonomicznych
- **Wizualizację postępów** - obserwacja jak AI uczy się jazdy

Projekt powstał jako demonstracja wykorzystania programowania obiektowego oraz algorytmów Reinforcement Learning w praktyce.

---

## 2. Funkcjonalności Aplikacji

### Tryb Gry Manualnej
- Sterowanie pojazdem za pomocą WSAD


### Tryb Treningu AI
- Trening agentów przy użyciu algorytmu **PPO** (Proximal Policy Optimization)

### Tryb Obserwacji AI
- **watch.py** - obserwacja wytrenowanego agenta (jazda w nieskończoność)
- **watch_progress.py** - wizualizacja postępów uczenia (porównanie modeli z różnych etapów treningu)

### System Torów
- Wczytywanie torów z plików PNG

### Obserwacje AI (Raycasting)
Agent AI widzi otoczenie poprzez:
- **7 raycastów** - detekcja odległości do ścian w różnych kierunkach

**Co to są raycasty?**
Raycasty to wirtualne "promienie" wystrzeliwane z pojazdu w różnych kierunkach (np. -90°, -60°, -30°, 0°, 30°, 60°, 90°). Każdy promień mierzy odległość do najbliższej ściany. Dzięki temu agent wie, jak daleko znajdują się przeszkody wokół niego - to jak "widzenie" robota. Im bliżej ściana, tym mniejsza wartość raycastu.

---

## 3. Wymagania Systemowe i Sprzętowe

- **Python**: 3.10 lub nowszy
- **RAM**: 8 GB (zalecane 16 GB dla treningu)
- **Procesor**: Dowolny wielordzeniowy (zalecane 4+ rdzenie dla treningu)
- **Miejsce na dysku**: 500 MB

---

## 4. Sposób Instalacji

### Krok 1: Sklonuj Repozytorium
```bash
git clone https://github.com/mewhoosh/zpo_projekt
cd zpo_projekt
```

### Krok 2: Utwórz Wirtualne Środowisko
```bash
python -m venv .venv
```

### Krok 3: Aktywuj Środowisko
**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### Krok 4: Zainstaluj Zależności
```bash
pip install -r requirements.txt
```

### Krok 5: (Opcjonalnie) Utwórz Własny Tor
Utwórz plik PNG w folderze `tracks/` zgodnie z następującymi zasadami:
- **Czarny (0,0,0)** - ściana/przeszkoda
- **Biały (255,255,255)** - tor do jazdy
- **Żółty (255,255,0)** - linia startu/mety
- **Zielony (0,255,0)** - checkpoint 1
- **Niebieski (0,0,255)** - checkpoint 2
- **Czerwony (255,0,0)** - checkpoint 3

---

## 5. Sposób Użycia

### Gra Manualna
```bash
python main.py
```
**Sterowanie:**
- `W` - przyspieszanie
- `S` - cofanie
- `A` - skręt w lewo
- `D` - skręt w prawo
- `V` - pokazanie/ukrycie raycastów
- `C` - pokazanie/ukrycie checkpointów
- `ESC` - wyjście z gry

---

### Trening Agenta AI
```bash
python train.py
```

**Parametry do edycji w `train.py`:**
- `SAVE_PATH` - folder dla modeli (np. "models/v5")
- `TRACK_FILE` - ścieżka do toru (np. "tracks/test.png")
- `TOTAL_TIMESTEPS` - liczba kroków treningu (domyślnie 100,000)
- `N_ENVS` - liczba równoległych środowisk (domyślnie 8)

**Zapisywane pliki:**
- Modele co 10,000 kroków: `racing_ppo_10000_steps.zip`, `racing_ppo_20000_steps.zip`, ...
- Finalny model: `racing_ppo_final.zip`
- Wykres postępów: `training_plot.png`
- Konfiguracja treningu: `config.txt`

---

### Obserwacja Wytrenowanego Agenta

#### Jazda Ciągła (nieskończona)
```bash
python watch.py
```
Agent jeździ w nieskończoność - obserwacja ostatecznego modelu.

**Parametry:**
- `model_path` - ścieżka do modelu (np. "models/v3/racing_ppo_final.zip")
- `track_file` - tor do jazdy

#### Porównanie Postępów Treningu
```bash
python watch_progress.py
```
Pokazuje modele z różnych etapów (10k, 20k, 30k... kroków).

**Sterowanie:**
- `ENTER` - przeskocz do następnego modelu (wciśnij 2x)
- `ESC` - zakończ

**Parametry w `watch_progress.py`:**
- `model_dir` - folder z modelami (np. "models/v3")
- `track_file` - tor do testowania

---

## 6. Wykorzystane Narzędzia i Biblioteki

| Biblioteka | Wersja | Cel |
|------------|--------|-----|
| **pygame** | 2.5.2 | Grafika, sterowanie, renderowanie |
| **numpy** | 1.26.4 | Operacje matematyczne, macierze |
| **pillow** | 10.1.0 | Wczytywanie i przetwarzanie obrazów (tory PNG) |
| **gymnasium** | 0.29.1 | Framework dla środowisk RL (następca OpenAI Gym) |
| **stable-baselines3** | 2.2.1 | Implementacja algorytmów RL (PPO) |
| **torch** | 2.1.0 | Backend dla sieci neuronowych |
| **matplotlib** | 3.8.0 | Generowanie wykresów postępów |

---

## 7. Wykorzystanie Cech Programowania Obiektowego

Projekt w pełni wykorzystuje paradygmat obiektowy poprzez trzy kluczowe cechy:

### Hermetyzacja

**Przykłady w projekcie:**
- **Track** - przechowuje mapę jako tablice pikseli i dane o checkpointach. Na zewnątrz daje tylko proste metody:
  - `is_collision(x, y)` - sprawdza kolizję, szczegóły mapy są ukryte
  - `get_checkpoint_progress()` - zwraca postęp
  - Dane prywatne (z `_`): `_track_map`, `_checkpoints`, `_cache` - dostęp tylko wewnątrz klasy

- **PhysicsEngine** -  na zewnątrz proste metody:
  - `apply_input(vehicle, gas, brake, steering)` - stosuje sterowanie
  - `update(vehicle, dt)` - aktualizuje fizykę

- **TrackLoader** - skanuje PNG i zapisuje do cache, na zewnątrz:
  - `load_from_png(filepath)` - zwraca gotowe dane

### Dziedziczenie

**Hierarchia w projekcie:**
```
Vehicle (klasa bazowa)
  ├── PlayerCar (sterowanie klawiaturą)
  └── AICar (sterowanie przez model RL + raycasting)
```

- **Vehicle** (klasa bazowa) - definiuje wspólne cechy wszystkich pojazdów:
  - Atrybuty: `position`, `velocity`, `angle`, `width`, `height`
  - Metody: `draw()`, `get_position()`, `reset()`

- **PlayerCar** (klasa pochodna) - dziedziczy wszystko z `Vehicle` i dodaje:
  - `handle_input()` - obsługa klawiatury (WSAD)
  - Rozszerza bazową funkcjonalność o interakcję z graczem

- **AICar** (klasa pochodna) - dziedziczy z `Vehicle` i dodaje:
  - `cast_rays()` - raycasting dla obserwacji środowiska
  - `get_observation()` - zwraca stan dla modelu RL
  - `perform_action(action)` - wykonuje akcję z modelu

### Polimorfizm
Różne klasy mogą być używane przez ten sam interfejs.

**Przykłady w projekcie:**
- **Renderer.draw_vehicle(vehicle: Vehicle)** - przyjmuje dowolny obiekt typu `Vehicle`:
  ```python
  #Renderer nie wie czy to PlayerCar czy AICar
  renderer.draw_vehicle(player_car)  # działa
  renderer.draw_vehicle(ai_car)      # też działa
  ```
  Obie klasy mają metodę `draw()`, więc renderer może je traktować identycznie.

- **GameEngine** - akceptuje dowolny obiekt `Vehicle`:
  ```python
  game = GameEngine(track, vehicle=PlayerCar(...))  # tryb gracza
  game = GameEngine(track, vehicle=AICar(...))     # tryb AI
  ```
  Silnik gry nie musi wiedzieć jaki typ pojazdu obsługuje - wszystkie mają ten sam interfejs.

- **PhysicsEngine.update(vehicle)** - działa z każdym pojazdem:
  ```python
  physics.update(player_car, dt)  # aktualizuje fizykę gracza
  physics.update(ai_car, dt)      # aktualizuje fizykę AI
  ```

---

## 8. Algorytm Reinforcement Learning

### PPO (Proximal Policy Optimization)
Algorytm uczenia ze wzmocnieniem - najczęściej używany, stabilny i uniwersalny.

**Jak działa:**
1. **Zbieranie danych** - Agent jeździ po torze i zapisuje co widział (raycasty), co zrobił (skręt/gaz) i co dostał (nagroda)
2. **Obliczanie prawdopodobieństw** - PPO oblicza prawdopodobieństwo każdej akcji. Np. "jechać prosto" 60%, "skręcić w lewo" 30%, "cofać" 10%
3. **Ocena** - Sprawdza czy akcja była lepsza niż oczekiwano
4. **Aktualizacja** - Zwiększa prawdopodobieństwo dobrych akcji (20% → 40%) i zmniejsza złych (30% → 10%)
5. **Ograniczenie zmian** - Nie pozwala na zbyt duże skoki, żeby nie zepsuć tego co agent już się nauczył

### Akcje Dyskretne (5 możliwości)
Agent wybiera jedną z 5 akcji w każdym kroku:
- **0**: Nic (dryfowanie)
- **1**: Gaz (przyspieszanie)
- **2**: Gaz + Lewo (skręt podczas przyspieszania)
- **3**: Gaz + Prawo (skręt podczas przyspieszania)
- **4**: Cofanie (ucieczka z impasu)

### Obserwacje (9 wartości)
Agent widzi:
- **7 raycastów** - odległości do ścian (kąty: -90°, -60°, -30°, 0°, 30°, 60°, 90°)
- **Prędkość** - jak szybko jedzie
- **Odległość do checkpointu** - jak daleko do celu

### System Nagród
- **+200** za checkpoint
- **+1000** za okrążenie
- **+bonus** za szybkie okrążenie (do +500)
- **-5** za kolizję ze ścianą
- **+postęp** za zbliżanie się do checkpointu
- **+0.05** za jazdę (prędkość > 0.5)

### Parametry Treningu (v3)
- **Learning rate**: 0.0003
- **Równoległych środowisk**: 8 (SubprocVecEnv)
- **Kroki na rollout**: 2048
- **Batch size**: 64
- **Epoki na update**: 10
- **Max kroków na epizod**: 800
- **Zasięg raycastów**: 500 jednostek

---

## 9. Struktura Projektu

```
zpo_projekt/
│
├── main.py                 # Gra manualna
├── train.py                # Trening AI
├── watch.py                # Obserwacja agenta (ciągła jazda)
├── watch_progress.py       # Porównanie etapów treningu
├── requirements.txt        # Zależności
│
├── core/                   # Silnik gry
│   ├── game_engine.py      # Główna pętla gry
│   ├── physics_engine.py   # Fizyka pojazdu
│   ├── renderer.py         # Renderowanie grafiki
│   ├── track.py            # Logika toru (kolizje, checkpointy)
│   ├── track_loader.py     # Ładowanie torów z PNG
│   └── lap_timer.py        # Mierzenie czasu okrążeń
│
├── entities/               # Pojazdy
│   ├── vehicle.py          # Klasa bazowa
│   ├── player_car.py       # Auto gracza
│   └── ai_car.py           # Auto AI (z raycastingiem)
│
├── ai/                     # Reinforcement Learning
│   └── racing_env.py       # Środowisko Gymnasium
│
├── tracks/                 # Tory (PNG + cache JSON)
│   ├── test.png
│   ├── test_cache.json
│   ├── test2.png
│   └── test2_cache.json
│
└── models/                 # Wytrenowane modele
    ├── v1/
    ├── v2/
    ├── v3/
    └── v4/
```

---

## 10. Wyniki Treningu

### Wersja v3 (zalecana do testów)
- **Algorytm**: PPO
- **Kroki treningu**: 210,000
- **Osiągnięcia**:
  - Agent przejeżdża 1-2 checkpointy stabilnie
  - Nauczył się unikać ścian
  - Potrafi cofać gdy ugrzęźnie
  - Czas treningu: ~25-30 min (CPU, 8 rdzeni)

### Progres Uczenia
1. **0-10k kroków**: Chaos, jazda losowa, częste kolizje
2. **10k-30k kroków**: Uczy się jechać prosto, unika ścian
3. **30k-50k kroków**: Pierwsze checkpointy, zaczyna cofać gdy utknął
4. **50k-100k kroków**: Stabilna jazda, osiąga 1-2 checkpointy
5. **100k+ kroków**: Próby pełnego okrążenia

---


Projekt wykonany jako część zajęć z **Zaawansowanego Programowania Obiektowego**.

**Repozytorium**: https://github.com/mewhoosh/zpo_projekt
**Data**: Styczeń 2026