import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import { sankey, sankeyLinkHorizontal, SankeyGraph, SankeyNode, SankeyLink } from 'd3-sankey'
import type { SankeyData } from '@/types'

interface SankeyDiagramProps {
  data: SankeyData
  width?: number
  height?: number
}

function SankeyDiagram({ data, width = 800, height = 400 }: SankeyDiagramProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || !data) return

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove()

    const margin = { top: 10, right: 10, bottom: 10, left: 10 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    // Create SVG
    const svg = d3
      .select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Color scale for different categories
    const colorScale = d3.scaleOrdinal<string>()
      .domain(['source', 'category', 'outcome'])
      .range(['#0ea5e9', '#8b5cf6', '#10b981'])

    // Create sankey generator
    const sankeyGenerator = sankey<SankeyNode<any, any>, SankeyLink<any, any>>()
      .nodeId((d: any) => d.name)
      .nodeWidth(15)
      .nodePadding(10)
      .extent([[1, 1], [innerWidth - 1, innerHeight - 5]])

    // Generate the sankey layout
    const graph: SankeyGraph<any, any> = sankeyGenerator({
      nodes: data.nodes.map((d) => ({ ...d })),
      links: data.links.map((d) => ({ ...d })),
    })

    // Add links
    const link = svg
      .append('g')
      .attr('class', 'links')
      .selectAll('path')
      .data(graph.links)
      .enter()
      .append('path')
      .attr('d', sankeyLinkHorizontal())
      .attr('stroke', (d: any) => {
        const sourceNode = d.source as any
        return colorScale(sourceNode.category || 'source')
      })
      .attr('stroke-width', (d: any) => Math.max(1, d.width))
      .style('fill', 'none')
      .style('opacity', 0.4)
      .on('mouseenter', function () {
        d3.select(this).style('opacity', 0.7)
      })
      .on('mouseleave', function () {
        d3.select(this).style('opacity', 0.4)
      })

    // Add link labels on hover
    link.append('title').text((d: any) => {
      const sourceNode = d.source as any
      const targetNode = d.target as any
      return `${sourceNode.name} → ${targetNode.name}\n${d.value.toLocaleString()} customers`
    })

    // Add nodes
    const node = svg
      .append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(graph.nodes)
      .enter()
      .append('g')

    // Add node rectangles
    node
      .append('rect')
      .attr('x', (d: any) => d.x0)
      .attr('y', (d: any) => d.y0)
      .attr('height', (d: any) => d.y1 - d.y0)
      .attr('width', (d: any) => d.x1 - d.x0)
      .attr('fill', (d: any) => colorScale(d.category || 'source'))
      .style('cursor', 'pointer')
      .on('mouseenter', function () {
        d3.select(this).style('opacity', 0.8)
      })
      .on('mouseleave', function () {
        d3.select(this).style('opacity', 1)
      })

    // Add node labels
    node
      .append('text')
      .attr('x', (d: any) => (d.x0 < innerWidth / 2 ? d.x1 + 6 : d.x0 - 6))
      .attr('y', (d: any) => (d.y1 + d.y0) / 2)
      .attr('dy', '0.35em')
      .attr('text-anchor', (d: any) => (d.x0 < innerWidth / 2 ? 'start' : 'end'))
      .text((d: any) => d.name)
      .style('font-size', '12px')
      .style('fill', '#374151')
      .style('font-weight', '500')

    // Add node tooltips
    node.append('title').text((d: any) => {
      return `${d.name}\n${d.value?.toLocaleString() || 0} customers`
    })

    // Add legend
    const legendData = [
      { label: 'Traffic Source', color: colorScale('source') },
      { label: 'Product Category', color: colorScale('category') },
      { label: 'Outcome', color: colorScale('outcome') },
    ]

    const legend = svg
      .append('g')
      .attr('class', 'legend')
      .attr('transform', `translate(${innerWidth - 150}, 0)`)

    legend
      .selectAll('g')
      .data(legendData)
      .enter()
      .append('g')
      .attr('transform', (_d, i) => `translate(0, ${i * 20})`)
      .each(function (d) {
        const g = d3.select(this)
        g.append('rect')
          .attr('width', 12)
          .attr('height', 12)
          .attr('fill', d.color)

        g.append('text')
          .attr('x', 18)
          .attr('y', 10)
          .text(d.label)
          .style('font-size', '11px')
          .style('fill', '#6b7280')
      })
  }, [data, width, height])

  return (
    <div className="w-full overflow-x-auto">
      <svg ref={svgRef} className="mx-auto" />
    </div>
  )
}

export default SankeyDiagram
