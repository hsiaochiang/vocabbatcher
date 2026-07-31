import { HashRouter, Routes, Route } from 'react-router-dom';
import { AppProvider } from './store/AppContext';
import HomePage from './pages/HomePage';
import BatchBuilderPage from './pages/BatchBuilderPage';
import BatchHubPage from './pages/BatchHubPage';
import FlashCardPage from './pages/FlashCardPage';
import ExamSetupPage from './pages/ExamSetupPage';
import ExamRunPage from './pages/ExamRunPage';
import ExamResultPage from './pages/ExamResultPage';

export default function App() {
  return (
    <AppProvider>
      <HashRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/builder" element={<BatchBuilderPage />} />
          <Route path="/batch/:id" element={<BatchHubPage />} />
          <Route path="/batch/:id/flashcard" element={<FlashCardPage />} />
          <Route path="/exam" element={<ExamSetupPage />} />
          <Route path="/exam/run" element={<ExamRunPage />} />
          <Route path="/exam/result" element={<ExamResultPage />} />
        </Routes>
      </HashRouter>
    </AppProvider>
  );
}
