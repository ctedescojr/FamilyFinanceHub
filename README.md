# 💰 FamilyFinanceHub

Sistema completo de controle financeiro familiar com OCR para notas fiscais e otimização de rotas de compras.

## 🚀 Tecnologias

### Backend
- **Python 3.13+**
- **Django 5.2+** + Django REST Framework
- **PostgreSQL 17+** (Banco de dados)
- **Redis** (Cache e filas)
- **Celery** (Tarefas assíncronas)
- **JWT** (Autenticação)
- **Tesseract OCR** (Reconhecimento de texto)

### Frontend
- **React 24+**
- **Vite 5+** (Build tool)
- **Tailwind CSS 4.1+** (Styling)
- **Zustand** (Gerenciamento de estado)
- **React Hook Form** (Formulários)
- **Recharts** (Gráficos)

### DevOps
- **Docker** + **Docker Compose**
- **Nginx** (Proxy reverso)

## 📁 Estrutura do Projeto

```
familyfinancehub/
├── backend/              # Django REST API
├── frontend/             # React + Vite + Tailwind
├── mobile/              # Flutter (futuro)
├── docker-compose.yml   # Orquestração
└── README.md
```

## 🛠️ Setup Rápido

### Pré-requisitos
- Docker e Docker Compose
- Git

### 1. Clone o repositório
```bash
git clone <repository-url> familyfinancehub
cd familyfinancehub
```

### 2. Configure as variáveis de ambiente
```bash
# Backend
cp .env.example backend/.env

# Frontend
cp .env.example frontend/.env
```

### 3. Inicie os serviços
```bash