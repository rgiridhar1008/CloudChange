import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Overview } from './pages/Overview';
import { ChangeAnalysis } from './pages/ChangeAnalysis';
import { DependencyGraph } from './pages/DependencyGraph';
import { RiskAnalysis } from './pages/RiskAnalysis';
import { Deployment } from './pages/Deployment';
import { Monitoring } from './pages/Monitoring';
import { History } from './pages/History';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Overview />} />
        <Route path="change" element={<ChangeAnalysis />} />
        <Route path="graph" element={<DependencyGraph />} />
        <Route path="risk" element={<RiskAnalysis />} />
        <Route path="deployment" element={<Deployment />} />
        <Route path="monitoring" element={<Monitoring />} />
        <Route path="history" element={<History />} />
      </Route>
    </Routes>
  );
}

export default App;
