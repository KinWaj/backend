# Backend API - Laboratorium 4

**Autor:** Kinga
**Grupa:** INMN2(hybryda)_PAW2

## Opis projektu
Koncowa wersja projektu

API umożliwia:
- Rejestrację i logowanie użytkowników
- Zarządzanie zadaniami (tasks) w bazie danych
- Chronione endpointy wymagające autoryzacji JWT

## Technologie
- Python
- FastAPI
- Supabase (PostgreSQL + Authentication)
- JWT (JSON Web Token) - przez Supabase Auth

## Endpointy

### Autoryzacja (`/auth`)
1. **POST /auth/register** - rejestracja nowego użytkownika

2. **POST /auth/login** - logowanie użytkownika

### Zadania (`/tasks`) - wymagają autoryzacji (Bearer token)

2. **POST /tasks** - utworzenie nowego zadania

3. **PATCH /tasks/{task_id}** - aktualizacja zadania

4. **DELETE /tasks/{task_id}** - usunięcie zadania

## Konfiguracja

W pliku `.env` należy zdefiniować:
- `SENTRY_DSN` - klucz do sentry
- `SUPABASE_URL` - URL projektu Supabase
- `SUPABASE_ANON_KEY` - klucz anonimowy Supabase
