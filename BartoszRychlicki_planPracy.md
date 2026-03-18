# Temat projektu: 
## Konteneryzacja i automatyzacja wdrażania aplikacji webowej z wykorzystaniem Docker, RabbitMQ oraz PyTest

## Zespół: Bartosz Rychlicki, Fabian Popielewski, Grupa 2

# Cel projektu:
### Celem projektu jest rozwinięcie istniejącej aplikacji serwisu auto-komisu napisanej w technologii FastAPI poprzez przygotowanie środowiska uruchomieniowego opartego na kontenerach Docker  i automatyzacji procesu budowania oraz testowania aplikacji.

# Zakres projektu:
## Projekt obejmuje następujące elementy:
1. Aplikacja webowa (FastAPI)
- rozwój istniejącej aplikacji auto-komisu (Dodanie przy tworzeniu ogłoszeń wyboru dodawanych informacji z listy)
2. Baza danych (MariaDB)
- integracja aplikacji z bazą danych uruchamianą w kontenerze
3. Konteneryzacja (Docker, Docker Compose)
- przygotowanie plików Dockerfile dla aplikacji
- konfiguracja środowiska wielokontenerowego (docker-compose)
- uruchamianie wszystkich usług jedną komendą
4. Reverse proxy (Nginx)
- konfiguracja serwera Nginx jako pośrednika HTTP
- przekierowanie ruchu do aplikacji FastAPI
5. Testy aplikacji
- przygotowanie testów API (z użyciem pytest)
- uruchamianie testów w osobnym kontenerze Docker
- Uruchamianie testów przed pushem do github
6. System kolejkowy (RabbitMQ)
- implementacja komunikacji asynchronicznej
- stworzenie procesu typu worker do obsługi komunikatów
7. Automatyzacja (Jenkins)???
- przygotowanie pipeline CI obejmującego:
  - budowanie obrazów Docker
  - uruchamianie aplikacji
  - wykonywanie testów

## Wykorzystywane technologie
- Python (FastAPI)
- mariadb
- Nginx
- Docker, Docker Compose
- Pytest
- (Jenkins)???

## Rezultat projektu
Rezultatem projektu będzie działająca aplikacja webowa uruchamiana w środowisku kontenerowym, wraz z pełną konfiguracją infrastruktury (baza danych, system kolejkowy, reverse proxy) oraz zautomatyzowanym procesem budowania i testowania aplikacji.

