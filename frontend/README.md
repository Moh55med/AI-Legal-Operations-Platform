# AI Legal Operations Platform - Frontend

React frontend for the AI Legal Operations Platform.

## Setup

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file from template:
```bash
cp .env.example .env
```

3. Update `.env` with your backend API URL:
```
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_DEBUG=false
```

### Development

Start the development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

### Build

Create a production build:
```bash
npm run build
```

### Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── pages/
│   │   ├── Login.js
│   │   ├── Dashboard.js
│   │   ├── Cases.js
│   │   ├── CaseDetail.js
│   │   ├── AIAssistant.js
│   │   └── Deadlines.js
│   ├── services/
│   │   └── api.js
│   ├── components/
│   ├── App.js
│   ├── App.css
│   └── index.js
├── package.json
└── .env.example
```

## Features

- User authentication with JWT
- Dashboard with case and deadline overview
- Case management with search and filtering
- Deadline tracking
- AI Assistant for structured queries
- Responsive design

## API Integration

The frontend uses axios to communicate with the backend API at `REACT_APP_API_URL`. Authentication is handled via JWT token stored in localStorage.

All API requests automatically include the JWT token in the Authorization header.
