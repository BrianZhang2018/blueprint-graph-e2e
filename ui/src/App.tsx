import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createBrowserRouter } from 'react-router-dom'

import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Alerts from './pages/Alerts'
import Rules from './pages/Rules'
import Events from './pages/Events'
import Settings from './pages/Settings'
import Graph from './pages/Graph'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
})

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        path: "/",
        element: <Dashboard />,
      },
      {
        path: "/rules",
        element: <Rules />,
      },
      {
        path: "/alerts",
        element: <Alerts />,
      },
      {
        path: "/events",
        element: <Events />,
      },
      {
        path: "/settings",
        element: <Settings />,
      },
      {
        path: "/graph",
        element: <Graph />,
      },
    ],
  },
])

function App() {
  const [darkMode, setDarkMode] = useState(false)

  // Create a theme instance
  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: '#2196f3',
      },
      secondary: {
        main: '#f50057',
      },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/rules" element={<Rules />} />
              <Route path="/events" element={<Events />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/graph" element={<Graph />} />
            </Routes>
          </Layout>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
