import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { ChatInterface } from './components/chat/ChatInterface';
import EvaluationPage from './pages/EvaluationPage';

function Navigation() {
  const location = useLocation();

  const navLinkClass = (path: string) =>
    `py-4 px-2 border-b-2 transition-colors ${
      location.pathname === path
        ? 'border-blue-500 text-blue-600'
        : 'border-transparent text-gray-600 hover:text-blue-500 hover:border-blue-300'
    }`;

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex space-x-8">
          <Link to="/" className={navLinkClass('/')}>
            Chat
          </Link>
          <Link to="/evaluation" className={navLinkClass('/evaluation')}>
            Evaluation
          </Link>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <Routes>
          <Route path="/" element={<ChatInterface />} />
          <Route path="/evaluation" element={<EvaluationPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
