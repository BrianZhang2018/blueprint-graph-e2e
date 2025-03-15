# Blueprint Graph UI

This is the frontend UI for the Blueprint Graph security event processing and detection system.

## Features

- Dashboard with overview of rules and alerts
- Manage detection rules
- View and filter alerts
- Submit events for processing
- Configure application settings

## Technologies Used

- React with TypeScript
- Material UI for components
- React Router for navigation
- React Query for data fetching
- Axios for API communication

## Getting Started

### Prerequisites

- Node.js (v16+)
- npm or yarn
- Blueprint Graph API running (default: http://localhost:8000)

### Installation

1. Clone the repository
2. Navigate to the UI directory
3. Install dependencies:

```bash
npm install
```

4. Create a `.env` file with the API URL:

```
VITE_API_URL=http://localhost:8000
```

### Development

Start the development server:

```bash
npm run dev
```

This will start the development server at http://localhost:5173.

### Building for Production

Build the application for production:

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

- `src/api`: API service for communicating with the backend
- `src/components`: Reusable UI components
- `src/hooks`: Custom React hooks
- `src/pages`: Page components
- `src/types`: TypeScript type definitions
- `src/utils`: Utility functions

## Configuration

The application can be configured using environment variables:

- `VITE_API_URL`: URL of the Blueprint Graph API (default: http://localhost:8000)

## License

This project is licensed under the MIT License.
