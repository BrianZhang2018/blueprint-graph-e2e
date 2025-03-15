import React, { useState, useCallback } from 'react';
import { 
  Box, 
  Paper, 
  TextField, 
  Button, 
  Typography,
  Grid,
  CircularProgress,
  Alert
} from '@mui/material';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useQuery } from '@tanstack/react-query';
import * as api from '../api/api';

interface GraphQueryResponse {
  nodes: Array<{
    id: string;
    labels: string[];
    properties: Record<string, any>;
  }>;
  relationships: Array<{
    id: string;
    type: string;
    start: string;
    end: string;
    properties: Record<string, any>;
  }>;
}

const Graph: React.FC = () => {
  const [query, setQuery] = useState('');
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [error, setError] = useState<string | null>(null);

  const { data, isLoading, refetch } = useQuery<GraphQueryResponse>({
    queryKey: ['graph', query],
    queryFn: () => api.executeGraphQuery(query),
    enabled: false,
  });

  const handleExecuteQuery = useCallback(() => {
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }
    refetch();
  }, [query, refetch]);

  const transformDataToGraph = useCallback((data: GraphQueryResponse) => {
    if (!data) return;

    // Transform nodes
    const transformedNodes: Node[] = data.nodes.map((node, index) => ({
      id: node.id,
      type: 'default',
      position: { x: index * 200, y: 0 },
      data: {
        label: node.labels.join(', '),
        properties: node.properties,
      },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
    }));

    // Transform relationships
    const transformedEdges: Edge[] = data.relationships.map((rel) => ({
      id: rel.id,
      source: rel.start,
      target: rel.end,
      label: rel.type,
      type: 'smoothstep',
    }));

    setNodes(transformedNodes);
    setEdges(transformedEdges);
    setError(null);
  }, [setNodes, setEdges]);

  React.useEffect(() => {
    if (data) {
      transformDataToGraph(data);
    }
  }, [data, transformDataToGraph]);

  return (
    <Box sx={{ height: '100vh', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Graph Visualization
      </Typography>

      <Grid container spacing={3} sx={{ height: 'calc(100vh - 100px)' }}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              Query Editor
            </Typography>
            <TextField
              multiline
              rows={10}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your Neo4j query..."
              fullWidth
              sx={{ mb: 2 }}
              error={!!error}
              helperText={error}
            />
            <Button
              variant="contained"
              onClick={handleExecuteQuery}
              disabled={isLoading}
              sx={{ mt: 'auto' }}
            >
              {isLoading ? <CircularProgress size={24} /> : 'Execute Query'}
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Graph Visualization
            </Typography>
            <Box sx={{ height: 'calc(100% - 40px)' }}>
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                fitView
              >
                <Background />
                <Controls />
              </ReactFlow>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Graph; 