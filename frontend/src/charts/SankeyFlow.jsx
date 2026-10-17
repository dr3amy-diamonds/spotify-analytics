import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { sankey, sankeyLinkHorizontal } from 'd3-sankey';
import { useTheme } from '../theme/ThemeContext';
import styles from './SankeyFlow.module.css';

const FRANJAS = ['Madrugada', 'Mañana', 'Tarde', 'Noche'];

export default function SankeyFlow({ data = [], loading }) {
  const svgRef = useRef(null);
  const wrapRef = useRef(null);
  const tipRef = useRef(null);
  const { theme } = useTheme();

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    if (!data.length) return;

    const draw = (width) => {
      const height = 300;
      const margin = { top: 8, right: 90, bottom: 8, left: 90 };
      const w = Math.max(240, width - margin.left - margin.right);
      svg.attr('width', width).attr('height', height);
      const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

      const artists = [...new Set(data.map((d) => d.nombre_artista))];
      const nodes = [...artists.map((a) => ({ name: a })), ...FRANJAS.map((f) => ({ name: f }))];
      const idx = new Map(nodes.map((n, i) => [n.name, i]));
      const links = data
        .filter((d) => idx.has(d.nombre_artista) && idx.has(d.franja_dia))
        .map((d) => ({ source: idx.get(d.nombre_artista), target: idx.get(d.franja_dia), value: Number(d.minutos_totales) || 0 }))
        .filter((l) => l.value > 0);

      const gen = sankey().nodeWidth(14).nodePadding(12).extent([[0, 0], [w, height - 16]]);
      const graph = gen({ nodes: nodes.map((n) => ({ ...n })), links: links.map((l) => ({ ...l })) });

      const color = d3.scaleLinear().domain([0, graph.links.length]).range([theme.gradientD3[1], theme.gradientD3[2]]);
      const tip = d3.select(tipRef.current);

      g.selectAll('rect')
        .data(graph.nodes)
        .join('rect')
        .attr('x', (d) => d.x0)
        .attr('y', (d) => d.y0)
        .attr('width', (d) => d.x1 - d.x0)
        .attr('height', (d) => Math.max(1, d.y1 - d.y0))
        .attr('fill', theme.accentPrimary);

      g.selectAll('text')
        .data(graph.nodes)
        .join('text')
        .attr('x', (d) => (d.x0 < w / 2 ? d.x1 + 4 : d.x0 - 4))
        .attr('y', (d) => (d.y0 + d.y1) / 2)
        .attr('text-anchor', (d) => (d.x0 < w / 2 ? 'start' : 'end'))
        .attr('dominant-baseline', 'middle')
        .attr('font-size', 12)
        .attr('fill', theme.textSecondary)
        .text((d) => d.name);

      g.selectAll('path')
        .data(graph.links)
        .join('path')
        .attr('d', sankeyLinkHorizontal())
        .attr('fill', 'none')
        .attr('stroke', (_, i) => color(i))
        .attr('stroke-opacity', 0.35)
        .attr('stroke-width', (d) => Math.max(1, d.width))
        .on('mousemove', (e, d) => {
          d3.select(e.target).attr('stroke-opacity', 0.6);
          tip.style('display', 'block').style('left', `${e.offsetX + 10}px`).style('top', `${e.offsetY}px`)
            .text(`${d.source.name} -> ${d.target.name}: ${d.value.toFixed(1)} min`);
        })
        .on('mouseleave', (e) => {
          d3.select(e.target).attr('stroke-opacity', 0.35);
          tip.style('display', 'none');
        });
    };

    const width = wrapRef.current?.clientWidth || 600;
    draw(width);
    const ro = new ResizeObserver((entries) => {
      const w = entries[0]?.contentRect.width;
      if (w) { svg.selectAll('*').remove(); draw(w); }
    });
    if (wrapRef.current) ro.observe(wrapRef.current);
    return () => { ro.disconnect(); svg.selectAll('*').remove(); };
  }, [data, theme]);

  return (
    <div className={styles.card}>
      <h2 className={styles.title}>Flujo Artista - Franja</h2>
      <div ref={wrapRef} className={styles.wrap}>
        {loading ? <span>Cargando…</span> : !data.length ? <span>Sin datos para filtros actuales.</span> : null}
        <svg ref={svgRef} role="img" aria-label="Diagrama Sankey" />
        <div ref={tipRef} className={styles.tooltip} />
      </div>
    </div>
  );
}
