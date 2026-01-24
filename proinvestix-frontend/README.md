# ProInvestiX Enterprise Frontend

Next.js 14 frontend voor het ProInvestiX Enterprise platform.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **State**: Zustand + React Query
- **Forms**: React Hook Form + Zod
- **UI**: Radix UI + shadcn/ui

## Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
npm start
```

## Project Structure

```
src/
├── app/                 # Next.js App Router pages
├── components/          # React components
│   ├── ui/             # Base UI components
│   ├── layout/         # Layout components
│   ├── forms/          # Form components
│   ├── tables/         # Table components
│   └── charts/         # Chart components
├── lib/                 # Utility functions & API client
├── hooks/               # Custom React hooks
├── store/               # Zustand stores
├── types/               # TypeScript types
└── styles/              # Global styles
```

## Features

- 🔐 Authentication (JWT)
- 📊 Dashboard with KPIs
- ⚽ Talent Management (NTSP)
- 💰 Transfer Tracking
- 🎫 TicketChain Integration
- 💳 Diaspora Wallet
- 🏛️ Foundation Bank
- 🎓 Academy Management
- 🏟️ FanDorpen WK 2030
- ⚖️ FRMF Integration
- 🆔 Identity Shield
- 🧠 Hayat Health
- 🛡️ Anti-Hate Shield
- 📰 NIL News Intelligence
- 🏢 Consulate Hub

## Environment Variables

Copy `.env.example` to `.env.local` and configure:

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```
