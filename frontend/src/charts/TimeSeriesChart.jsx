import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { useTheme } from '../theme/ThemeContext';
import styles from './TimeSeriesChart.module.css';

export default function TimeSeriesChart({ data = [], loading }) {
  const svgRef = useRef(null);
  const wrapRef = useRef(null);
  const tipRef = useRef(null);
  const { theme } = useTheme();
  const [metric, setMetric] = useState('total_escuchas');

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    if (!data.length) return;

    const agg = new Map();
    data.forEach((d) => {
      const key = `${d.anio}-${String(d.mes).padStart(2, '0')}`;
      const cur = agg.get(key) ?? { date: new Date(d.anio, d.mes - 1, 1), total_escuchas: 0, minutos_totales: 0 };
      cur.total_escuchas += Number(d.total_escuchas) || 0;
      cur.minutos_totales += Number(d.minutos_totales) || 0;
      agg.set(key, cur);
    });
    const points = [...agg.values()].sort((a, b) => a.date - b.date);

    const draw = (width) => {
      const height = 260;
      const margin = { top: 10, right: 12, bottom: 28, left: 48 };
      const w = Math.max(200, width - margin.left - margin.right);
      const h = height - margin.top - margin.bottom;
      svg.attr('width', width).attr('height', height);
      const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

      const x = d3.scaleTime().domain(d3.extent(points, (d) => d.date)).range([0, w]);
      const y = d3.scaleLinear().domain([0, d3.max(points, (d) => d[metric]) || 1]).nice().range([h, 0]);

      g.append('g').attr('transform', `translate(0,${h})`).call(d3.axisBottom(x).tickFormat(d3.timeFormat('%b-%y')));
      g.append('g').call(d3.axisLeft(y).ticks(5));

      const area = d3.area().x((d) => x(d.date)).y0(h).y1((d) => y(d[metric])).curve(d3.curveMonotoneX);
      const line = d3.line().x((d) => x(d.date)).y((d) => y(d[metric])).curve(d3.curveMonotoneX);

      g.append('path').datum(points).attr('fill', theme.accentPrimary).attr('opacity', 0.18).attr('d', area);
      g.append('path').datum(points).attr('fill', 'none').attr('stroke', theme.accentPrimary).attr('stroke-width', 2).attr('d', line);

      const tip = d3.select(tipRef.current);
      g.selectAll('circle')
        .data(points)
        .join('circle')
        .attr('cx', (d) => x(d.date))
        .attr('cy', (d) => y(d[metric]))
        .attr('r', 3)
        .attr('fill', theme.accentPrimary)
        .on('mousemove', (e, d) => {
          tip.style('display', 'block').style('left', `${e.offsetX + 10}px`).style('top', `${e.offsetY}px`)
            .text(`${d3.timeFormat('%Y-%m')(d.date)}: ${d.total_escuchas} escuchas, ${d.minutos_totales.toFixed(1)} min`);
        })
        .on('mouseleave', () => tip.style('display', 'none'));
    };

    const width = wrapRef.current?.clientWidth || 600;
    draw(width);
    const ro = new ResizeObserver((entries) => {
      const w = entries[0]?.contentRect.width;
      if (w) { svg.selectAll('*').remove(); draw(w); }
    });
    if (wrapRef.current) ro.observe(wrapRef.current);

    return () => { ro.disconnect(); svg.selectAll('*').remove(); };
  }, [data, metric, theme]);

  return (
    <div className={styles.card}>
      <div className={styles.head}>
        <h2>Evolución mensual</h2>
        <select value={metric} onChange={(e) => setMetric(e.target.value)} aria-label="Métrica">
          <option value="total_escuchas">Escuchas</option>
          <option value="minutos_totales">Minutos</option>
        </select>
      </div>
      <div ref={wrapRef} className={styles.wrap}>
        {loading ? <span>Cargando…</span> : !data.length ? <span>Sin datos para filtros actuales.</span> : null}
        <svg ref={svgRef} role="img" aria-label="Serie temporal mensual" />
        <div ref={tipRef} className={styles.tooltip} />
      </div>
    </div>
  );
}
