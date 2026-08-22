import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider } from 'react-router-dom'
import { router } from './router'
import { ThemeProvider } from './hooks/useTheme'
import { LocalCollectionsProvider } from './hooks/useLocalCollections'
import { ApiError } from './services/client'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      gcTime: 10 * 60 * 1000,
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => {
        // Retrying a 404 or a validation error only delays the error state.
        if (error instanceof ApiError && error.status >= 400 && error.status < 500) return false
        return failureCount < 2
      },
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <LocalCollectionsProvider>
          <RouterProvider router={router} />
        </LocalCollectionsProvider>
      </ThemeProvider>
    </QueryClientProvider>
  </StrictMode>,
)
