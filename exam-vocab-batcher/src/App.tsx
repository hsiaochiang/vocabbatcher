import { HashRouter, Routes, Route } from 'react-router-dom';
import { AppProvider } from './store/AppContext';
import HomePage from './pages/HomePage';
import BatchBuilderPage from './pages/BatchBuilderPage';
import BatchHubPage from './pages/BatchHubPage';
import FlashCardPage from './pages/FlashCardPage';

export default function App() {
  return (
    <AppProvider>
      <HashRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/builder" element={<BatchBuilderPage />} />
          <Route path="/batch/:id" element={<BatchHubPage />} />
          <Route path="/batch/:id/flashcard" element={<FlashCardPage />} />
        </Routes>
      </HashRouter>
    </AppProvider>
  );
}
