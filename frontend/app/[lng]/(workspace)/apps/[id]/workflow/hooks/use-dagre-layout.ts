import dagre from '@dagrejs/dagre'
import { useReactFlow } from '@xyflow/react'
import { useCallback } from 'react'

export interface DagreLayoutOptions {
  nodesep?: number
  edgesep?: number
  ranksep?: number
  marginx?: number
  marginy?: number
  ranker?: 'network-simplex' | 'tight-tree' | 'longest-path'
}

const defaultOptions: DagreLayoutOptions = {
  nodesep: 50,
  edgesep: 10,
  ranksep: 50,
  marginx: 20,
  marginy: 20,
  ranker: 'longest-path',
}

export function useDagreLayout() {
  const { getNodes, getEdges, setNodes, setEdges } = useReactFlow()

  const getLayoutedElements = useCallback((options?: DagreLayoutOptions) => {
    const nodes = getNodes()
    const edges = getEdges()
    const resolvedOptions = { ...defaultOptions, ...options, rankdir: 'LR' }

    const dagreGraph = new dagre.graphlib.Graph()
    dagreGraph.setGraph(resolvedOptions)
    dagreGraph.setDefaultEdgeLabel(() => ({}))

    nodes.forEach((node) => {
      const nodeWidth = node.measured?.width || 150
      const nodeHeight = node.measured?.height || 50

      dagreGraph.setNode(node.id, {
        width: nodeWidth,
        height: nodeHeight,
      })
    })

    edges.forEach((edge) => {
      dagreGraph.setEdge(edge.source, edge.target)
    })

    dagre.layout(dagreGraph)

    const layoutedNodes = nodes.map((node) => {
      const nodeWithPosition = dagreGraph.node(node.id)

      return {
        ...node,
        // We need to shift the dagre node position (anchor=center center)
        // to the top left so it matches the React Flow node anchor point (top left)
        position: {
          x: nodeWithPosition.x - (node.measured?.width || 150) / 2,
          y: nodeWithPosition.y - (node.measured?.height || 50) / 2,
        },
      }
    })

    return {
      nodes: layoutedNodes,
      edges,
    }
  }, [getNodes, getEdges])

  const layout = useCallback((options?: DagreLayoutOptions) => {
    const currentNodes = getNodes()
    if (currentNodes.length === 0)
      return

    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(options)

    // Check if layout change is needed
    const needsLayout = currentNodes.some((node, index) => {
      const layoutedNode = layoutedNodes[index]
      return node.position.x !== layoutedNode?.position?.x
        || node.position.y !== layoutedNode?.position?.y
    })

    // Only update if layout actually changes
    if (needsLayout) {
      setNodes(layoutedNodes)
      setEdges(layoutedEdges)
    }
  }, [getLayoutedElements, getNodes, setNodes, setEdges])

  return {
    layout,
    getLayoutedElements,
  }
}
