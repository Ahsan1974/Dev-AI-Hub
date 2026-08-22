import { createBrowserRouter } from 'react-router-dom'
import { AppLayout } from './components/layout/AppLayout'
import { HomePage } from './pages/HomePage'
import { BrowsePage } from './pages/BrowsePage'
import { SearchPage } from './pages/SearchPage'
import { ToolDetailPage } from './pages/ToolDetailPage'
import { CategoryPage } from './pages/CategoryPage'
import { FreeToolsPage } from './pages/FreeToolsPage'
import { CollectionsPage } from './pages/CollectionsPage'
import { CollectionDetailPage } from './pages/CollectionDetailPage'
import { WhatDoINeedPage } from './pages/WhatDoINeedPage'
import { ComparePage } from './pages/ComparePage'
import { BuildMyStackPage } from './pages/BuildMyStackPage'
import { FavoritesPage } from './pages/FavoritesPage'
import { NotFoundPage } from './pages/NotFoundPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    errorElement: <NotFoundPage />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'tools', element: <BrowsePage /> },
      { path: 'tools/:slug', element: <ToolDetailPage /> },
      { path: 'search', element: <SearchPage /> },
      { path: 'category/:slug', element: <CategoryPage /> },
      { path: 'free-tools', element: <FreeToolsPage /> },
      // SEO landing pages: same view, category pre-selected.
      { path: 'free-ai-coding-tools', element: <FreeToolsPage presetCategory="ai-coding" /> },
      { path: 'free-ai-image-tools', element: <FreeToolsPage presetCategory="image-generation" /> },
      { path: 'free-ai-video-tools', element: <FreeToolsPage presetCategory="video-generation" /> },
      { path: 'free-ai-audio-tools', element: <FreeToolsPage presetCategory="audio" /> },
      { path: 'free-ai-research-tools', element: <FreeToolsPage presetCategory="research" /> },
      { path: 'collections', element: <CollectionsPage /> },
      { path: 'collections/:slug', element: <CollectionDetailPage /> },
      { path: 'what-do-i-need', element: <WhatDoINeedPage /> },
      { path: 'build-my-stack', element: <BuildMyStackPage /> },
      { path: 'compare', element: <ComparePage /> },
      { path: 'compare/:pair', element: <ComparePage /> },
      { path: 'favorites', element: <FavoritesPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
