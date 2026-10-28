import React, { useState, useEffect, useRef, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Card, CardHeader, CardTitle, CardContent } from '../components/Card';
import { api } from '../services/api';
import { Network, Database, Globe, Box, Server, AlertTriangle, Info, ZoomIn, ZoomOut, Maximize, RefreshCw, X } from 'lucide-react';

const getNodeColor = (node) => {
  if (node.changed) return '#3b82f6';   // primary blue — changed
  if (node.affected) return '#f59e0b';  // amber — affected
  
  switch(node.type?.toUpperCase()) {
    case 'DATABASE': return '#a855f7';   // purple
    case 'GATEWAY': return '#06b6d4';    // cyan
    case 'INGRESS': return '#10b981';    // green
    case 'MESSAGE_QUEUE': return '#f97316'; // orange
    default: return '#64748b';           // slate
  }
};

const getNodeIcon = (type) => {
  switch(type?.toUpperCase()) {
    case 'DATABASE': return Database;
    case 'GATEWAY': return Globe;
    case 'INGRESS': return Globe;
    case 'MESSAGE_QUEUE': return Server;
    default: return Box;
  }
};

export const DependencyGraph = () => {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const fgRef = useRef();
  const containerRef = useRef();

  // Responsive sizing
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight,
        });
      }
    };
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, [loading, error]);

  const fetchGraph = useCallback(async () => {
    setLoading(true);
    setError(null);
    setSelectedNode(null);
    try {
      const res = await api.getGraph();

      // ── Validate response ──
      if (!res || !Array.isArray(res.nodes) || !Array.isArray(res.edges)) {
        console.error('[DependencyGraph] Invalid API response:', res);
        setError('Backend returned an invalid graph structure.');
        setLoading(false);
        return;
      }

      // ── Build a set of valid node IDs for edge validation ──
      const nodeIdSet = new Set();

      // ── Normalize nodes ──
      const nodes = res.nodes
        .filter(n => {
          if (!n || !n.id) {
            console.warn('[DependencyGraph] Skipping node without id:', n);
            return false;
          }
          return true;
        })
        .map(n => {
          nodeIdSet.add(n.id);
          return {
            id: n.id,
            label: n.label || n.name || n.id,   // canonical label
            type: n.type || 'Service',
            namespace: n.namespace || 'default',
            criticality: n.criticality || 'medium',
            changed: n.changed || false,
            affected: n.affected || false,
            status: n.status || 'healthy',
            val: 1.5,
          };
        });

      // ── Normalize edges ──
      const links = res.edges
        .filter(e => {
          // Accepts both { source, target } AND { from_node, to_node }
          const src = e.source || e.from_node;
          const tgt = e.target || e.to_node;
          if (!src || !tgt) {
            console.warn('[DependencyGraph] Skipping edge without source/target:', e);
            return false;
          }
          if (!nodeIdSet.has(src) || !nodeIdSet.has(tgt)) {
            console.warn(`[DependencyGraph] Skipping edge with unknown node(s): ${src} → ${tgt}`);
            return false;
          }
          return true;
        })
        .map(e => {
          const src = e.source || e.from_node;
          const tgt = e.target || e.to_node;
          return {
            id: e.id || `${src}-${tgt}`,
            source: src,
            target: tgt,
            relationship: e.relationship || e.type || 'depends_on',
          };
        });

      console.log(`[DependencyGraph] Loaded ${nodes.length} nodes, ${links.length} edges`);
      setGraphData({ nodes, links });
    } catch (err) {
      console.error('[DependencyGraph] Fetch failed:', err);
      setError('Unable to load dependency topology. Check that the backend is running.');
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchGraph();
  }, [fetchGraph]);

  // Fit to screen once data is loaded
  useEffect(() => {
    if (!loading && !error && graphData.nodes.length > 0 && fgRef.current) {
      setTimeout(() => fgRef.current.zoomToFit(400, 60), 300);
    }
  }, [loading, error, graphData]);

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    if (fgRef.current) {
      fgRef.current.centerAt(node.x, node.y, 800);
      fgRef.current.zoom(4, 800);
    }
  };

  const handleBackgroundClick = () => setSelectedNode(null);

  const zoomIn = () => fgRef.current?.zoom(fgRef.current.zoom() * 1.5, 400);
  const zoomOut = () => fgRef.current?.zoom(fgRef.current.zoom() / 1.5, 400);
  const resetView = () => { fgRef.current?.zoomToFit(400, 60); setSelectedNode(null); };

  // ── Connections helper for detail panel ──
  const getUpstream = () => graphData.links.filter(l =>
    (typeof l.source === 'object' ? l.source.id : l.source) === selectedNode?.id
  );
  const getDownstream = () => graphData.links.filter(l =>
    (typeof l.target === 'object' ? l.target.id : l.target) === selectedNode?.id
  );

  return (
    <div className="space-y-6 h-[calc(100vh-140px)] flex flex-col animate-in fade-in duration-500">
      <div>
        <h2 className="text-3xl font-bold tracking-tight text-text-primary mb-2">Architectural Topology</h2>
        <p className="text-text-secondary">Interactive dependency graph for blast radius evaluation.</p>
      </div>

      <Card className="flex-1 flex flex-col relative overflow-hidden bg-background border-border shadow-2xl">
        {/* Controls */}
        <div className="absolute top-4 left-4 z-10 flex space-x-2">
          <button onClick={zoomIn} className="p-2 bg-surface hover:bg-gray-700 border border-border rounded-lg text-text-secondary hover:text-text-primary transition-colors shadow-lg" title="Zoom In"><ZoomIn size={18} /></button>
          <button onClick={zoomOut} className="p-2 bg-surface hover:bg-gray-700 border border-border rounded-lg text-text-secondary hover:text-text-primary transition-colors shadow-lg" title="Zoom Out"><ZoomOut size={18} /></button>
          <button onClick={resetView} className="p-2 bg-surface hover:bg-gray-700 border border-border rounded-lg text-text-secondary hover:text-text-primary transition-colors shadow-lg" title="Fit to Screen"><Maximize size={18} /></button>
        </div>

        {/* Legend */}
        <div className="absolute top-4 right-4 z-10 flex items-center space-x-4 bg-surface/80 backdrop-blur-sm border border-border rounded-lg px-4 py-2 text-xs">
          <div className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#3b82f6]"></span><span className="text-text-secondary">Changed</span></div>
          <div className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#f59e0b]"></span><span className="text-text-secondary">Affected</span></div>
          <div className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#a855f7]"></span><span className="text-text-secondary">Database</span></div>
          <div className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#06b6d4]"></span><span className="text-text-secondary">Gateway</span></div>
          <div className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#64748b]"></span><span className="text-text-secondary">Service</span></div>
        </div>

        <div ref={containerRef} className="flex-1 w-full h-full relative cursor-crosshair">
          {/* ── Loading State ── */}
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-20">
              <div className="flex flex-col items-center">
                <span className="w-10 h-10 rounded-full border-4 border-border border-t-blue-500 animate-spin mb-4"></span>
                <p className="text-text-secondary font-medium text-sm">Loading dependency topology...</p>
              </div>
            </div>
          )}

          {/* ── Error State ── */}
          {error && !loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-20">
              <div className="flex flex-col items-center text-center max-w-sm">
                <AlertTriangle size={48} className="mb-4 text-red-500/70" />
                <p className="font-semibold text-red-400 mb-2">Unable to load dependency topology</p>
                <p className="text-sm text-text-secondary mb-6">{error}</p>
                <button
                  onClick={fetchGraph}
                  className="flex items-center space-x-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
                >
                  <RefreshCw size={16} />
                  <span>Retry</span>
                </button>
              </div>
            </div>
          )}

          {/* ── Empty State ── */}
          {!loading && !error && graphData.nodes.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center z-20">
              <div className="flex flex-col items-center text-center max-w-sm">
                <Network size={48} className="mb-4 text-text-secondary/30" />
                <p className="font-semibold text-text-primary mb-2">No dependency relationships found</p>
                <p className="text-sm text-text-secondary mb-6">The backend dependency analyzer did not return any service nodes. Make sure your Kubernetes manifests define services with dependency relationships.</p>
                <button
                  onClick={fetchGraph}
                  className="flex items-center space-x-2 px-6 py-2 bg-surface hover:bg-gray-700 border border-border text-text-primary rounded-lg text-sm font-medium transition-colors"
                >
                  <RefreshCw size={16} />
                  <span>Reload</span>
                </button>
              </div>
            </div>
          )}

          {/* ── Graph ── */}
          {!loading && !error && graphData.nodes.length > 0 && dimensions.width > 0 && (
            <ForceGraph2D
              ref={fgRef}
              graphData={graphData}
              nodeLabel={node => node.label}
              nodeColor={node => getNodeColor(node)}
              nodeRelSize={8}
              linkDirectionalArrowLength={6}
              linkDirectionalArrowRelPos={1}
              linkCurvature={0.1}
              linkWidth={link => {
                if (!selectedNode) return 1.5;
                const srcId = typeof link.source === 'object' ? link.source.id : link.source;
                const tgtId = typeof link.target === 'object' ? link.target.id : link.target;
                return (srcId === selectedNode.id || tgtId === selectedNode.id) ? 3 : 1;
              }}
              linkColor={link => {
                if (!selectedNode) return '#475569';
                const srcId = typeof link.source === 'object' ? link.source.id : link.source;
                const tgtId = typeof link.target === 'object' ? link.target.id : link.target;
                return (srcId === selectedNode.id || tgtId === selectedNode.id) ? '#60a5fa' : '#1e293b';
              }}
              width={dimensions.width}
              height={dimensions.height}
              backgroundColor="rgba(0,0,0,0)"
              onNodeClick={handleNodeClick}
              onBackgroundClick={handleBackgroundClick}
              cooldownTicks={100}
              d3AlphaDecay={0.02}
              d3VelocityDecay={0.3}
              nodeCanvasObject={(node, ctx, globalScale) => {
                const label = node.label;
                const isSelected = node.id === selectedNode?.id;
                const radius = isSelected ? 7 : 5;
                const color = getNodeColor(node);

                // ── Glow for selected node ──
                if (isSelected) {
                  ctx.beginPath();
                  ctx.arc(node.x, node.y, radius + 4, 0, 2 * Math.PI);
                  ctx.fillStyle = color + '30';
                  ctx.fill();
                }

                // ── Node circle ──
                ctx.beginPath();
                ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI);
                ctx.fillStyle = color;
                ctx.fill();
                if (isSelected) {
                  ctx.lineWidth = 2 / globalScale;
                  ctx.strokeStyle = '#ffffff';
                  ctx.stroke();
                }

                // ── Label ──
                const fontSize = Math.max(11 / globalScale, 3);
                ctx.font = `600 ${fontSize}px Inter, system-ui, sans-serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';

                // Background pill
                const textWidth = ctx.measureText(label).width;
                const padding = fontSize * 0.4;
                const bgHeight = fontSize + padding;
                const bgWidth = textWidth + padding * 2;
                const labelY = node.y + radius + fontSize * 0.8;

                ctx.fillStyle = isSelected ? 'rgba(30,41,59,0.95)' : 'rgba(15,23,42,0.85)';
                ctx.beginPath();
                ctx.roundRect(node.x - bgWidth / 2, labelY - bgHeight / 2, bgWidth, bgHeight, 3);
                ctx.fill();

                ctx.fillStyle = isSelected ? '#ffffff' : '#cbd5e1';
                ctx.fillText(label, node.x, labelY);
              }}
              nodePointerAreaPaint={(node, color, ctx) => {
                ctx.beginPath();
                ctx.arc(node.x, node.y, 8, 0, 2 * Math.PI);
                ctx.fillStyle = color;
                ctx.fill();
              }}
            />
          )}
        </div>

        {/* ── Node Details Side Panel ── */}
        <div className={`absolute top-0 right-0 h-full w-80 bg-surface/95 backdrop-blur-xl border-l border-border shadow-2xl transition-transform duration-300 transform ${selectedNode ? 'translate-x-0' : 'translate-x-full'} z-30`}>
          {selectedNode && (
            <div className="h-full flex flex-col overflow-y-auto">
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-border">
                <h3 className="text-sm font-bold text-text-secondary uppercase tracking-wider">Node Inspector</h3>
                <button onClick={() => setSelectedNode(null)} className="p-1 hover:bg-gray-800 rounded-lg transition-colors text-text-secondary hover:text-text-primary"><X size={16} /></button>
              </div>

              <div className="p-6 space-y-6 flex-1">
                {/* Identity */}
                <div className="flex items-center space-x-4">
                  <div className="p-3 rounded-xl border border-border" style={{ backgroundColor: getNodeColor(selectedNode) + '15' }}>
                    {React.createElement(getNodeIcon(selectedNode.type), { size: 24, style: { color: getNodeColor(selectedNode) } })}
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-text-primary leading-tight break-all">{selectedNode.label}</h3>
                    <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">{selectedNode.type}</span>
                  </div>
                </div>

                {/* Properties */}
                <div>
                  <h4 className="text-xs font-bold text-text-secondary uppercase tracking-wider mb-3">Service Details</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-text-secondary">Node ID</span>
                      <span className="text-text-primary font-mono text-xs bg-background px-2 py-0.5 rounded border border-border">{selectedNode.id}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-text-secondary">Status</span>
                      <span className={`text-xs font-bold uppercase ${selectedNode.status === 'healthy' ? 'text-green-400' : 'text-red-400'}`}>{selectedNode.status}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-text-secondary">Criticality</span>
                      <span className="text-text-primary capitalize">{selectedNode.criticality}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-text-secondary">Changed</span>
                      <span className={`text-xs font-bold ${selectedNode.changed ? 'text-blue-400' : 'text-text-secondary'}`}>{selectedNode.changed ? 'Yes' : 'No'}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-text-secondary">Affected</span>
                      <span className={`text-xs font-bold ${selectedNode.affected ? 'text-amber-400' : 'text-text-secondary'}`}>{selectedNode.affected ? 'Yes' : 'No'}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-text-secondary">Namespace</span>
                      <span className="text-text-primary font-mono text-xs">{selectedNode.namespace}</span>
                    </div>
                  </div>
                </div>

                {/* Connections */}
                <div>
                  <h4 className="text-xs font-bold text-text-secondary uppercase tracking-wider mb-3">Connections</h4>
                  <div className="bg-background rounded-lg border border-border p-4 space-y-4">
                    <div>
                      <p className="text-xs text-text-secondary mb-2">Dependencies (Upstream)</p>
                      {getUpstream().length > 0 ? getUpstream().map((l, i) => {
                        const tgtId = typeof l.target === 'object' ? l.target.id : l.target;
                        const tgtNode = graphData.nodes.find(n => n.id === tgtId);
                        return <p key={i} className="text-sm text-text-primary font-medium">→ {tgtNode?.label || tgtId}</p>;
                      }) : <p className="text-xs text-text-secondary italic">None</p>}
                    </div>
                    <div className="border-t border-border pt-3">
                      <p className="text-xs text-text-secondary mb-2">Dependents (Downstream)</p>
                      {getDownstream().length > 0 ? getDownstream().map((l, i) => {
                        const srcId = typeof l.source === 'object' ? l.source.id : l.source;
                        const srcNode = graphData.nodes.find(n => n.id === srcId);
                        return <p key={i} className="text-sm text-text-primary font-medium">← {srcNode?.label || srcId}</p>;
                      }) : <p className="text-xs text-text-secondary italic">None</p>}
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4 border-t border-border">
                <button
                  onClick={() => setSelectedNode(null)}
                  className="w-full py-2 bg-surface hover:bg-gray-700 border border-border text-text-primary rounded-lg text-sm font-medium transition-colors"
                >
                  Close Inspector
                </button>
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};
